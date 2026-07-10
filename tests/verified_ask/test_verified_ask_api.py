from __future__ import annotations

import inspect
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from apps.api.hybrid_retrieval.service import (
    HybridRetrievalConfig,
    HybridRetrievalService,
)
from apps.api.main import app
from apps.api.routes import verified_ask as verified_ask_route
from apps.api.verified_ask.service import VerifiedAskService


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        verified_ask_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_ask_user() -> Iterator[None]:
    dependency = _dependency_for(
        "ask_plantmind_verified"
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "test-reliability-engineer",
        "email": "reliability@plantmind.local",
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
def isolated_verified_ask_service(
    tmp_path: Path,
) -> Iterator[VerifiedAskService]:
    original_service = verified_ask_route.verified_ask_service

    retrieval_service = HybridRetrievalService(
        HybridRetrievalConfig(
            extracted_dir=tmp_path / "extracted",
            collection_dir=tmp_path / "retrieval",
            collection_name="plantmind_industrial_documents",
        )
    )

    ask_service = VerifiedAskService(
        retrieval_service=retrieval_service,
    )

    verified_ask_route.verified_ask_service = ask_service

    try:
        yield ask_service
    finally:
        verified_ask_route.verified_ask_service = original_service


def write_extracted_artifact(
    extracted_dir: Path,
    *,
    document_id: str,
    chunks: list[dict],
) -> None:
    extracted_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_path = extracted_dir / f"{document_id}.json"
    artifact_path.write_text(
        json.dumps(
            {
                "status": "completed",
                "document_id": document_id,
                "chunks": chunks,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_verified_ask_api_returns_grounded_answer_with_citations(
    tmp_path: Path,
) -> None:
    write_extracted_artifact(
        tmp_path / "extracted",
        document_id="DOC-P101-REV-2",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-2-PAGE-0003-CHUNK-0001",
                "text": (
                    "P-101 bearing lubrication procedure requires vibration "
                    "inspection and post-maintenance verification."
                ),
                "page_number": 3,
                "section_heading": "P-101 Bearing Procedure",
                "asset_ids": ["P-101"],
            }
        ],
    )

    with isolated_verified_ask_service(tmp_path) as ask_service:
        ask_service.retrieval_service.build_index(
            collection_name="plantmind_industrial_documents",
            rebuild=True,
        )

        with authorized_ask_user():
            response = client.post(
                "/ask-plantmind/verified",
                json={
                    "question": "What is the P-101 bearing lubrication procedure?",
                    "asset_ids": ["P-101"],
                    "top_k": 3,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["request_id"]
    assert payload["answer_status"] == "supported"
    assert payload["grounded"] is True
    assert payload["citations_verified"] is True
    assert payload["confidence"] > 0
    assert payload["unsupported_claims"] == []
    assert payload["evidence"][0]["document_id"] == "DOC-P101-REV-2"
    assert payload["evidence"][0]["page"] == 3
    assert payload["evidence"][0]["section"] == "P-101 Bearing Procedure"
    assert payload["evidence"][0]["revision"] == 2


def test_verified_ask_api_uses_safe_answer_for_insufficient_evidence(
    tmp_path: Path,
) -> None:
    with isolated_verified_ask_service(tmp_path):
        with authorized_ask_user():
            response = client.post(
                "/ask-plantmind/verified",
                json={
                    "question": "What is the C-201 compressor seal replacement torque?",
                    "asset_ids": ["C-201"],
                    "top_k": 3,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["request_id"]
    assert payload["answer_status"] == "insufficient_evidence"
    assert payload["grounded"] is False
    assert payload["citations_verified"] is True
    assert payload["confidence"] == 0
    assert payload["evidence"] == []
    assert payload["missing_information"]
    assert payload["unsupported_claims"] == []
    assert "cannot confirm" in payload["direct_answer"]


def test_verified_ask_api_surfaces_contradictory_evidence(
    tmp_path: Path,
) -> None:
    write_extracted_artifact(
        tmp_path / "extracted",
        document_id="DOC-P101-REV-2",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-2-PAGE-0001-CHUNK-0001",
                "text": "P-101 vibration is high and bearing temperature increased.",
                "page_number": 1,
                "section_heading": "Abnormal Event",
                "asset_ids": ["P-101"],
            },
            {
                "chunk_id": "DOC-P101-REV-2-PAGE-0002-CHUNK-0001",
                "text": "P-101 vibration is normal and within limit.",
                "page_number": 2,
                "section_heading": "Normal Reading",
                "asset_ids": ["P-101"],
            },
        ],
    )

    with isolated_verified_ask_service(tmp_path) as ask_service:
        ask_service.retrieval_service.build_index(
            collection_name="plantmind_industrial_documents",
            rebuild=True,
        )

        with authorized_ask_user():
            response = client.post(
                "/ask-plantmind/verified",
                json={
                    "question": "Is P-101 vibration high or normal?",
                    "asset_ids": ["P-101"],
                    "top_k": 5,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["answer_status"] == "supported"
    assert payload["contradictory_evidence"]
    assert "contradictory evidence" in payload["direct_answer"]
    assert "Review contradictory evidence" in payload["recommended_next_action"]


def test_verified_ask_api_requires_authentication() -> None:
    response = client.post(
        "/ask-plantmind/verified",
        json={
            "question": "What is the P-101 bearing procedure?",
            "asset_ids": ["P-101"],
        },
    )

    assert response.status_code == 401