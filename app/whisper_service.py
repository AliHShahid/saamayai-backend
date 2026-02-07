import torch
import librosa
import logging
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache
_model_cache = None

def get_model_components():
    """
    Loads the Processor and Model manually.
    This bypasses the 'pipeline' abstraction to avoid ffmpeg/metadata errors.
    """
    global _model_cache
    if _model_cache is None:
        logger.info("⬇️ Loading Whisper Model & Processor (Manual Mode)...")
        
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        try:
            # 1. Load Processor (Handles audio -> numbers)
            processor = WhisperProcessor.from_pretrained("openai/whisper-small")
            
            # 2. Load Model (Handles numbers -> text)
            model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
            model.to(device)
            
            # Optimization for GPU
            if device == "cuda:0":
                model = model.half() # Convert to FP16 for speed
                
            logger.info(f"🚀 Model loaded on {device} ({torch_dtype})")
            _model_cache = (processor, model, device, torch_dtype)
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise e

    return _model_cache

def transcribe_audio_local(file_path: str) -> str:
    try:
        logger.info(f"🎤 Processing audio: {file_path}")
        
        processor, model, device, torch_dtype = get_model_components()
        
        # 1. Load Audio with Librosa (Forces 16kHz)
        # This returns a simple numpy array of numbers
        audio_array, _ = librosa.load(file_path, sr=16000)
        
        # 2. Process Audio (Convert array to Tensor)
        input_features = processor(
            audio_array, 
            sampling_rate=16000, 
            return_tensors="pt"
        ).input_features
        
        # Move inputs to the correct device/datatype
        input_features = input_features.to(device)
        if device == "cuda:0":
            input_features = input_features.half()

        # 3. Generate Tokens (Force Arabic)
        # We manually tell the model to use Arabic logic
        forced_decoder_ids = processor.get_decoder_prompt_ids(language="arabic", task="transcribe")
        
        predicted_ids = model.generate(
            input_features, 
            forced_decoder_ids=forced_decoder_ids,
            max_new_tokens=256
        )
        
        # 4. Decode Tokens to Text
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        transcription = transcription.strip()
        logger.info(f"✅ Transcription Success: {transcription}")
        return transcription

    except Exception as e:
        logger.error(f"❌ Manual Transcription Error: {e}")
        return ""