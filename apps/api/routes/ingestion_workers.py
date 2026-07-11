from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission
from apps.api.ingestion.service import DocumentIngestionService
from apps.api.ingestion_workers.schemas import (
    ExtractionJobRequest,
    ExtractionWorkerJob,
)
from apps.api.ingestion_workers.service import (
    DocumentExtractionWorkerService,
)

router = APIRouter(
    prefix="/ingestion-workers",
    tags=["ingestion-workers"],
)

ingestion_service = DocumentIngestionService()
extraction_worker_service = DocumentExtractionWorkerService(
    ingestion_service=ingestion_service,
)


@router.post(
    "/extraction/jobs",
    response_model=ExtractionWorkerJob,
)
def start_extraction_job(
    request: ExtractionJobRequest,
    user=Depends(require_permission("evidence.write")),
) -> ExtractionWorkerJob:
    job = extraction_worker_service.run_extraction_job(
        request.document_id
    )

    record_audit_event(
        action="document.extraction_worker.run",
        entity_type="extraction_job",
        entity_id=job.job_id,
        actor=actor_from_user(user),
        outcome="allowed" if job.status != "failed" else "denied",
        reason="document extraction worker executed",
        metadata={
            "document_id": job.document_id,
            "status": job.status,
            "attempts": job.attempts,
            "parser_name": job.parser.parser_name,
            "parser_version": job.parser.parser_version,
            "total_pages": job.total_pages,
            "total_chunks": job.total_chunks,
            "detected_asset_ids": job.detected_asset_ids,
            "error_count": len(job.errors),
        },
    )

    return job


@router.get(
    "/extraction/jobs/{job_id}",
    response_model=ExtractionWorkerJob,
)
def get_extraction_job(
    job_id: str,
    user=Depends(require_permission("document.read")),
) -> ExtractionWorkerJob:
    try:
        job = extraction_worker_service.load_job(
            job_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="document.extraction_worker.read",
        entity_type="extraction_job",
        entity_id=job.job_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="document extraction worker job read",
        metadata={
            "document_id": job.document_id,
            "status": job.status,
            "attempts": job.attempts,
        },
    )

    return job


@router.post(
    "/extraction/jobs/{job_id}/retry",
    response_model=ExtractionWorkerJob,
)
def retry_extraction_job(
    job_id: str,
    user=Depends(require_permission("evidence.write")),
) -> ExtractionWorkerJob:
    try:
        job = extraction_worker_service.retry_job(
            job_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="document.extraction_worker.retry",
        entity_type="extraction_job",
        entity_id=job.job_id,
        actor=actor_from_user(user),
        outcome="allowed" if job.status != "failed" else "denied",
        reason="document extraction worker job retried",
        metadata={
            "document_id": job.document_id,
            "status": job.status,
            "attempts": job.attempts,
            "error_count": len(job.errors),
        },
    )

    return job