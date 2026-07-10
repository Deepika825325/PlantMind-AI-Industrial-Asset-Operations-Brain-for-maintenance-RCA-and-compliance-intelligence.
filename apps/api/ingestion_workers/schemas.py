from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ExtractionJobStatus = Literal[
    "queued",
    "running",
    "completed",
    "failed",
]


class ParserMetadata(BaseModel):
    parser_name: str
    parser_version: str
    parser_mode: str


class ExtractionJobRequest(BaseModel):
    document_id: str


class ExtractedHeading(BaseModel):
    page_number: int
    heading_text: str
    line_number: int


class ExtractedTable(BaseModel):
    page_number: int
    table_index: int
    rows: list[list[str]] = Field(default_factory=list)


class PageAwareChunk(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    page_number: int
    section_heading: str | None = None
    text: str
    character_start: int
    character_end: int
    token_estimate: int
    asset_ids: list[str] = Field(default_factory=list)


class ExtractionError(BaseModel):
    code: str
    message: str
    retryable: bool = True


class ExtractionWorkerJob(BaseModel):
    job_id: str
    document_id: str
    status: ExtractionJobStatus
    attempts: int = 0
    parser: ParserMetadata
    total_pages: int = 0
    total_chunks: int = 0
    detected_asset_ids: list[str] = Field(default_factory=list)
    headings: list[ExtractedHeading] = Field(default_factory=list)
    tables: list[ExtractedTable] = Field(default_factory=list)
    chunks: list[PageAwareChunk] = Field(default_factory=list)
    errors: list[ExtractionError] = Field(default_factory=list)
    created_at: str
    updated_at: str
