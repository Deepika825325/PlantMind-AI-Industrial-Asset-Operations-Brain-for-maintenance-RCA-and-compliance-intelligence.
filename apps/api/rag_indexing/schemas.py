from __future__ import annotations

from pydantic import BaseModel, Field


class RagIndexedChunk(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    text: str
    normalized_text: str
    keyword_terms: list[str] = Field(default_factory=list)
    asset_ids: list[str] = Field(default_factory=list)
    document_type: str
    source_filename: str
    character_start: int
    character_end: int
    token_estimate: int


class RagIndexManifest(BaseModel):
    index_id: str
    source: str
    total_documents: int
    total_chunks: int
    asset_ids: list[str] = Field(default_factory=list)
    document_types: list[str] = Field(default_factory=list)
    index_path: str
    created_at: str


class RagIndexBuildResult(BaseModel):
    index_id: str
    status: str
    total_documents: int
    total_chunks: int
    index_path: str
    manifest_path: str
    message: str


class RagIndexedChunkListResponse(BaseModel):
    total: int
    chunks: list[RagIndexedChunk]


class RagSearchRequest(BaseModel):
    query: str
    asset_id: str | None = None
    document_type: str | None = None
    limit: int = 5


class RagSearchHit(BaseModel):
    rank: int
    score: float
    document_id: str
    chunk_id: str
    chunk_index: int
    text: str
    asset_ids: list[str] = Field(default_factory=list)
    document_type: str
    source_filename: str
    matched_terms: list[str] = Field(default_factory=list)


class RagSearchResponse(BaseModel):
    query: str
    total: int
    hits: list[RagSearchHit]
