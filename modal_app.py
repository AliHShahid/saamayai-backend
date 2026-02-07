import modal
import os
import sys

# 1. Define the build step
def download_model():
    from transformers import pipeline
    print("⬇️ Downloading Whisper Small model...")
    pipeline("automatic-speech-recognition", model="openai/whisper-small")

# 2. Define the Image (Attach files HERE now)
# 2. Define the Image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "fastapi",
        "uvicorn",
        "transformers",
        "torch",
        "torchaudio",
        "python-multipart",
        "huggingface-hub",
        "librosa",
        "soundfile",
        "pydub",
        "numpy",
        "accelerate"
    )
    .env({"HF_HOME": "/root/.cache/huggingface"})
    .run_function(download_model)
    # MODAL 1.0: add_local_dir mounts files at runtime by default (hot-sync)
    .add_local_dir("app", remote_path="/root/app")
    .add_local_dir("assets", remote_path="/root/assets")
    .add_local_dir("temp", remote_path="/root/temp")
)

app = modal.App("saamay-backend")

# 3. Define the FastAPI App
@app.function(
    image=image,
    gpu="T4",
    timeout=600,
    scaledown_window=60, # Renamed from container_idle_timeout in Modal 1.0
)
@modal.asgi_app()
def fastapi_app():
    # Verification print
    print("🚀 Saamay Backend: Version 1.0 SDK Syncing Active")
    from app.main import app as my_app
    return my_app