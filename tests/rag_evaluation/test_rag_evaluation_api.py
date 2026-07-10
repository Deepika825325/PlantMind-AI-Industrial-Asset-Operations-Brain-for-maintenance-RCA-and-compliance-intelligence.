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
from apps.api.rag_answering.service import IngestionRagAnsweringService
from apps.api.rag_evaluation.service import RagEvaluationService
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
    RagIndexingConfig,
)
from apps.api.routes import rag_evaluation as rag_evaluation_route


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        rag_evaluation_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_evaluation_user() -> Iterator[None]:
    dependency = _dependency_for(
        "run_ingestion_rag_evaluation"
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
def isolated_evaluation_service(
    tmp_path: Path,
) -> Iterator[RagEvaluationService]:
    original_service = rag_evaluation_route.rag_evaluation_service

    ingestion_service = DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
            chunks_dir=tmp_path / "chunks",
            chunk_size_chars=180,
            chunk_overlap_chars=20,
        )
    )

    p101 = tmp_path / "p101-api-eval-note.txt"
    hx301 = tmp_path / "hx301-api-eval-note.txt"

    p101.write_text(
        "P-101 vibration increased above normal range. "
        "Bearing temperature increased after the vibration event. "
        "Lubrication evidence is missing from the inspection record.",
        encoding="utf-8",
    )

    hx301.write_text(
        "HX-301 fouling reduced heat transfer efficiency. "
        "Cleaning heat-transfer surfaces is recommended.",
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

    evaluation_service = RagEvaluationService(
        rag_answering_service=answering_service,
    )

    rag_evaluation_route.rag_evaluation_service = evaluation_service

    try:
        yield evaluation_service
    finally:
        rag_evaluation_route.rag_evaluation_service = original_service


def test_rag_evaluation_api_runs_benchmark(
    tmp_path: Path,
) -> None:
    with isolated_evaluation_service(tmp_path):
        with authorized_evaluation_user():
            response = client.post(
                "/rag-evaluation/ingestion/run",
                json={
                    "questions": [
                        {
                            "question_id": "RAG-Q-001",
                            "question": "Why is P-101 vibration high?",
                            "asset_id": "P-101",
                            "expected_terms": [
                                "vibration",
                                "bearing",
                            ],
                        },
                        {
                            "question_id": "RAG-Q-002",
                            "question": "Why is HX-301 heat transfer reduced?",
                            "asset_id": "HX-301",
                            "expected_terms": [
                                "fouling",
                                "heat transfer",
                            ],
                        },
                    ]
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["evaluation_id"].startswith("RAG-EVAL-")
    assert payload["summary"]["total_questions"] == 2
    assert payload["summary"]["passed_questions"] == 2
    assert payload["summary"]["failed_questions"] == 0
    assert payload["summary"]["pass_rate"] == 1.0
    assert len(payload["results"]) == 2
    assert all(
        result["passed"]
        for result in payload["results"]
    )


def test_rag_evaluation_api_reports_failed_case(
    tmp_path: Path,
) -> None:
    with isolated_evaluation_service(tmp_path):
        with authorized_evaluation_user():
            response = client.post(
                "/rag-evaluation/ingestion/run",
                json={
                    "questions": [
                        {
                            "question_id": "RAG-Q-003",
                            "question": "Why is P-101 vibration high?",
                            "asset_id": "P-101",
                            "expected_terms": [
                                "cavitation",
                            ],
                        }
                    ]
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["summary"]["total_questions"] == 1
    assert payload["summary"]["passed_questions"] == 0
    assert payload["summary"]["failed_questions"] == 1
    assert payload["results"][0]["passed"] is False
    assert "cavitation" in payload["results"][0]["missing_expected_terms"]
    assert "missing_expected_terms" in payload["results"][0]["warnings"]


def test_rag_evaluation_api_requires_authentication() -> None:
    response = client.post(
        "/rag-evaluation/ingestion/run",
        json={
            "questions": []
        },
    )

    assert response.status_code == 401