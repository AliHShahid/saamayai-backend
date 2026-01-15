# # # # # # # # # # from fastapi import FastAPI, File, UploadFile, HTTPException
# # # # # # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # # # # # from app.whisper_service import transcribe_audio_local

# # # # # # # # # # app = FastAPI(title="SaamayAI Backend", debug=True)

# # # # # # # # # # # Enable CORS so Flutter can access
# # # # # # # # # # app.add_middleware(
# # # # # # # # # #     CORSMiddleware,
# # # # # # # # # #     allow_origins=["*"],  # allow all origins
# # # # # # # # # #     allow_credentials=True,
# # # # # # # # # #     allow_methods=["*"],
# # # # # # # # # #     allow_headers=["*"],
# # # # # # # # # # )

# # # # # # # # # # # Root endpoint
# # # # # # # # # # @app.get("/")
# # # # # # # # # # def read_root():
# # # # # # # # # #     return {"message": "SaamayAI FastAPI running successfully!"}

# # # # # # # # # # # # Transcribe local audio
# # # # # # # # # # # @app.post("/transcribe")
# # # # # # # # # # # async def transcribe(file: UploadFile = File(...)):
# # # # # # # # # # #     if file.content_type not in ["audio/wav", "audio/mpeg", "audio/mp3"]:
# # # # # # # # # # #         raise HTTPException(status_code=400, detail="Invalid audio format")
    
# # # # # # # # # # #     try:
# # # # # # # # # # #         # Read file content
# # # # # # # # # # #         audio_bytes = await file.read()
# # # # # # # # # # #         transcription = transcribe_audio_local(audio_bytes)
# # # # # # # # # # #         return {"source": "local", "transcription": transcription}
# # # # # # # # # # #     except Exception as e:
# # # # # # # # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # # # # # # @app.post("/transcribe")
# # # # # # # # # # async def transcribe(file: UploadFile = File(...)):
# # # # # # # # # #     allowed_types = [
# # # # # # # # # #         "audio/wav", "audio/x-wav",
# # # # # # # # # #         "audio/mpeg", "audio/mp3",
# # # # # # # # # #         "audio/mp4", "audio/aac",
# # # # # # # # # #         "audio/ogg", "audio/webm",
# # # # # # # # # #         "audio/m4a"
# # # # # # # # # #     ]
# # # # # # # # # #     print("📥 File received:", file.filename, file.content_type)

# # # # # # # # # #     if file.content_type not in allowed_types:
# # # # # # # # # #         print("❌ Invalid format:", file.content_type)
# # # # # # # # # #         raise HTTPException(status_code=400, detail=f"Invalid audio format: {file.content_type}")

# # # # # # # # # #     try:
# # # # # # # # # #         audio_bytes = await file.read()
# # # # # # # # # #         print("🎧 Bytes length:", len(audio_bytes))
# # # # # # # # # #         transcription = transcribe_audio_local(audio_bytes)
# # # # # # # # # #         print("📝 Transcription output:", transcription)
# # # # # # # # # #         return {"transcription": transcription}
# # # # # # # # # #     except Exception as e:
# # # # # # # # # #         print("🔥 ERROR in /transcribe:", e)
# # # # # # # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # # # # # import logging
# # # # # # # # # import os
# # # # # # # # # import shutil
# # # # # # # # # from fastapi import FastAPI, UploadFile, File, HTTPException

# # # # # # # # # # Import your new service
# # # # # # # # # from app.whisper_service import transcribe_audio_local

# # # # # # # # # # 1. Setup Logging
# # # # # # # # # logging.basicConfig(level=logging.INFO)
# # # # # # # # # logger = logging.getLogger(__name__)

# # # # # # # # # app = FastAPI()

# # # # # # # # # @app.get("/")
# # # # # # # # # def home():
# # # # # # # # #     return {"message": "Saamay Backend is Running!"}

# # # # # # # # # @app.post("/transcribe")
# # # # # # # # # async def transcribe(file: UploadFile = File(...)):
# # # # # # # # #     try:
# # # # # # # # #         logger.info(f"Received file: {file.filename}")

# # # # # # # # #         # 2. Ensure temp directory exists
# # # # # # # # #         if not os.path.exists("temp"):
# # # # # # # # #             os.makedirs("temp")

# # # # # # # # #         # 3. Save the file temporarily
# # # # # # # # #         temp_file_path = f"temp/{file.filename}"
# # # # # # # # #         with open(temp_file_path, "wb") as buffer:
# # # # # # # # #             shutil.copyfileobj(file.file, buffer)
            
# # # # # # # # #         logger.info(f"File saved to {temp_file_path}. Starting transcription...")

# # # # # # # # #         # 4. CALL THE SERVICE
# # # # # # # # #         # Pass the file path directly to your Hugging Face pipeline
# # # # # # # # #         transcription_text = transcribe_audio_local(temp_file_path)
        
# # # # # # # # #         logger.info(f"Transcription complete: {transcription_text[:50]}...")

# # # # # # # # #         # 5. Clean up (Optional: delete file after processing)
# # # # # # # # #         # os.remove(temp_file_path)

# # # # # # # # #         # 6. Return result to Flutter
# # # # # # # # #         return {
# # # # # # # # #             "filename": file.filename, 
# # # # # # # # #             "transcription": transcription_text
# # # # # # # # #         }

# # # # # # # # #     except Exception as e:
# # # # # # # # #         logger.error(f"CRASH: {str(e)}")
# # # # # # # # #         raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")

# # # # # # # # # ### 3. Dependencies
# # # # # # # # # # Make sure you have the required libraries installed in your Python environment:

# # # # # # # # # # ```bash
# # # # # # # # # # pip install torch transformers torchaudio librosa soundfile

# # # # # # # # import logging
# # # # # # # # import os
# # # # # # # # import shutil
# # # # # # # # from fastapi import FastAPI, UploadFile, File, HTTPException

# # # # # # # # # Import your new service
# # # # # # # # from app.whisper_service import transcribe_audio_local

# # # # # # # # # 1. Setup Logging
# # # # # # # # logging.basicConfig(level=logging.INFO)
# # # # # # # # logger = logging.getLogger(__name__)

# # # # # # # # app = FastAPI()

# # # # # # # # @app.get("/")
# # # # # # # # def home():
# # # # # # # #     return {"message": "Saamay Backend is Running (Arabic Mode)!"}

# # # # # # # # @app.post("/transcribe")
# # # # # # # # async def transcribe(file: UploadFile = File(...)):
# # # # # # # #     temp_file_path = ""
# # # # # # # #     try:
# # # # # # # #         logger.info(f"Received file: {file.filename}")

# # # # # # # #         # 2. Ensure temp directory exists
# # # # # # # #         if not os.path.exists("temp"):
# # # # # # # #             os.makedirs("temp")

# # # # # # # #         # 3. Create temp path
# # # # # # # #         temp_file_path = f"temp/{file.filename}"
        
# # # # # # # #         # ⚠️ CRITICAL: Read file in chunks to prevent 'Broken Pipe' or Memory errors
# # # # # # # #         with open(temp_file_path, "wb") as buffer:
# # # # # # # #             while content := await file.read(1024 * 1024):  # Read 1MB chunks
# # # # # # # #                 buffer.write(content)
            
# # # # # # # #         logger.info(f"File saved to {temp_file_path}. Size: {os.path.getsize(temp_file_path)} bytes. Starting transcription...")

# # # # # # # #         # 4. CALL THE SERVICE
# # # # # # # #         # Pass the file path directly to your Hugging Face pipeline
# # # # # # # #         transcription_text = transcribe_audio_local(temp_file_path)
        
# # # # # # # #         logger.info(f"Transcription complete: {transcription_text[:50]}...")

# # # # # # # #         # 5. Return result to Flutter
# # # # # # # #         return {
# # # # # # # #             "filename": file.filename, 
# # # # # # # #             "transcription": transcription_text
# # # # # # # #         }

# # # # # # # #     except Exception as e:
# # # # # # # #         logger.error(f"CRASH: {str(e)}")
# # # # # # # #         # Raise valid HTTP error so client knows what happened
# # # # # # # #         raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")
        
# # # # # # # #     finally:
# # # # # # # #         # 6. Cleanup: Ensure file handle is closed
# # # # # # # #         await file.close()
        
# # # # # # # #         # Optional: Delete file after processing to save space
# # # # # # # #         # if os.path.exists(temp_file_path):
# # # # # # # #         #     os.remove(temp_file_path)

# # V1
# import logging
# import os
# import shutil
# from fastapi import FastAPI, UploadFile, File, HTTPException

# # Import your services
# from app.whisper_service import transcribe_audio_local
# from app.audio_utils import process_audio_for_speech  # 👈 Import the cleaner

# # Setup Logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "Saamay Backend is Running (Arabic Mode + Audio Cleaning)!"}

# @app.post("/transcribe")
# async def transcribe(file: UploadFile = File(...)):
#     temp_file_path = ""
#     processed_file_path = ""
    
#     try:
#         logger.info(f"Received file: {file.filename}")

#         if not os.path.exists("temp"):
#             os.makedirs("temp")

#         temp_file_path = f"temp/{file.filename}"
        
#         # 1. Save Original File
#         with open(temp_file_path, "wb") as buffer:
#             while content := await file.read(1024 * 1024): 
#                 buffer.write(content)
            
#         logger.info(f"Original saved. Size: {os.path.getsize(temp_file_path)} bytes.")

#         # 2. ✨ CLEAN & PROCESS AUDIO ✨
#         # This creates a new "_clean.wav" file optimized for Whisper
#         processed_file_path = process_audio_for_speech(temp_file_path)

#         # 3. Transcribe the CLEANED file
#         transcription_text = transcribe_audio_local(processed_file_path)
        
#         logger.info(f"Transcription complete: {transcription_text[:50]}...")

#         return {
#             "filename": file.filename, 
#             "transcription": transcription_text
#         }

#     except Exception as e:
#         logger.error(f"CRASH: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")
        
#     finally:
#         await file.close()
        
#         # Cleanup: Delete both original and processed files to save space
#         if os.path.exists(temp_file_path):
#             os.remove(temp_file_path)
#         if os.path.exists(processed_file_path) and processed_file_path != temp_file_path:
#             os.remove(processed_file_path)
            
# # # # V2
# # import logging
# # import os
# # import shutil
# # import asyncio
# # from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
# # from app.whisper_service import transcribe_audio_local
# # from app.audio_utils import process_audio_for_speech

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # app = FastAPI()

# # @app.get("/")
# # def home():
# #     return {"message": "Saamay Backend is Running (WebSocket Enabled)!"}

# # # --- HTTP ENDPOINT (Keep this for backup/compatibility) ---
# # @app.post("/transcribe")
# # async def transcribe(file: UploadFile = File(...)):
# #     # ... (Keep your existing HTTP logic here as a fallback) ...
# #     pass 

# # # --- WEBSOCKET ENDPOINT (New Live Logic) ---
# # @app.websocket("/ws/transcribe")
# # async def websocket_endpoint(websocket: WebSocket):
# #     await websocket.accept()
# #     logger.info("🔌 WebSocket connected")
    
# #     # We will buffer received audio bytes here
# #     temp_filename = f"temp/live_{os.getpid()}.wav"
    
# #     try:
# #         # Create/Clear the file
# #         with open(temp_filename, "wb") as f:
# #             pass

# #         while True:
# #             # 1. Receive audio chunk from Flutter
# #             data = await websocket.receive_bytes()
            
# #             # 2. Append chunk to our temp file
# #             # In a real production app, you would use a ring buffer or VAD 
# #             # to avoid the file growing infinitely.
# #             with open(temp_filename, "ab") as f:
# #                 f.write(data)
            
# #             # 3. Transcribe occasionally (Simulating real-time)
# #             # Running Whisper on EVERY chunk is too slow. 
# #             # We assume the client sends data frequently, so we transcribe the growing file.
            
# #             # (Optional: Only transcribe if file size > X bytes to save CPU)
# #             if os.path.getsize(temp_filename) > 10000: # Example threshold
# #                  # Copy to a read-safe file so we don't lock the write stream
# #                 read_safe_path = temp_filename + "_read.wav"
# #                 shutil.copy(temp_filename, read_safe_path)
                
# #                 # Run transcription
# #                 text = transcribe_audio_local(read_safe_path)
                
# #                 # Send text back to Flutter
# #                 await websocket.send_text(text)

# #     except WebSocketDisconnect:
# #         logger.info("🔌 WebSocket disconnected")
# #     except Exception as e:
# #         logger.error(f"WebSocket Error: {e}")
# #     finally:
# #         if os.path.exists(temp_filename):
# #             os.remove(temp_filename)

# # # V3
# # import logging
# # import os
# # import shutil
# # from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
# # from app.whisper_service import transcribe_audio_local
# # from app.vad_service import is_speech
# # from pydub import AudioSegment

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # app = FastAPI()


# # @app.get("/")
# # def home():
# #     return {"message": "Saamay Backend Running (WebRTC VAD)"}


# # @app.post("/transcribe")
# # async def transcribe(file: UploadFile = File(...)):
# #     temp_path = f"temp/{file.filename}"
# #     try:
# #         if not os.path.exists("temp"):
# #             os.makedirs("temp")

# #         with open(temp_path, "wb") as f:
# #             while chunk := await file.read(1024 * 1024):
# #                 f.write(chunk)

# #         text = transcribe_audio_local(temp_path)
# #         return {"transcription": text}

# #     except Exception as e:
# #         raise HTTPException(500, detail=str(e))

# #     finally:
# #         await file.close()


# # @app.websocket("/ws/transcribe")
# # async def websocket_endpoint(websocket: WebSocket):
# #     await websocket.accept()
# #     logger.info("🔌 WebSocket connected")

# #     raw_filename = f"temp/live_{os.getpid()}.raw"
# #     wav_filename = f"temp/live_{os.getpid()}.wav"

# #     try:
# #         # Clear file
# #         with open(raw_filename, "wb"):
# #             pass

# #         while True:
# #             # 1. Receive Raw Bytes
# #             data = await websocket.receive_bytes()

# #             # 2. VAD Check
# #             if is_speech(data):
# #                 with open(raw_filename, "ab") as f:
# #                     f.write(data)
# #             else:
# #                 pass  # Skip silence

# #             # 3. Transcribe Buffer (~1 sec)
# #             if os.path.getsize(raw_filename) > 32000:

# #                 audio = AudioSegment.from_raw(
# #                     raw_filename,
# #                     sample_width=2,
# #                     frame_rate=16000,
# #                     channels=1,
# #                 )
# #                 audio.export(wav_filename, format="wav")

# #                 text = transcribe_audio_local(wav_filename)
# #                 if text and text.strip():
# #                     await websocket.send_text(text)

# #                 # Reset buffer
# #                 with open(raw_filename, "wb"):
# #                     pass

# #     except WebSocketDisconnect:
# #         logger.info("🔌 WebSocket disconnected")

# #     except Exception as e:
# #         logger.error(f"WebSocket Error: {e}")

# #     finally:
# #         if os.path.exists(raw_filename):
# #             os.remove(raw_filename)
# #         if os.path.exists(wav_filename):
# #             os.remove(wav_filename)

import logging
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException

# Import Services
from app.whisper_service import transcribe_audio_local
from app.mistake_service import mistake_service

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Saamay Backend is Running (Mistake Detection Enabled)"}

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    surah_number: int = Form(None) # Optional: if provided, we compare
):
    temp_file_path = ""
    try:
        logger.info(f"Received file: {file.filename}. Surah: {surah_number}")

        # 1. Prepare temp directory
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        temp_file_path = f"temp/{file.filename}"
        
        # 2. Save file safely
        with open(temp_file_path, "wb") as buffer:
            while content := await file.read(1024 * 1024): 
                buffer.write(content)
            
        # 3. Transcribe
        transcription_text = transcribe_audio_local(temp_file_path)
        
        # 4. Mistake Detection (If Surah ID provided)
        result = {
            "filename": file.filename, 
            "transcription": transcription_text
        }
        
        if surah_number:
            analysis = mistake_service.detect_mistakes(transcription_text, surah_number)
            result["analysis"] = analysis
            logger.info(f"Mistake Analysis Accuracy: {analysis['accuracy']}%")

        return result

    except Exception as e:
        logger.error(f"CRASH: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")
        
    finally:
        await file.close()
        # Optional cleanup
        # if os.path.exists(temp_file_path):
        #     os.remove(temp_file_path)