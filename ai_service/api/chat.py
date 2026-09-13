from fastapi import APIRouter
from pydantic import BaseModel

from services.qa_service import ask

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):

    answer = ask(request.question)

    return ChatResponse(
        answer=answer
    )