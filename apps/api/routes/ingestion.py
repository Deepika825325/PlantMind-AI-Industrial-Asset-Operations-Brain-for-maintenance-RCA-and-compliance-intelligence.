from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission
from apps.api.ingestion.schemas import (
    DocumentIngestionRequest,
    DocumentIngestionResult,
    IngestionChunkManifest,
    IngestionManifest,
    IngestionManifestListResponse,
)
from apps.api.ingestion.service import (
    DocumentIngestionService,
    IngestionValidationException,
)

router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
)

ingestion_service = DocumentIngestionService()


@router.post(
    "/documents/local-file",
    response_model=DocumentIngestionResult,
    status_code=status.HTTP_201_CREATED,
)
def ingest_local_document(
    request: DocumentIngestionRequest,
    user=Depends(require_permission("evidence.write")),
) -> DocumentIngestionResult | JSONResponse:
    try:
        result = ingestion_service.ingest_document(
            request
        )
    except FileNotFoundError as exc:
        record_audit_event(
            action="document.ingest",
            entity_type="document",
            entity_id=None,
            actor=actor_from_user(user),
            outcome="denied",
            reason="source file not found",
            metadata={
                "source_path": request.source_path,
                "document_type": request.document_type,
                "asset_ids": request.asset_ids,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except IngestionValidationException as exc:
        validation_errors = [
            error.model_dump()
            for error in exc.errors
        ]

        record_audit_event(
            action="document.ingest",
            entity_type="document",
            entity_id=None,
            actor=actor_from_user(user),
            outcome="denied",
            reason="document validation failed",
            metadata={
                "source_path": request.source_path,
                "document_type": request.document_type,
                "asset_ids": request.asset_ids,
                "validation_errors": validation_errors,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": {
                    "message": "Document validation failed",
                    "errors": validation_errors,
                }
            },
        )
    except ValueError as exc:
        record_audit_event(
            action="document.ingest",
            entity_type="document",
            entity_id=None,
            actor=actor_from_user(user),
            outcome="denied",
            reason="invalid source path",
            metadata={
                "source_path": request.source_path,
                "document_type": request.document_type,
                "asset_ids": request.asset_ids,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="document.ingest",
        entity_type="document",
        entity_id=result.document_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="document ingestion completed",
        metadata={
            "status": result.status,
            "source_filename": result.source_filename,
            "document_type": result.document_type,
            "asset_ids": result.asset_ids,
            "text_extract_status": result.text_extract_status,
            "lifecycle_status": result.lifecycle_status,
            "processing_status": result.processing_status,
            "revision_group_id": result.revision_group_id,
            "revision_number": result.revision_number,
            "is_duplicate": result.is_duplicate,
        },
    )

    return result


@router.get(
    "/documents",
    response_model=IngestionManifestListResponse,
)
def list_ingested_documents(
    user=Depends(require_permission("document.read")),
) -> IngestionManifestListResponse:
    documents = ingestion_service.list_manifests()

    record_audit_event(
        action="document.ingestion_registry.read",
        entity_type="ingestion_registry",
        entity_id="documents",
        actor=actor_from_user(user),
        outcome="allowed",
        reason="ingestion registry listed",
        metadata={
            "total": len(documents),
        },
    )

    return IngestionManifestListResponse(
        total=len(documents),
        documents=documents,
    )


@router.get(
    "/documents/{document_id}",
    response_model=IngestionManifest,
)
def get_ingested_document(
    document_id: str,
    user=Depends(require_permission("document.read")),
) -> IngestionManifest:
    try:
        manifest = ingestion_service.load_manifest(
            document_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="document.ingestion_manifest.read",
        entity_type="document",
        entity_id=document_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="ingestion manifest read",
    )

    return manifest


@router.get(
    "/documents/{document_id}/chunks",
    response_model=IngestionChunkManifest,
)
def get_ingested_document_chunks(
    document_id: str,
    user=Depends(require_permission("document.read")),
) -> IngestionChunkManifest:
    try:
        chunk_manifest = ingestion_service.load_chunk_manifest(
            document_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="document.ingestion_chunks.read",
        entity_type="document",
        entity_id=document_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="ingestion chunks read",
        metadata={
            "total_chunks": chunk_manifest.total_chunks,
        },
    )

    return chunk_manifest