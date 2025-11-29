# from transformers import pipeline
# import torch
# import tempfile

# # Load Whisper Tiny pipeline once
# pipe = pipeline("automatic-speech-recognition", model="openai/whisper-base")

# def transcribe_audio_local(audio_bytes: bytes) -> str:
#     """
#     Transcribe audio bytes using Whisper Tiny pipeline
#     """
#     # Save bytes to a temporary file
#     with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
#         tmp.write(audio_bytes)
#         tmp.flush()
#         # Transcribe with pipeline
#         result = pipe(tmp.name)
#         return result["text"]

import logging
from transformers import pipeline
import torch

# Setup logging
logger = logging.getLogger(__name__)

# Global variable to hold the model in memory
_speech_recognizer = None

def get_model():
    """
    Singleton pattern to load the model only once.
    """
    global _speech_recognizer
    if _speech_recognizer is None:
        logger.info("⏳ Loading Whisper model... (This might take a moment on first run)")
        
        # Use "openai/whisper-tiny" for speed on CPU, or "openai/whisper-base" for better accuracy
        # device=0 uses GPU if available, otherwise CPU
        device = 0 if torch.cuda.is_available() else -1
        
        _speech_recognizer = pipeline(
            "automatic-speech-recognition", 
            model="openai/whisper-base", 
            device=device
        )
        logger.info("✅ Whisper model loaded successfully.")
    
    return _speech_recognizer

def transcribe_audio_local(file_path: str) -> str:
    """
    Transcribe audio file from a specific path using local Whisper model.
    """
    try:
        pipe = get_model()
        
        # The pipeline handles loading the audio file directly from path
        result = pipe(
            file_path,
            return_timestamps=True,
            generate_kwargs={
                "language": "arabic", 
                "task": "transcribe"
            }
            )
        
        text = result.get("text", "")
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise e