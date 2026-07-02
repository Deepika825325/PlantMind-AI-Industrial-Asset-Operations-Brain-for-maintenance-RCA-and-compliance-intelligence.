from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from apps.api.services.simple_retriever import (
    ask_plantmind,
    get_suggested_questions,
    search_evidence,
)


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


@router.get("/search")
def search(
    query: str = Query(..., min_length=3),
    asset_id: str | None = Query(default=None),
    top_k: int = Query(default=10, ge=1, le=20)
):
    return search_evidence(
        query=query,
        asset_id=asset_id,
        top_k=top_k
    )


@router.get("/suggested-questions")
def suggested_questions():
    questions = get_suggested_questions()

    return {
        "total": len(questions),
        "questions": questions
    }