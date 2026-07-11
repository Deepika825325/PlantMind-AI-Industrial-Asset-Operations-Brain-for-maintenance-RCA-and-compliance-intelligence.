from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from apps.api.ingestion.schemas import DocumentIngestionRequest
from apps.api.ingestion.service import (
    DocumentIngestionService,
    IngestionConfig,
)
from apps.api.main import app
from apps.api.routes import ingestion as ingestion_route


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        ingestion_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_chunk_reader() -> Iterator[None]:
    dependency = _dependency_for(
        "get_ingested_document_chunks"
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "test-reader",
        "email": "reader@plantmind.local",
        "role": "administrator",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_ingestion_service(
    tmp_path: Path,
) -> Iterator[DocumentIngestionService]:
    original_service = ingestion_route.ingestion_service

    service = DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
            chunks_dir=tmp_path / "chunks",
            chunk_size_chars=80,
            chunk_overlap_chars=10,
        )
    )

    ingestion_route.ingestion_service = service

    try:
        yield service
    finally:
        ingestion_route.ingestion_service = original_service


def test_chunks_api_gets_document_chunks(
    tmp_path: Path,
) -> None:
    source = tmp_path / "inspection-note.txt"
    source.write_text(
        "P-101 vibration increased. "
        "Bearing temperature increased. "
        "Lubrication evidence is missing. "
        "Maintenance inspection is required.",
        encoding="utf-8",
    )

    with isolated_ingestion_service(tmp_path) as service:
        result = service.ingest_document(
            DocumentIngestionRequest(
                source_path=str(source),
                asset_ids=["P-101"],
                document_type="inspection_note",
            )
        )

        with authorized_chunk_reader():
            response = client.get(
                f"/ingestion/documents/{result.document_id}/chunks"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["document_id"] == result.document_id
    assert payload["total_chunks"] == result.chunk_count
    assert payload["chunks"][0]["chunk_id"].startswith(
        f"{result.document_id}-CHUNK-"
    )
    assert payload["chunks"][0]["asset_ids"] == ["P-101"]


def test_chunks_api_returns_404_for_pdf_without_chunks(
    tmp_path: Path,
) -> None:
    source = tmp_path / "manual.pdf"
    source.write_bytes(b"%PDF-1.4 fake demo pdf")

    with isolated_ingestion_service(tmp_path) as service:
        result = service.ingest_document(
            DocumentIngestionRequest(
                source_path=str(source),
                asset_ids=["P-101"],
                document_type="manual",
            )
        )

        with authorized_chunk_reader():
            response = client.get(
                f"/ingestion/documents/{result.document_id}/chunks"
            )

    assert response.status_code == 404


def test_chunks_api_requires_authentication(
    tmp_path: Path,
) -> None:
    response = client.get(
        "/ingestion/documents/DOC-ING-UNKNOWN/chunks"
    )

    assert response.status_code == 401