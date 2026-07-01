from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.api.services.simple_retriever import ask_plantmind, get_suggested_questions


router = APIRouter(prefix="/ask", tags=["Ask PlantMind"])


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User question for PlantMind AI")
    asset_id: str | None = Field(default=None, description="Optional asset filter like P-101, C-201, HX-301")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of evidence chunks to retrieve")


@router.post("")
def ask(request: AskRequest):
    return ask_plantmind(
        question=request.question,
        asset_id=request.asset_id,
        top_k=request.top_k
    )


@router.get("/suggested-questions")
def suggested_questions():
    questions = get_suggested_questions()

    return {
        "total": len(questions),
        "questions": questions
    }