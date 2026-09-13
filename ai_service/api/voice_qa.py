from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil

from services.speech_service import SpeechService
from services.qa_service import ask


router = APIRouter(
    prefix="/voice",
    tags=["Voice Assistant"]
)


# Charger Whisper une seule fois
speech_service = SpeechService()


@router.post("/ask")
def voice_question(
    audio: UploadFile = File(...)
):

    # ==========================================
    # Vérifier le fichier
    # ==========================================

    if not audio.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio file is required"
        )

    # ==========================================
    # Créer dossier temporaire
    # ==========================================

    os.makedirs("temp", exist_ok=True)

    audio_path = os.path.join(
        "temp",
        audio.filename
    )

    # ==========================================
    # Sauvegarder audio
    # ==========================================

    try:

        with open(audio_path, "wb") as buffer:

            shutil.copyfileobj(
                audio.file,
                buffer
            )

        # ==========================================
        # Audio → Texte
        # ==========================================

        question = speech_service.transcribe(
            audio_path
        )

        # ==========================================
        # Texte → LLM + RAG
        # ==========================================

        answer = ask(question)

        # ==========================================
        # Retour
        # ==========================================

        return {

            "success": True,

            "question": question,

            "answer": answer

        }

    finally:

        # ==========================================
        # Supprimer fichier temporaire
        # ==========================================

        if os.path.exists(audio_path):

            os.remove(audio_path)