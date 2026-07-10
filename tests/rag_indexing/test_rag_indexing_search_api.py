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
def authorized_search_user() -> Iterator[None]:
    dependency = _dependency_for(
        "search_ingestion_rag_index"
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "test-data-scientist",
        "email": "ds@plantmind.local",
        "role": "data_scientist",
    }

    try:
        yield
    finally:
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
            chunk_size_chars=120,
            chunk_overlap_chars=10,
        )
    )

    p101 = tmp_path / "p101-inspection.txt"
    hx301 = tmp_path / "hx301-inspection.txt"

    p101.write_text(
        "P-101 vibration increased and bearing temperature increased. "
        "Lubrication evidence is missing.",
        encoding="utf-8",
    )

    hx301.write_text(
        "HX-301 fouling reduced heat transfer efficiency.",
        encoding="utf-8",
    )

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(p101),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(hx301),
            asset_ids=["HX-301"],
            document_type="inspection_note",
        )
    )

    service = IngestionRagIndexingService(
        ingestion_service=ingestion_service,
        config=RagIndexingConfig(
            index_dir=tmp_path / "rag_index",
        ),
    )

    service.build_index()

    rag_indexing_route.rag_indexing_service = service

    try:
        yield service
    finally:
        rag_indexing_route.rag_indexing_service = original_service


def test_rag_search_api_returns_relevant_hit(
    tmp_path: Path,
) -> None:
    with isolated_rag_indexing_service(tmp_path):
        with authorized_search_user():
            response = client.post(
                "/rag-indexing/ingestion/search",
                json={
                    "query": "Why is P-101 vibration high?",
                    "asset_id": "P-101",
                    "limit": 3,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["query"] == "Why is P-101 vibration high?"
    assert payload["total"] >= 1
    assert payload["hits"][0]["asset_ids"] == ["P-101"]
    assert "vibration" in payload["hits"][0]["matched_terms"]


def test_rag_search_api_respects_asset_filter(
    tmp_path: Path,
) -> None:
    with isolated_rag_indexing_service(tmp_path):
        with authorized_search_user():
            response = client.post(
                "/rag-indexing/ingestion/search",
                json={
                    "query": "fouling heat transfer",
                    "asset_id": "HX-301",
                    "limit": 3,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] >= 1
    assert payload["hits"][0]["asset_ids"] == ["HX-301"]
    assert "fouling" in payload["hits"][0]["matched_terms"]


def test_rag_search_api_returns_empty_for_no_match(
    tmp_path: Path,
) -> None:
    with isolated_rag_indexing_service(tmp_path):
        with authorized_search_user():
            response = client.post(
                "/rag-indexing/ingestion/search",
                json={
                    "query": "compressor seal leakage",
                    "asset_id": "C-201",
                    "limit": 3,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 0
    assert payload["hits"] == []


def test_rag_search_api_requires_authentication() -> None:
    response = client.post(
        "/rag-indexing/ingestion/search",
        json={
            "query": "P-101 vibration",
            "asset_id": "P-101",
        },
    )

    assert response.status_code == 401