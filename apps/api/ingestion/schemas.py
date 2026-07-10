from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


IngestionStatus = Literal[
    "ingested",
    "duplicate",
    "unsupported",
    "failed",
]


class IngestionChunk(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    text: str
    character_start: int
    character_end: int
    token_estimate: int
    asset_ids: list[str]
    document_type: str
    source_filename: str


class IngestionChunkManifest(BaseModel):
    document_id: str
    total_chunks: int
    chunks: list[IngestionChunk]


class DocumentIngestionRequest(BaseModel):
    source_path: str
    asset_ids: list[str] = Field(default_factory=list)
    document_type: str = "unknown"
    source_system: str = "local_upload"
    uploaded_by: str | None = None


class DocumentIngestionResult(BaseModel):
    document_id: str
    status: IngestionStatus
    source_filename: str
    source_path: str
    stored_raw_path: str
    normalized_text_path: str | None = None
    chunk_manifest_path: str | None = None
    manifest_path: str
    checksum_sha256: str
    file_size_bytes: int
    extension: str
    document_type: str
    asset_ids: list[str]
    source_system: str
    uploaded_by: str | None = None
    text_extract_status: str
    text_preview: str | None = None
    chunk_count: int = 0
    message: str


class IngestionManifest(BaseModel):
    document_id: str
    source_filename: str
    source_path: str
    stored_raw_path: str
    normalized_text_path: str | None = None
    chunk_manifest_path: str | None = None
    checksum_sha256: str
    file_size_bytes: int
    extension: str
    document_type: str
    asset_ids: list[str]
    source_system: str
    uploaded_by: str | None = None
    text_extract_status: str
    text_preview: str | None = None
    chunk_count: int = 0
    created_at: str


class IngestionManifestListResponse(BaseModel):
    total: int
    documents: list[IngestionManifest]