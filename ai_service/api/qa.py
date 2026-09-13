from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.postgres import get_db
from services.qa_service import QAService


router = APIRouter(
    prefix="/qa",
    tags=["QA"]
)


# ==========================================================
# Request
# ==========================================================

class QuestionRequest(BaseModel):

    question: str
    inspection_id: int | None = None


# ==========================================================
# POST /qa/ask
# ==========================================================

@router.post("/ask")
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):

    service = QAService(db)

    answer = service.ask(
        question=request.question,
        inspection_id=request.inspection_id
    )

    return {
        "question": request.question,
        "inspection_id": request.inspection_id,
        "answer": answer
    }