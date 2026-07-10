from __future__ import annotations

from pathlib import Path

from apps.api.ingestion.schemas import DocumentIngestionRequest
from apps.api.ingestion.service import (
    DocumentIngestionService,
    IngestionConfig,
)
from apps.api.ingestion_workers.service import (
    DocumentExtractionWorkerService,
    ExtractionWorkerConfig,
)


def make_services(
    tmp_path: Path,
) -> tuple[
    DocumentIngestionService,
    DocumentExtractionWorkerService,
]:
    ingestion_service = DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
            chunks_dir=tmp_path / "chunks",
        )
    )

    worker_service = DocumentExtractionWorkerService(
        ingestion_service=ingestion_service,
        config=ExtractionWorkerConfig(
            jobs_dir=tmp_path / "worker_jobs",
            extracted_dir=tmp_path / "extracted",
            failure_log_path=tmp_path / "worker_failures.jsonl",
            chunk_size_chars=120,
            chunk_overlap_chars=10,
        ),
    )

    return ingestion_service, worker_service


def test_worker_creates_page_aware_chunks_and_links_assets(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-worker-note.txt"
    source.write_text(
        "P-101 INSPECTION\n"
        "P-101 vibration increased near the bearing.\f"
        "FOLLOW UP\n"
        "P-101 lubrication evidence is missing.",
        encoding="utf-8",
    )

    ingestion_service, worker_service = make_services(
        tmp_path,
    )

    ingestion = ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    job = worker_service.run_extraction_job(
        ingestion.document_id,
    )

    assert job.status == "completed"
    assert job.parser.parser_version == "1.0.0"
    assert job.total_pages == 2
    assert job.total_chunks >= 2
    assert "P-101" in job.detected_asset_ids
    assert all(
        chunk.page_number in {1, 2}
        for chunk in job.chunks
    )
    assert any(
        "P-101" in chunk.asset_ids
        for chunk in job.chunks
    )


def test_worker_detects_headings_tables_and_parser_metadata(
    tmp_path: Path,
) -> None:
    source = tmp_path / "hx301-worker-note.txt"
    source.write_text(
        "# HX-301 Fouling Review\n"
        "HX-301 fouling reduced heat transfer efficiency.\n"
        "| Metric | Value |\n"
        "| Delta T | Low |\n",
        encoding="utf-8",
    )

    ingestion_service, worker_service = make_services(
        tmp_path,
    )

    ingestion = ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["HX-301"],
            document_type="inspection_note",
        )
    )

    job = worker_service.run_extraction_job(
        ingestion.document_id,
    )

    assert job.status == "completed"
    assert job.parser.parser_name == "plantmind_page_aware_extraction_worker"
    assert job.parser.parser_mode == "page_aware_local_worker"
    assert job.headings[0].heading_text == "HX-301 Fouling Review"
    assert job.tables
    assert job.tables[0].rows[0] == ["Metric", "Value"]


def test_failed_worker_job_can_be_retried_and_failure_is_logged(
    tmp_path: Path,
) -> None:
    ingestion_service, worker_service = make_services(
        tmp_path,
    )

    failed_job = worker_service.run_extraction_job(
        "DOC-ING-MISSING",
    )

    assert failed_job.status == "failed"
    assert failed_job.attempts == 1
    assert failed_job.errors
    assert worker_service.config.failure_log_path.exists()

    retried_job = worker_service.retry_job(
        failed_job.job_id,
    )

    assert retried_job.status == "failed"
    assert retried_job.attempts == 2
    assert retried_job.errors

    failure_log = worker_service.config.failure_log_path.read_text(
        encoding="utf-8",
    )

    assert failed_job.job_id in failure_log
    assert "DOC-ING-MISSING" in failure_log