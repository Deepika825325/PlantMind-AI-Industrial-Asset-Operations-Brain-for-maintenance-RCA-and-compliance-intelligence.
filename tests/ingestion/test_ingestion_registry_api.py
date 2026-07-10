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
def authorized_registry_user() -> Iterator[None]:
    dependencies = [
        _dependency_for("list_ingested_documents"),
        _dependency_for("get_ingested_document"),
    ]

    for dependency in dependencies:
        app.dependency_overrides[dependency] = lambda: {
            "user_id": "test-reader",
            "email": "reader@plantmind.local",
            "role": "administrator",
        }

    try:
        yield
    finally:
        for dependency in dependencies:
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
        )
    )

    ingestion_route.ingestion_service = service

    try:
        yield service
    finally:
        ingestion_route.ingestion_service = original_service


def test_registry_api_lists_ingested_documents(
    tmp_path: Path,
) -> None:
    source = tmp_path / "inspection-note.txt"
    source.write_text(
        "P-101 inspection found vibration increase.",
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

        with authorized_registry_user():
            response = client.get(
                "/ingestion/documents"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 1
    assert payload["documents"][0]["document_id"] == result.document_id
    assert payload["documents"][0]["asset_ids"] == ["P-101"]


def test_registry_api_gets_single_ingested_document(
    tmp_path: Path,
) -> None:
    source = tmp_path / "maintenance-note.md"
    source.write_text(
        "P-101 bearing inspection is required.",
        encoding="utf-8",
    )

    with isolated_ingestion_service(tmp_path) as service:
        result = service.ingest_document(
            DocumentIngestionRequest(
                source_path=str(source),
                asset_ids=["P-101"],
                document_type="maintenance_note",
            )
        )

        with authorized_registry_user():
            response = client.get(
                f"/ingestion/documents/{result.document_id}"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["document_id"] == result.document_id
    assert payload["document_type"] == "maintenance_note"
    assert payload["text_extract_status"] == "extracted"


def test_registry_api_returns_404_for_unknown_document(
    tmp_path: Path,
) -> None:
    with isolated_ingestion_service(tmp_path):
        with authorized_registry_user():
            response = client.get(
                "/ingestion/documents/DOC-ING-DOES-NOT-EXIST"
            )

    assert response.status_code == 404


def test_registry_api_requires_authentication() -> None:
    response = client.get(
        "/ingestion/documents"
    )

    assert response.status_code == 401