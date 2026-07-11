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


def _permission_dependency() -> Any:
    user_parameter = inspect.signature(
        ingestion_route.ingest_local_document
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_ingestion_user() -> Iterator[None]:
    dependency = _permission_dependency()

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "test-admin",
        "email": "admin@plantmind.local",
        "role": "administrator",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


def test_ingestion_api_ingests_local_text_file(
    tmp_path: Path,
) -> None:
    source = tmp_path / "inspection-note.txt"
    source.write_text(
        "P-101 inspection found vibration increase.",
        encoding="utf-8",
    )

    original_service = ingestion_route.ingestion_service
    ingestion_route.ingestion_service = DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
        )
    )

    try:
        with authorized_ingestion_user():
            response = client.post(
                "/ingestion/documents/local-file",
                json=DocumentIngestionRequest(
                    source_path=str(source),
                    asset_ids=["P-101"],
                    document_type="inspection_note",
                    source_system="api_test",
                    uploaded_by="admin@plantmind.local",
                ).model_dump(),
            )
    finally:
        ingestion_route.ingestion_service = original_service

    assert response.status_code == 201

    payload = response.json()

    assert payload["document_id"].startswith("DOC-ING-")
    assert payload["status"] == "ingested"
    assert payload["asset_ids"] == ["P-101"]
    assert payload["text_extract_status"] == "extracted"
    assert payload["normalized_text_path"] is not None


def test_ingestion_api_returns_404_for_missing_file() -> None:
    with authorized_ingestion_user():
        response = client.post(
            "/ingestion/documents/local-file",
            json={
                "source_path": "missing-file-does-not-exist.txt",
                "asset_ids": ["P-101"],
                "document_type": "inspection_note",
            },
        )

    assert response.status_code == 404


def test_ingestion_api_requires_authentication(
    tmp_path: Path,
) -> None:
    source = tmp_path / "inspection-note.txt"
    source.write_text(
        "P-101 inspection found vibration increase.",
        encoding="utf-8",
    )

    response = client.post(
        "/ingestion/documents/local-file",
        json={
            "source_path": str(source),
            "asset_ids": ["P-101"],
            "document_type": "inspection_note",
        },
    )

    assert response.status_code == 401