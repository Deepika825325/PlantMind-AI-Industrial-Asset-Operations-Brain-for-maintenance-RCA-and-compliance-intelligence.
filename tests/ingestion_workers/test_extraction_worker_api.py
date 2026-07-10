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
from apps.api.ingestion_workers.service import (
    DocumentExtractionWorkerService,
    ExtractionWorkerConfig,
)
from apps.api.main import app
from apps.api.routes import ingestion_workers as worker_route


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        worker_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_worker_user(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "test-engineer",
        "email": "engineer@plantmind.local",
        "role": "maintenance_engineer",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_worker_service(
    tmp_path: Path,
) -> Iterator[
    tuple[
        DocumentIngestionService,
        DocumentExtractionWorkerService,
    ]
]:
    original_service = worker_route.extraction_worker_service

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

    worker_route.extraction_worker_service = worker_service

    try:
        yield ingestion_service, worker_service
    finally:
        worker_route.extraction_worker_service = original_service


def test_start_extraction_worker_job_api(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-worker-api-note.txt"
    source.write_text(
        "P-101 INSPECTION\n"
        "P-101 vibration increased near the bearing.\f"
        "FOLLOW UP\n"
        "P-101 lubrication evidence is missing.",
        encoding="utf-8",
    )

    with isolated_worker_service(tmp_path) as (
        ingestion_service,
        _worker_service,
    ):
        ingestion = ingestion_service.ingest_document(
            DocumentIngestionRequest(
                source_path=str(source),
                asset_ids=["P-101"],
                document_type="inspection_note",
            )
        )

        with authorized_worker_user(
            "start_extraction_job"
        ):
            response = client.post(
                "/ingestion-workers/extraction/jobs",
                json={
                    "document_id": ingestion.document_id,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "completed"
    assert payload["document_id"] == ingestion.document_id
    assert payload["total_pages"] == 2
    assert payload["total_chunks"] >= 2
    assert "P-101" in payload["detected_asset_ids"]
    assert payload["parser"]["parser_version"] == "1.0.0"


def test_get_extraction_worker_job_api(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-worker-api-note.txt"
    source.write_text(
        "P-101 vibration increased near the bearing.",
        encoding="utf-8",
    )

    with isolated_worker_service(tmp_path) as (
        ingestion_service,
        worker_service,
    ):
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

        with authorized_worker_user(
            "get_extraction_job"
        ):
            response = client.get(
                f"/ingestion-workers/extraction/jobs/{job.job_id}"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["job_id"] == job.job_id
    assert payload["status"] == "completed"


def test_retry_failed_extraction_worker_job_api(
    tmp_path: Path,
) -> None:
    with isolated_worker_service(tmp_path) as (
        _ingestion_service,
        worker_service,
    ):
        failed_job = worker_service.run_extraction_job(
            "DOC-ING-MISSING",
        )

        with authorized_worker_user(
            "retry_extraction_job"
        ):
            response = client.post(
                f"/ingestion-workers/extraction/jobs/{failed_job.job_id}/retry"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "failed"
    assert payload["attempts"] == 2
    assert payload["errors"]


def test_start_extraction_worker_job_requires_authentication() -> None:
    response = client.post(
        "/ingestion-workers/extraction/jobs",
        json={
            "document_id": "DOC-ING-TEST",
        },
    )

    assert response.status_code == 401