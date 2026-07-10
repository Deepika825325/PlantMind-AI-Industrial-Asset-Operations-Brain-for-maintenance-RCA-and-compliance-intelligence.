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


def make_answering_service(
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


def test_quality_marks_grounded_answer(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-quality-note.txt"
    source.write_text(
        "P-101 vibration increased above normal range. "
        "Bearing temperature increased after the vibration event.",
        encoding="utf-8",
    )

    ingestion_service, indexing_service, answering_service = make_answering_service(
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

    assert response.quality.grounded is True
    assert response.quality.quality_score > 0
    assert response.quality.query_coverage > 0
    assert "vibration" in response.quality.matched_query_terms
    assert response.quality.warnings


def test_quality_tracks_missing_query_terms(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-partial-note.txt"
    source.write_text(
        "P-101 vibration increased above normal range.",
        encoding="utf-8",
    )

    ingestion_service, indexing_service, answering_service = make_answering_service(
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
            question="Why is P-101 vibration high with lubrication issue?",
            asset_id="P-101",
        )
    )

    assert "vibration" in response.quality.matched_query_terms
    assert "lubrication" in response.quality.missing_query_terms


def test_quality_marks_no_context_answer_as_not_grounded(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-note.txt"
    source.write_text(
        "P-101 vibration increased above normal range.",
        encoding="utf-8",
    )

    ingestion_service, indexing_service, answering_service = make_answering_service(
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

    assert response.quality.grounded is False
    assert response.quality.quality_score == 0
    assert response.quality.query_coverage == 0
    assert "no_relevant_context" in response.quality.warnings