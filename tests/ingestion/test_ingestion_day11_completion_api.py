from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

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
def authorized_ingestion_user() -> Iterator[None]:
    dependency = _dependency_for(
        "ingest_local_document"
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "test-engineer",
        "email": "engineer@plantmind.local",
        "role": "maintenance_engineer",
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
    *,
    max_file_size_bytes: int = 1024 * 1024,
) -> Iterator[DocumentIngestionService]:
    original_service = ingestion_route.ingestion_service

    service = DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
            chunks_dir=tmp_path / "chunks",
            max_file_size_bytes=max_file_size_bytes,
        )
    )

    ingestion_route.ingestion_service = service

    try:
        yield service
    finally:
        ingestion_route.ingestion_service = original_service


def test_ingestion_api_returns_structured_validation_error_for_unsupported_file(
    tmp_path: Path,
) -> None:
    source = tmp_path / "unsupported.exe"
    source.write_text(
        "unsupported document",
        encoding="utf-8",
    )

    with isolated_ingestion_service(tmp_path):
        with authorized_ingestion_user():
            response = client.post(
                "/ingestion/documents/local-file",
                json={
                    "source_path": str(source),
                    "asset_ids": ["P-101"],
                    "document_type": "unknown",
                },
            )

    assert response.status_code == 400

    payload = response.json()

    assert payload["detail"]["message"] == "Document validation failed"
    assert payload["detail"]["errors"][0]["code"] == "unsupported_file_extension"
    assert payload["detail"]["errors"][0]["field"] == "source_path"


def test_ingestion_api_returns_structured_validation_error_for_large_file(
    tmp_path: Path,
) -> None:
    source = tmp_path / "large-note.txt"
    source.write_text(
        "x" * 50,
        encoding="utf-8",
    )

    with isolated_ingestion_service(
        tmp_path,
        max_file_size_bytes=10,
    ):
        with authorized_ingestion_user():
            response = client.post(
                "/ingestion/documents/local-file",
                json={
                    "source_path": str(source),
                    "asset_ids": ["P-101"],
                    "document_type": "inspection_note",
                },
            )

    assert response.status_code == 400

    payload = response.json()

    assert payload["detail"]["message"] == "Document validation failed"
    assert payload["detail"]["errors"][0]["code"] == "file_too_large"
    assert "maximum allowed size" in payload["detail"]["errors"][0]["message"]


def test_ingestion_api_response_includes_day11_metadata(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-note.txt"
    source.write_text(
        "P-101 vibration increased near the bearing.",
        encoding="utf-8",
    )

    with isolated_ingestion_service(tmp_path):
        with authorized_ingestion_user():
            response = client.post(
                "/ingestion/documents/local-file",
                json={
                    "source_path": str(source),
                    "asset_ids": ["P-101"],
                    "document_type": "inspection_note",
                },
            )

    assert response.status_code == 201

    payload = response.json()

    assert payload["lifecycle_status"] == "ready"
    assert payload["upload_status"] == "uploaded"
    assert payload["processing_status"] == "ready"
    assert payload["detected_mime_type"] == "text/plain"
    assert payload["storage_backend"] == "local_object_store"
    assert payload["object_storage_path"] == payload["stored_raw_path"]
    assert payload["revision_group_id"] == "DOC-REV-P101-NOTE"
    assert payload["revision_number"] == 1
    assert payload["is_duplicate"] is False
    assert payload["validation_errors"] == []