import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.whisper_service import WhisperService

app = FastAPI(title="SaamayAI Backend")

# CORS for Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For Flutter mobile allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


@app.get("/")
async def home():
    return {"message": "SaamayAI FastAPI running successfully!"}


# ----------------------------------------------------------
# 🔹 1 - Hugging Face Whisper API Route
# ----------------------------------------------------------
@app.post("/transcribe/hf")
async def transcribe_hf(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    text = WhisperService.transcribe_hf(audio_bytes)
    return {"source": "huggingface", "transcription": text}


# ----------------------------------------------------------
# 🔹 2 - Local Whisper Model Route
# ----------------------------------------------------------
@app.post("/transcribe/local")
async def transcribe_local(file: UploadFile = File(...)):
    file_path = f"{TEMP_DIR}/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = WhisperService.transcribe_local(file_path)

    os.remove(file_path)  # clean temp file

    return {"source": "local", "transcription": text}
