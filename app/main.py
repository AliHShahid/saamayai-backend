# # from fastapi import FastAPI, File, UploadFile, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware
# # from app.whisper_service import transcribe_audio_local

# # app = FastAPI(title="SaamayAI Backend", debug=True)

# # # Enable CORS so Flutter can access
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],  # allow all origins
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # Root endpoint
# # @app.get("/")
# # def read_root():
# #     return {"message": "SaamayAI FastAPI running successfully!"}

# # # # Transcribe local audio
# # # @app.post("/transcribe")
# # # async def transcribe(file: UploadFile = File(...)):
# # #     if file.content_type not in ["audio/wav", "audio/mpeg", "audio/mp3"]:
# # #         raise HTTPException(status_code=400, detail="Invalid audio format")
    
# # #     try:
# # #         # Read file content
# # #         audio_bytes = await file.read()
# # #         transcription = transcribe_audio_local(audio_bytes)
# # #         return {"source": "local", "transcription": transcription}
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/transcribe")
# # async def transcribe(file: UploadFile = File(...)):
# #     allowed_types = [
# #         "audio/wav", "audio/x-wav",
# #         "audio/mpeg", "audio/mp3",
# #         "audio/mp4", "audio/aac",
# #         "audio/ogg", "audio/webm",
# #         "audio/m4a"
# #     ]
# #     print("📥 File received:", file.filename, file.content_type)

# #     if file.content_type not in allowed_types:
# #         print("❌ Invalid format:", file.content_type)
# #         raise HTTPException(status_code=400, detail=f"Invalid audio format: {file.content_type}")

# #     try:
# #         audio_bytes = await file.read()
# #         print("🎧 Bytes length:", len(audio_bytes))
# #         transcription = transcribe_audio_local(audio_bytes)
# #         print("📝 Transcription output:", transcription)
# #         return {"transcription": transcription}
# #     except Exception as e:
# #         print("🔥 ERROR in /transcribe:", e)
# #         raise HTTPException(status_code=500, detail=str(e))

# import logging
# import os
# import shutil
# from fastapi import FastAPI, UploadFile, File, HTTPException

# # Import your new service
# from app.whisper_service import transcribe_audio_local

# # 1. Setup Logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "Saamay Backend is Running!"}

# @app.post("/transcribe")
# async def transcribe(file: UploadFile = File(...)):
#     try:
#         logger.info(f"Received file: {file.filename}")

#         # 2. Ensure temp directory exists
#         if not os.path.exists("temp"):
#             os.makedirs("temp")

#         # 3. Save the file temporarily
#         temp_file_path = f"temp/{file.filename}"
#         with open(temp_file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
            
#         logger.info(f"File saved to {temp_file_path}. Starting transcription...")

#         # 4. CALL THE SERVICE
#         # Pass the file path directly to your Hugging Face pipeline
#         transcription_text = transcribe_audio_local(temp_file_path)
        
#         logger.info(f"Transcription complete: {transcription_text[:50]}...")

#         # 5. Clean up (Optional: delete file after processing)
#         # os.remove(temp_file_path)

#         # 6. Return result to Flutter
#         return {
#             "filename": file.filename, 
#             "transcription": transcription_text
#         }

#     except Exception as e:
#         logger.error(f"CRASH: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")

# ### 3. Dependencies
# # Make sure you have the required libraries installed in your Python environment:

# # ```bash
# # pip install torch transformers torchaudio librosa soundfile

import logging
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException

# Import your new service
from app.whisper_service import transcribe_audio_local

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Saamay Backend is Running (Arabic Mode)!"}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    temp_file_path = ""
    try:
        logger.info(f"Received file: {file.filename}")

        # 2. Ensure temp directory exists
        if not os.path.exists("temp"):
            os.makedirs("temp")

        # 3. Create temp path
        temp_file_path = f"temp/{file.filename}"
        
        # ⚠️ CRITICAL: Read file in chunks to prevent 'Broken Pipe' or Memory errors
        with open(temp_file_path, "wb") as buffer:
            while content := await file.read(1024 * 1024):  # Read 1MB chunks
                buffer.write(content)
            
        logger.info(f"File saved to {temp_file_path}. Size: {os.path.getsize(temp_file_path)} bytes. Starting transcription...")

        # 4. CALL THE SERVICE
        # Pass the file path directly to your Hugging Face pipeline
        transcription_text = transcribe_audio_local(temp_file_path)
        
        logger.info(f"Transcription complete: {transcription_text[:50]}...")

        # 5. Return result to Flutter
        return {
            "filename": file.filename, 
            "transcription": transcription_text
        }

    except Exception as e:
        logger.error(f"CRASH: {str(e)}")
        # Raise valid HTTP error so client knows what happened
        raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")
        
    finally:
        # 6. Cleanup: Ensure file handle is closed
        await file.close()
        
        # Optional: Delete file after processing to save space
        # if os.path.exists(temp_file_path):
        #     os.remove(temp_file_path)