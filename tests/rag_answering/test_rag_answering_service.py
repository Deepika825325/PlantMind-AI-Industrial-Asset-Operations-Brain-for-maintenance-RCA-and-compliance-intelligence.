from __future__ import annotations

from pathlib import Path

from apps.api.ingestion.schemas import DocumentIngestionRequest
from apps.api.ingestion.service import (
    DocumentIngestionService,
    IngestionConfig,
)
from apps.api.rag_answering.schemas import RagAnswerRequest
from apps.api.rag_answering.service import (
    IngestionRagAnsweringService,
)
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
    RagIndexingConfig,
)


def make_services(
    tmp_path: Path,
) -> tuple[
    DocumentIngestionService,
    IngestionRagIndexingService,
    IngestionRagAnsweringService,
]:
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

    indexing_service = IngestionRagIndexingService(
        ingestion_service=ingestion_service,
        config=RagIndexingConfig(
            index_dir=tmp_path / "rag_index",
        ),
    )

    answering_service = IngestionRagAnsweringService(
        rag_indexing_service=indexing_service,
    )

    return (
        ingestion_service,
        indexing_service,
        answering_service,
    )


def test_answers_question_with_citations(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-inspection.txt"
    source.write_text(
        "P-101 vibration increased above the normal operating range. "
        "Bearing temperature also increased. "
        "Lubrication evidence is missing from the inspection record.",
        encoding="utf-8",
    )

    ingestion_service, indexing_service, answering_service = make_services(
        tmp_path,
    )

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    indexing_service.build_index()

    response = answering_service.answer_question(
        RagAnswerRequest(
            question="Why is P-101 vibration high?",
            asset_id="P-101",
        )
    )

    assert response.retrieval_status == "answered_with_ingested_context"
    assert response.total_citations >= 1
    assert response.confidence > 0
    assert "P-101" in response.answer
    assert response.citations[0].document_id.startswith("DOC-ING-")
    assert response.citations[0].citation_id == "CIT-001"
    assert "vibration" in response.citations[0].matched_terms


def test_answer_respects_asset_filter(
    tmp_path: Path,
) -> None:
    p101 = tmp_path / "p101-note.txt"
    hx301 = tmp_path / "hx301-note.txt"

    p101.write_text(
        "P-101 vibration increased near the bearing.",
        encoding="utf-8",
    )

    hx301.write_text(
        "HX-301 fouling reduced heat transfer efficiency.",
        encoding="utf-8",
    )

    ingestion_service, indexing_service, answering_service = make_services(
        tmp_path,
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

    indexing_service.build_index()

    response = answering_service.answer_question(
        RagAnswerRequest(
            question="Why is heat transfer reduced?",
            asset_id="HX-301",
        )
    )

    assert response.total_citations >= 1
    assert response.citations[0].asset_ids == ["HX-301"]
    assert "fouling" in response.answer.lower()


def test_answer_returns_no_context_when_no_match(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-note.txt"
    source.write_text(
        "P-101 vibration increased near the bearing.",
        encoding="utf-8",
    )

    ingestion_service, indexing_service, answering_service = make_services(
        tmp_path,
    )

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    indexing_service.build_index()

    response = answering_service.answer_question(
        RagAnswerRequest(
            question="Why is compressor seal leaking?",
            asset_id="C-201",
        )
    )

    assert response.retrieval_status == "no_relevant_context"
    assert response.confidence == 0
    assert response.total_citations == 0
    assert response.citations == []