from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


IngestionStatus = Literal[
    "ingested",
    "duplicate",
    "unsupported",
    "failed",
]

LifecycleStatus = Literal[
    "uploaded",
    "validating",
    "extracting",
    "chunking",
    "indexing",
    "ready",
    "failed",
]

ProcessingStatus = Literal[
    "pending",
    "validating",
    "extracting",
    "chunking",
    "ready",
    "stored_only",
    "failed",
]


class IngestionValidationError(BaseModel):
    code: str
    message: str
    field: str | None = None


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
    lifecycle_status: LifecycleStatus = "ready"
    upload_status: str = "uploaded"
    processing_status: ProcessingStatus = "ready"
    source_filename: str
    source_path: str
    stored_raw_path: str
    object_storage_path: str
    storage_backend: str = "local_object_store"
    normalized_text_path: str | None = None
    chunk_manifest_path: str | None = None
    manifest_path: str
    checksum_sha256: str
    detected_mime_type: str
    file_size_bytes: int
    max_file_size_bytes: int
    extension: str
    document_type: str
    asset_ids: list[str]
    source_system: str
    uploaded_by: str | None = None
    text_extract_status: str
    text_preview: str | None = None
    chunk_count: int = 0
    revision_group_id: str
    revision_number: int
    is_latest_revision: bool = True
    is_duplicate: bool = False
    duplicate_of_document_id: str | None = None
    validation_errors: list[IngestionValidationError] = Field(default_factory=list)
    message: str


class IngestionManifest(BaseModel):
    document_id: str
    source_filename: str
    source_path: str
    stored_raw_path: str
    object_storage_path: str
    storage_backend: str = "local_object_store"
    normalized_text_path: str | None = None
    chunk_manifest_path: str | None = None
    checksum_sha256: str
    detected_mime_type: str
    file_size_bytes: int
    max_file_size_bytes: int
    extension: str
    document_type: str
    asset_ids: list[str]
    source_system: str
    uploaded_by: str | None = None
    lifecycle_status: LifecycleStatus = "ready"
    upload_status: str = "uploaded"
    processing_status: ProcessingStatus = "ready"
    text_extract_status: str
    text_preview: str | None = None
    chunk_count: int = 0
    revision_group_id: str
    revision_number: int
    is_latest_revision: bool = True
    is_duplicate: bool = False
    duplicate_of_document_id: str | None = None
    validation_errors: list[IngestionValidationError] = Field(default_factory=list)
    created_at: str


class IngestionManifestListResponse(BaseModel):
    total: int
    documents: list[IngestionManifest]