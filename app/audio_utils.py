import logging
import os
from pydub import AudioSegment
from pydub.effects import normalize

logger = logging.getLogger(__name__)

def process_audio_for_speech(file_path: str) -> str:
    """
    Cleans audio for better speech recognition:
    1. Resamples to 16kHz (Whisper's native rate)
    2. Converts to Mono
    3. Filters out low-frequency noise (rumble/wind)
    4. Normalizes volume
    """
    try:
        logger.info(f"🧹 Cleaning audio: {file_path}")
        
        # 1. Load Audio
        audio = AudioSegment.from_file(file_path)
        
        # 2. Convert to Mono & 16kHz (Standardize)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        # 3. Noise Handling: High Pass Filter (cuts frequencies < 200Hz)
        # This removes wind, mic handling noise, and AC hum without hurting speech.
        audio = audio.high_pass_filter(200)
        
        # 4. Normalize Volume (Boosts quiet recordings)
        # Target -20dBFS is standard for speech processing
        audio = normalize(audio, headroom=2.0) 

        # 5. Export processed file
        base_name, _ = os.path.splitext(file_path)
        clean_file_path = f"{base_name}_clean.wav"
        
        audio.export(clean_file_path, format="wav")
        
        logger.info(f"✨ Audio cleaned and saved to: {clean_file_path}")
        return clean_file_path

    except Exception as e:
        logger.error(f"⚠️ Audio processing failed: {e}")
        # If cleaning fails, return original file so app doesn't crash
        return file_path