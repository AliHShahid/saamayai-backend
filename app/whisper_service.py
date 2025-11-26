import requests
import whisper
import os
from app.config import HF_API_URL, HF_API_KEY

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Load local whisper model once at startup
local_model = whisper.load_model("tiny")


class WhisperService:

    @staticmethod
    def transcribe_hf(audio_bytes: bytes):
        """Transcribe using Hugging Face Whisper API"""
        response = requests.post(
            HF_API_URL,
            headers=headers,
            data=audio_bytes
        )
        try:
            return response.json().get("text", "")
        except:
            return "Error: Could not parse response."

    @staticmethod
    def transcribe_local(file_path: str):
        """Transcribe using Local Whisper"""
        result = local_model.transcribe(file_path)
        return result["text"]
