from transformers import pipeline
import torch
import tempfile

# Load Whisper Tiny pipeline once
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-base")

def transcribe_audio_local(audio_bytes: bytes) -> str:
    """
    Transcribe audio bytes using Whisper Tiny pipeline
    """
    # Save bytes to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        # Transcribe with pipeline
        result = pipe(tmp.name)
        return result["text"]
