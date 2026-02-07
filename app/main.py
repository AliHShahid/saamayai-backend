from fastapi import FastAPI, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import tempfile
import wave
from pydub import AudioSegment
from app.whisper_service import transcribe_audio_local
from app.mistake_service import mistake_service

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for Flutter access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Saamay Backend Running (v1.1-warmup)"}

@app.get("/warmup")
def warmup():
    """Triggers model loading so the first transcription is fast."""
    try:
        from app.whisper_service import get_model_components
        get_model_components()
        return {"status": "success", "message": "Model warmed up"}
    except Exception as e:
        logger.error(f"Warmup Error: {e}")
        return {"status": "error", "message": str(e)}

def is_silence(file_path: str, threshold_db: float = -40.0) -> bool:
    """Checks if the audio file is silent (background noise only)."""
    try:
        audio = AudioSegment.from_file(file_path)
        if audio.dBFS < threshold_db:
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking silence: {e}")
        return False

def is_audio_silent(audio_bytes: bytes, threshold_db: float = -45.0) -> bool:
    """Checks if raw PCM bytes are silent."""
    try:
        if not audio_bytes: return True
        audio = AudioSegment(
            data=audio_bytes,
            sample_width=2,
            frame_rate=16000,
            channels=1
        )
        return audio.dBFS < threshold_db
    except Exception:
        return False

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    surah_number: int = Form(...),
    ayah_number: int = Form(...)
):
    # Create temp file robustly
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        temp_file_path = tmp.name

    try:
        # 1. Save File
        with open(temp_file_path, "wb") as buffer:
            while content := await file.read(1024 * 1024): 
                buffer.write(content)

        # 2. 🔇 SILENCE GATE
        if is_silence(temp_file_path):
            logger.info("🤫 Silence detected. Skipping transcription.")
            return {
                "transcription": "", 
                "analysis": None,
                "status": "silence"
            }

        # 3. Transcribe
        transcription_text = transcribe_audio_local(temp_file_path)
        logger.info(f"🗣️ Transcribed: {transcription_text}")
        
        # 4. Analyze
        analysis = mistake_service.detect_mistakes(transcription_text, surah_number, ayah_number)
        
        return {
            "analysis": analysis, 
            "transcription": transcription_text,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"CRASH: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
        
    finally:
        await file.close()
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.websocket("/ws/transcribe/{surah_number}")
async def websocket_endpoint(websocket: WebSocket, surah_number: int):
    await websocket.accept()
    logger.info(f"🔌 WS Connected. Surah: {surah_number}")
    
    audio_buffer = bytearray()
    current_ayah = 1 
    
    # Thresholds for VAD and Chunking
    CHUNK_SIZE_THRESHOLD = 150 * 1024  # ~4.8 seconds of audio
    MAX_BUFFER_SIZE = 500 * 1024       # Force process if it hits ~16 seconds
    SILENCE_TOLERANCE_MS = 400         # Look for 400ms of silence at the end
    OVERLAP_BYTES = 16000              # 500ms overlap if forced to split
    
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)
            
            should_transcribe = False
            is_forced = False
            
            if len(audio_buffer) > CHUNK_SIZE_THRESHOLD:
                silence_check_bytes = int(16000 * 2 * (SILENCE_TOLERANCE_MS / 1000))
                tail = audio_buffer[-silence_check_bytes:]
                
                if is_audio_silent(tail, threshold_db=-45.0):
                    logger.info(f"✨ Silenced detected at end of {len(audio_buffer)} bytes. Transcribing...")
                    should_transcribe = True
                elif len(audio_buffer) > MAX_BUFFER_SIZE:
                    logger.info("⚠️ Buffer limit reached. Forcing transcription.")
                    should_transcribe = True
                    is_forced = True
            
            if should_transcribe:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    temp_filename = tmp_file.name
                
                try:
                    with wave.open(temp_filename, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(16000)
                        wf.writeframes(audio_buffer)
                    
                    transcript = transcribe_audio_local(temp_filename)
                    
                    if transcript.strip():
                        analysis = mistake_service.detect_mistakes_continuous(
                            transcript, surah_number, start_ayah_hint=current_ayah
                        )
                        
                        if analysis and "ayah" in analysis:
                            current_ayah = analysis["ayah"]
                        
                        await websocket.send_json({
                            "transcription": transcript,
                            "analysis": analysis,
                            "is_final": not is_forced
                        })
                        
                        if is_forced:
                            audio_buffer = audio_buffer[-OVERLAP_BYTES:]
                        else:
                            audio_buffer = audio_buffer[-3200:]
                    else:
                        audio_buffer = audio_buffer[-8000:]
                
                finally:
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)

    except WebSocketDisconnect:
        logger.info("🔌 WS Disconnected")
    except Exception as e:
        logger.error(f"WS Error: {e}")
