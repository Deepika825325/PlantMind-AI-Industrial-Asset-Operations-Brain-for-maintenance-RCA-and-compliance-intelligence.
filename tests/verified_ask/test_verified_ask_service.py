from __future__ import annotations

import json
from pathlib import Path

from apps.api.hybrid_retrieval.service import (
    HybridRetrievalConfig,
    HybridRetrievalService,
)
from apps.api.verified_ask.schemas import VerifiedAskRequest
from apps.api.verified_ask.service import VerifiedAskService


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


def make_services(
    tmp_path: Path,
) -> tuple[
    HybridRetrievalService,
    VerifiedAskService,
]:
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

    return retrieval_service, ask_service


def test_verified_ask_returns_evidence_backed_answer(
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

    retrieval_service, ask_service = make_services(
        tmp_path,
    )

    retrieval_service.build_index(
        collection_name="plantmind_industrial_documents",
        rebuild=True,
    )

    response = ask_service.answer(
        VerifiedAskRequest(
            question="What is the P-101 bearing lubrication procedure?",
            asset_ids=["P-101"],
            top_k=3,
        )
    )

    assert response.request_id
    assert response.answer_status == "supported"
    assert response.grounded is True
    assert response.citations_verified is True
    assert response.confidence > 0
    assert response.evidence
    assert response.evidence[0].document_id == "DOC-P101-REV-2"
    assert response.evidence[0].page == 3
    assert response.evidence[0].section == "P-101 Bearing Procedure"
    assert response.evidence[0].revision == 2
    assert response.unsupported_claims == []
    assert "verified PlantMind evidence" in response.direct_answer


def test_verified_ask_safe_answer_when_evidence_is_insufficient(
    tmp_path: Path,
) -> None:
    _retrieval_service, ask_service = make_services(
        tmp_path,
    )

    response = ask_service.answer(
        VerifiedAskRequest(
            question="What is the compressor seal replacement torque?",
            asset_ids=["C-201"],
            top_k=3,
        )
    )

    assert response.request_id
    assert response.answer_status == "insufficient_evidence"
    assert response.grounded is False
    assert response.citations_verified is True
    assert response.confidence == 0
    assert response.evidence == []
    assert response.missing_information
    assert response.unsupported_claims == []
    assert "cannot confirm" in response.direct_answer


def test_verified_ask_surfaces_contradictory_evidence(
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

    retrieval_service, ask_service = make_services(
        tmp_path,
    )

    retrieval_service.build_index(
        collection_name="plantmind_industrial_documents",
        rebuild=True,
    )

    response = ask_service.answer(
        VerifiedAskRequest(
            question="Is P-101 vibration high or normal?",
            asset_ids=["P-101"],
            top_k=5,
        )
    )

    assert response.answer_status == "supported"
    assert response.contradictory_evidence
    assert response.confidence < 1
    assert "contradictory evidence" in response.direct_answer
    assert "Review contradictory evidence" in response.recommended_next_action


def test_verified_ask_reports_missing_question_terms(
    tmp_path: Path,
) -> None:
    write_extracted_artifact(
        tmp_path / "extracted",
        document_id="DOC-P101-REV-1",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-1-PAGE-0001-CHUNK-0001",
                "text": "P-101 bearing lubrication procedure is available.",
                "page_number": 1,
                "section_heading": "Procedure",
                "asset_ids": ["P-101"],
            }
        ],
    )

    retrieval_service, ask_service = make_services(
        tmp_path,
    )

    retrieval_service.build_index(
        collection_name="plantmind_industrial_documents",
        rebuild=True,
    )

    response = ask_service.answer(
        VerifiedAskRequest(
            question="What is the P-101 bearing lubrication procedure torque?",
            asset_ids=["P-101"],
            top_k=3,
        )
    )

    assert response.answer_status == "supported"
    assert response.missing_information
    assert "torque" in response.missing_information[0]