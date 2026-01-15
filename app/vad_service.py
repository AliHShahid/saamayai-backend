# # import logging
# # import torch
# # import torchaudio

# # logger = logging.getLogger(__name__)

# # # Global VAD model
# # _vad_model = None
# # _utils = None

# # def get_vad_model():
# #     """
# #     Load Silero VAD model (Singleton).
# #     """
# #     global _vad_model, _utils
# #     if _vad_model is None:
# #         logger.info("⏳ Loading Silero VAD model...")
# #         try:
# #             # Load directly from torch hub (downloads automatically on first run)
# #             _vad_model, _utils = torch.hub.load(
# #                 repo_or_dir='snakers4/silero-vad',
# #                 model='silero_vad',
# #                 force_reload=False,
# #                 trust_repo=True
# #             )
# #             logger.info("✅ VAD model loaded.")
# #         except Exception as e:
# #             logger.error(f"❌ Failed to load VAD model: {e}")
# #             raise e
# #     return _vad_model, _utils

# # def is_speech(audio_path: str, threshold: float = 0.5) -> bool:
# #     """
# #     Check if the audio file contains speech.
# #     """
# #     try:
# #         model, utils = get_vad_model()
# #         (get_speech_timestamps, _, read_audio, *_) = utils
        
# #         # Read audio file
# #         wav = read_audio(audio_path)
        
# #         # Get speech timestamps
# #         speech_timestamps = get_speech_timestamps(wav, model, threshold=threshold)
        
# #         # If list is not empty, speech was detected
# #         return len(speech_timestamps) > 0
        
# #     except Exception as e:
# #         logger.error(f"VAD Error: {e}")
# #         # Fail-safe: If VAD fails, assume speech so we don't miss anything
# #         return True

# import logging
# import webrtcvad

# logger = logging.getLogger(__name__)

# # VAD Aggressiveness (0–3)
# _vad = webrtcvad.Vad(2)

# def is_speech(pcm_data: bytes, sample_rate: int = 16000) -> bool:
#     """
#     Detect speech inside raw 16-bit mono PCM audio.
#     WebRTC VAD requires 10 / 20 / 30 ms frames.
#     """

#     try:
#         frame_duration_ms = 20
#         bytes_per_sample = 2  # 16-bit mono
#         frame_size = int(sample_rate * frame_duration_ms / 1000) * bytes_per_sample  # 640 bytes

#         if len(pcm_data) < frame_size:
#             # Not enough data → treat as silence to avoid false positives
#             return False

#         speech_frames = 0
#         total_frames = 0

#         # Iterate through 20ms chunks
#         for i in range(0, len(pcm_data) - frame_size + 1, frame_size):
#             chunk = pcm_data[i:i + frame_size]

#             total_frames += 1
#             if _vad.is_speech(chunk, sample_rate):
#                 speech_frames += 1

#         # More than 30% speech = classify as speech
#         return (speech_frames / total_frames) > 0.30 if total_frames else False

#     except Exception as e:
#         logger.error(f"VAD Error: {e}")
#         # Fail safe: allow transcription instead of blocking audio
#         return True
