from __future__ import annotations

from pathlib import Path

from apps.api.ingestion.schemas import DocumentIngestionRequest
from apps.api.ingestion.service import (
    DocumentIngestionService,
    IngestionConfig,
)
from apps.api.rag_answering.service import IngestionRagAnsweringService
from apps.api.rag_evaluation.schemas import RagBenchmarkQuestion
from apps.api.rag_evaluation.service import RagEvaluationService
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
    RagIndexingConfig,
)


def make_evaluation_service(
    tmp_path: Path,
) -> tuple[
    DocumentIngestionService,
    IngestionRagIndexingService,
    RagEvaluationService,
]:
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

    indexing_service = IngestionRagIndexingService(
        ingestion_service=ingestion_service,
        config=RagIndexingConfig(
            index_dir=tmp_path / "rag_index",
        ),
    )

    answering_service = IngestionRagAnsweringService(
        rag_indexing_service=indexing_service,
    )

    evaluation_service = RagEvaluationService(
        rag_answering_service=answering_service,
    )

    return (
        ingestion_service,
        indexing_service,
        evaluation_service,
    )


def seed_documents(
    ingestion_service: DocumentIngestionService,
    tmp_path: Path,
) -> None:
    p101 = tmp_path / "p101-eval-note.txt"
    hx301 = tmp_path / "hx301-eval-note.txt"

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


def test_evaluation_passes_grounded_questions(
    tmp_path: Path,
) -> None:
    ingestion_service, indexing_service, evaluation_service = make_evaluation_service(
        tmp_path,
    )

    seed_documents(
        ingestion_service,
        tmp_path,
    )

    indexing_service.build_index()

    report = evaluation_service.evaluate_questions(
        [
            RagBenchmarkQuestion(
                question_id="RAG-Q-001",
                question="Why is P-101 vibration high?",
                asset_id="P-101",
                expected_terms=[
                    "vibration",
                    "bearing",
                ],
            ),
            RagBenchmarkQuestion(
                question_id="RAG-Q-002",
                question="Why is HX-301 heat transfer reduced?",
                asset_id="HX-301",
                expected_terms=[
                    "fouling",
                    "heat transfer",
                ],
            ),
        ]
    )

    assert report.evaluation_id.startswith("RAG-EVAL-")
    assert report.summary.total_questions == 2
    assert report.summary.passed_questions == 2
    assert report.summary.failed_questions == 0
    assert report.summary.pass_rate == 1.0
    assert report.summary.average_quality_score > 0
    assert all(
        result.passed
        for result in report.results
    )


def test_evaluation_fails_when_expected_terms_missing(
    tmp_path: Path,
) -> None:
    ingestion_service, indexing_service, evaluation_service = make_evaluation_service(
        tmp_path,
    )

    seed_documents(
        ingestion_service,
        tmp_path,
    )

    indexing_service.build_index()

    report = evaluation_service.evaluate_questions(
        [
            RagBenchmarkQuestion(
                question_id="RAG-Q-003",
                question="Why is P-101 vibration high?",
                asset_id="P-101",
                expected_terms=[
                    "cavitation",
                ],
            )
        ]
    )

    assert report.summary.total_questions == 1
    assert report.summary.passed_questions == 0
    assert report.summary.failed_questions == 1
    assert report.results[0].passed is False
    assert "cavitation" in report.results[0].missing_expected_terms
    assert "missing_expected_terms" in report.results[0].warnings


def test_evaluation_handles_no_context_answer(
    tmp_path: Path,
) -> None:
    ingestion_service, indexing_service, evaluation_service = make_evaluation_service(
        tmp_path,
    )

    seed_documents(
        ingestion_service,
        tmp_path,
    )

    indexing_service.build_index()

    report = evaluation_service.evaluate_questions(
        [
            RagBenchmarkQuestion(
                question_id="RAG-Q-004",
                question="Why is compressor seal leaking?",
                asset_id="C-201",
                expected_terms=[
                    "seal",
                ],
            )
        ]
    )

    assert report.summary.total_questions == 1
    assert report.summary.passed_questions == 0
    assert report.results[0].retrieval_status == "no_relevant_context"
    assert report.results[0].grounded is False