from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil

from services.speech_service import SpeechService
from services.qa_service import ask


router = APIRouter(
    prefix="/voice",
    tags=["Voice Assistant"]
)


# ==========================================================
# WHISPER
# ==========================================================

speech_service = SpeechService()


# ==========================================================
# MODELE POUR QUESTION TEXTE
# ==========================================================

class TextQuestion(BaseModel):
    question: str


# ==========================================================
# AUDIO → TEXTE → LLM + RAG
# ==========================================================

@router.post("/ask")
def voice_question(
    audio: UploadFile = File(...)
):

    if not audio.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio file is required"
        )

    os.makedirs("temp", exist_ok=True)

    audio_path = os.path.join(
        "temp",
        audio.filename
    )

    try:

        with open(audio_path, "wb") as buffer:

            shutil.copyfileobj(
                audio.file,
                buffer
            )

        # Audio → texte
        question = speech_service.transcribe(
            audio_path
        )

        if not question:
            raise HTTPException(
                status_code=400,
                detail="Unable to transcribe audio"
            )

        # Texte → LLM + RAG
        answer = ask(question)

        return {
            "success": True,
            "question": question,
            "answer": answer
        }

    finally:

        if os.path.exists(audio_path):
            os.remove(audio_path)


# ==========================================================
# TEXTE → LLM + RAG
# ==========================================================

@router.post("/ask-text")
def text_question(
    data: TextQuestion
):

    question = data.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question is required"
        )

    try:

        # ==================================================
        # QUESTION → LLM + RAG
        # ==================================================

        answer = ask(question)

        return {
            "success": True,
            "question": question,
            "answer": answer
        }

    except Exception as e:

        print("❌ Erreur LLM :", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )