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
from apps.api.rag_answering.service import (
    IngestionRagAnsweringService,
)
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
    RagIndexingConfig,
)
from apps.api.routes import rag_answering as rag_answering_route


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        rag_answering_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_answer_user() -> Iterator[None]:
    dependency = _dependency_for(
        "answer_from_ingested_documents"
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
def isolated_answering_service(
    tmp_path: Path,
) -> Iterator[IngestionRagAnsweringService]:
    original_service = rag_answering_route.rag_answering_service

    ingestion_service = DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
            chunks_dir=tmp_path / "chunks",
            chunk_size_chars=160,
            chunk_overlap_chars=20,
        )
    )

    p101 = tmp_path / "p101-inspection.txt"
    hx301 = tmp_path / "hx301-inspection.txt"

    p101.write_text(
        "P-101 vibration increased above the normal operating range. "
        "Bearing temperature also increased. "
        "Lubrication evidence is missing from the inspection record.",
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

    indexing_service = IngestionRagIndexingService(
        ingestion_service=ingestion_service,
        config=RagIndexingConfig(
            index_dir=tmp_path / "rag_index",
        ),
    )

    indexing_service.build_index()

    answering_service = IngestionRagAnsweringService(
        rag_indexing_service=indexing_service,
    )

    rag_answering_route.rag_answering_service = answering_service

    try:
        yield answering_service
    finally:
        rag_answering_route.rag_answering_service = original_service


def test_rag_answering_api_answers_with_citations(
    tmp_path: Path,
) -> None:
    with isolated_answering_service(tmp_path):
        with authorized_answer_user():
            response = client.post(
                "/rag-answering/ingestion/answer",
                json={
                    "question": "Why is P-101 vibration high?",
                    "asset_id": "P-101",
                    "limit": 4,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["retrieval_status"] == "answered_with_ingested_context"
    assert payload["confidence"] > 0
    assert payload["total_citations"] >= 1
    assert "P-101" in payload["answer"]
    assert payload["citations"][0]["citation_id"] == "CIT-001"
    assert "vibration" in payload["citations"][0]["matched_terms"]


def test_rag_answering_api_respects_asset_filter(
    tmp_path: Path,
) -> None:
    with isolated_answering_service(tmp_path):
        with authorized_answer_user():
            response = client.post(
                "/rag-answering/ingestion/answer",
                json={
                    "question": "Why is heat transfer reduced?",
                    "asset_id": "HX-301",
                    "limit": 4,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total_citations"] >= 1
    assert payload["citations"][0]["asset_ids"] == ["HX-301"]
    assert "fouling" in payload["answer"].lower()


def test_rag_answering_api_returns_no_context(
    tmp_path: Path,
) -> None:
    with isolated_answering_service(tmp_path):
        with authorized_answer_user():
            response = client.post(
                "/rag-answering/ingestion/answer",
                json={
                    "question": "Why is compressor seal leaking?",
                    "asset_id": "C-201",
                    "limit": 4,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["retrieval_status"] == "no_relevant_context"
    assert payload["confidence"] == 0
    assert payload["total_citations"] == 0
    assert payload["citations"] == []


def test_rag_answering_api_requires_authentication() -> None:
    response = client.post(
        "/rag-answering/ingestion/answer",
        json={
            "question": "Why is P-101 vibration high?",
            "asset_id": "P-101",
        },
    )

    assert response.status_code == 401