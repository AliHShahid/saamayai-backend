from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.whisper_service import transcribe_audio_local

app = FastAPI(title="SaamayAI Backend")

# Enable CORS so Flutter can access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "SaamayAI FastAPI running successfully!"}

# Transcribe local audio
@app.post("/transcribe/local")
async def transcribe_local(file: UploadFile = File(...)):
    if file.content_type not in ["audio/wav", "audio/mpeg", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    try:
        # Read file content
        audio_bytes = await file.read()
        transcription = transcribe_audio_local(audio_bytes)
        return {"source": "local", "transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
