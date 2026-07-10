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
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
    RagIndexingConfig,
)
from apps.api.routes import rag_indexing as rag_indexing_route


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        rag_indexing_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_rag_index_user() -> Iterator[None]:
    dependencies = [
        _dependency_for("build_ingestion_rag_index"),
        _dependency_for("get_ingestion_rag_index_manifest"),
        _dependency_for("list_ingestion_rag_index_chunks"),
    ]

    for dependency in dependencies:
        app.dependency_overrides[dependency] = lambda: {
            "user_id": "test-data-scientist",
            "email": "ds@plantmind.local",
            "role": "data_scientist",
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
def isolated_rag_indexing_service(
    tmp_path: Path,
) -> Iterator[IngestionRagIndexingService]:
    original_service = rag_indexing_route.rag_indexing_service

    ingestion_service = DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
            chunks_dir=tmp_path / "chunks",
            chunk_size_chars=80,
            chunk_overlap_chars=10,
        )
    )

    source = tmp_path / "inspection-note.txt"
    source.write_text(
        "P-101 vibration increased. "
        "Bearing temperature increased. "
        "Lubrication evidence is missing.",
        encoding="utf-8",
    )

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    service = IngestionRagIndexingService(
        ingestion_service=ingestion_service,
        config=RagIndexingConfig(
            index_dir=tmp_path / "rag_index",
        ),
    )

    rag_indexing_route.rag_indexing_service = service

    try:
        yield service
    finally:
        rag_indexing_route.rag_indexing_service = original_service


def test_rag_indexing_api_builds_index(
    tmp_path: Path,
) -> None:
    with isolated_rag_indexing_service(tmp_path):
        with authorized_rag_index_user():
            response = client.post(
                "/rag-indexing/ingestion/build"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "built"
    assert payload["total_documents"] == 1
    assert payload["total_chunks"] >= 1
    assert payload["index_path"]
    assert payload["manifest_path"]


def test_rag_indexing_api_reads_manifest(
    tmp_path: Path,
) -> None:
    with isolated_rag_indexing_service(tmp_path) as service:
        service.build_index()

        with authorized_rag_index_user():
            response = client.get(
                "/rag-indexing/ingestion/manifest"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["source"] == "ingestion_chunk_manifests"
    assert payload["total_documents"] == 1
    assert payload["total_chunks"] >= 1
    assert payload["asset_ids"] == ["P-101"]


def test_rag_indexing_api_lists_chunks(
    tmp_path: Path,
) -> None:
    with isolated_rag_indexing_service(tmp_path) as service:
        service.build_index()

        with authorized_rag_index_user():
            response = client.get(
                "/rag-indexing/ingestion/chunks"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] >= 1
    assert payload["chunks"][0]["asset_ids"] == ["P-101"]
    assert "vibration" in payload["chunks"][0]["keyword_terms"]


def test_rag_indexing_api_requires_authentication() -> None:
    response = client.post(
        "/rag-indexing/ingestion/build"
    )

    assert response.status_code == 401