from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DocumentStatusFilter = Literal[
    "ready",
    "stored_only",
    "failed",
    "all",
]

RetrievalMode = Literal[
    "hybrid",
    "keyword",
    "vector",
]


class RetrievalDocumentMetadata(BaseModel):
    document_id: str
    revision: int
    page: int
    section: str | None = None
    asset_ids: list[str] = Field(default_factory=list)
    source_quality: float = 1.0
    approval_status: str = "approved"
    effective_date: str | None = None
    document_status: str = "ready"
    is_obsolete: bool = False
    source_filename: str
    document_type: str


class HybridRetrievalIndexRequest(BaseModel):
    collection_name: str = "plantmind_industrial_documents"
    rebuild: bool = True


class HybridRetrievalIndexResult(BaseModel):
    collection_name: str
    total_points: int
    indexed_document_ids: list[str]
    message: str


class HybridRetrievalSearchRequest(BaseModel):
    query: str
    mode: RetrievalMode = "hybrid"
    asset_ids: list[str] = Field(default_factory=list)
    document_status: DocumentStatusFilter = "ready"
    include_obsolete: bool = False
    revision: int | None = None
    top_k: int = 5


class HybridRetrievalHit(BaseModel):
    point_id: str
    chunk_id: str
    text: str
    keyword_score: float
    vector_score: float
    hybrid_score: float
    matched_terms: list[str] = Field(default_factory=list)
    metadata: RetrievalDocumentMetadata


class HybridRetrievalSearchResponse(BaseModel):
    query: str
    mode: RetrievalMode
    total_hits: int
    hits: list[HybridRetrievalHit]