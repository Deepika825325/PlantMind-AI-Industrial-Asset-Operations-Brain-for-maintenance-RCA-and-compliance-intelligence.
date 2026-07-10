from __future__ import annotations

from pydantic import BaseModel, Field


class RagAnswerRequest(BaseModel):
    question: str
    asset_id: str | None = None
    document_type: str | None = None
    limit: int = 5


class RagAnswerCitation(BaseModel):
    citation_id: str
    document_id: str
    chunk_id: str
    chunk_index: int
    source_filename: str
    asset_ids: list[str] = Field(default_factory=list)
    document_type: str
    score: float
    matched_terms: list[str] = Field(default_factory=list)
    quoted_text: str


class RagAnswerResponse(BaseModel):
    answer_id: str
    question: str
    answer: str
    confidence: float
    retrieval_status: str
    total_citations: int
    citations: list[RagAnswerCitation] = Field(default_factory=list)