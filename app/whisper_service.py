import torch
import librosa
import logging
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from peft import PeftModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache
_model_cache = None
_is_warmed_up = False

def get_model_components():
    """
    Loads the Processor and Model manually.
    """
    global _model_cache
    if _model_cache is None:
        logger.info("⬇️ Loading Whisper Model & Processor (Manual Mode)...")
        
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        try:
            model_id = "alihassanshahid/whisper_everyayah"
            base_model_id = "openai/whisper-small"
            
            # 1. Load Processor
            processor = AutoProcessor.from_pretrained(model_id)
            
            # 2. Load Base Model
            logger.info(f"⬇️ Loading Base Model: {base_model_id}")
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                base_model_id, 
                torch_dtype=torch_dtype, 
                low_cpu_mem_usage=True, 
                use_safetensors=True
            )
            
            # 3. Load and Merge PEFT Adapter
            logger.info(f"⬇️ Loading and Merging Adapter: {model_id}")
            model = PeftModel.from_pretrained(model, model_id)
            model = model.merge_and_unload()
            
            model.to(device)
            
            # Get the actual dtype after loading
            torch_dtype = model.dtype
            
            logger.info(f"🚀 Model loaded and merged on {device} ({torch_dtype})")
            _model_cache = (processor, model, device, torch_dtype)
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise e

    return _model_cache

def warmup_inference():
    """
    Runs inference on REAL asset files to ensure the model is fully hot.
    Only runs ONCE per server lifetime.
    """
    global _is_warmed_up
    
    if _is_warmed_up:
        logger.info("🔥 Model already warmed up. Skipping active transcription.")
        return

    logger.info("🔥 Starting Audio-Based Warmup...")
    
    # Files to warmup with
    asset_files = ["assets/001001.mp3", "assets/001002.mp3"]
    
    processor, model, device, torch_dtype = get_model_components()
    
    for file_name in asset_files:
        try:
            file_path = os.path.abspath(file_name)
            
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ Warmup file not found: {file_path}")
                continue

            logger.info(f"🎤 Warmup Transcribing: {file_name}")
            
            # 1. Load Audio
            audio_array, _ = librosa.load(file_path, sr=16000)
            
            # 2. Process
            inputs = processor(
                audio_array, 
                sampling_rate=16000, 
                return_tensors="pt"
            )
            
            # Move to device
            input_features = inputs.input_features.to(device).type(torch_dtype)
            
            # 3. Generate
            forced_decoder_ids = processor.get_decoder_prompt_ids(language="arabic", task="transcribe")
            
            generated_ids = model.generate(
                input_features,
                forced_decoder_ids=forced_decoder_ids,
                max_new_tokens=128
            )
            
            logger.info(f"✅ Warmup Finished for {file_name}")

        except Exception as e:
            import traceback
            logger.error(f"❌ Warmup Failed for {file_name}: {e}")
            logger.error(traceback.format_exc())
    
    logger.info("🔥 All Warmup Tasks Complete")
    _is_warmed_up = True

def transcribe_audio_local(file_path: str) -> str:
    try:
        logger.info(f"🎤 Processing audio: {file_path}")
        
        processor, model, device, torch_dtype = get_model_components()
        
        # 1. Load Audio
        audio_array, _ = librosa.load(file_path, sr=16000)
        
        # 2. Process
        inputs = processor(
            audio_array, 
            sampling_rate=16000, 
            return_tensors="pt"
        )
        
        input_features = inputs.input_features.to(device).type(torch_dtype)
        
        # 3. Generate
        forced_decoder_ids = processor.get_decoder_prompt_ids(language="arabic", task="transcribe")
        
        generated_ids = model.generate(
            input_features,
            forced_decoder_ids=forced_decoder_ids,
            max_new_tokens=256
        )
        
        # 4. Decode
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        transcription = transcription.strip()
        logger.info(f"✅ Transcription Success: {transcription}")
        return transcription

    except Exception as e:
        import traceback
        logger.error(f"❌ Transcription Error: {e}")
        logger.error(traceback.format_exc())
        return ""
