from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission
from apps.api.ingestion.service import DocumentIngestionService
from apps.api.rag_indexing.schemas import (
    RagIndexBuildResult,
    RagIndexManifest,
    RagIndexedChunkListResponse,
    RagSearchRequest,
    RagSearchResponse,
)
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
)

router = APIRouter(
    prefix="/rag-indexing",
    tags=["rag-indexing"],
)

ingestion_service = DocumentIngestionService()
rag_indexing_service = IngestionRagIndexingService(
    ingestion_service=ingestion_service,
)


@router.post(
    "/ingestion/build",
    response_model=RagIndexBuildResult,
)
def build_ingestion_rag_index(
    user=Depends(require_permission("model.read")),
) -> RagIndexBuildResult:
    result = rag_indexing_service.build_index()

    record_audit_event(
        action="rag_index.build",
        entity_type="rag_index",
        entity_id=result.index_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="ingestion chunks indexed for RAG",
        metadata={
            "total_documents": result.total_documents,
            "total_chunks": result.total_chunks,
            "index_path": result.index_path,
        },
    )

    return result


@router.get(
    "/ingestion/manifest",
    response_model=RagIndexManifest,
)
def get_ingestion_rag_index_manifest(
    user=Depends(require_permission("model.read")),
) -> RagIndexManifest:
    try:
        manifest = rag_indexing_service.load_manifest()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="rag_index.manifest.read",
        entity_type="rag_index",
        entity_id=manifest.index_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="RAG index manifest read",
    )

    return manifest


@router.get(
    "/ingestion/chunks",
    response_model=RagIndexedChunkListResponse,
)
def list_ingestion_rag_index_chunks(
    user=Depends(require_permission("model.read")),
) -> RagIndexedChunkListResponse:
    try:
        chunks = rag_indexing_service.load_index()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="rag_index.chunks.read",
        entity_type="rag_index",
        entity_id="ingestion_chunks",
        actor=actor_from_user(user),
        outcome="allowed",
        reason="RAG indexed chunks listed",
        metadata={
            "total": len(chunks),
        },
    )

    return RagIndexedChunkListResponse(
        total=len(chunks),
        chunks=chunks,
    )


@router.post(
    "/ingestion/search",
    response_model=RagSearchResponse,
)
def search_ingestion_rag_index(
    request: RagSearchRequest,
    user=Depends(require_permission("model.read")),
) -> RagSearchResponse:
    try:
        response = rag_indexing_service.search_index(
            query=request.query,
            asset_id=request.asset_id,
            document_type=request.document_type,
            limit=request.limit,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="rag_index.search",
        entity_type="rag_index",
        entity_id="ingestion_chunks",
        actor=actor_from_user(user),
        outcome="allowed",
        reason="RAG index searched",
        metadata={
            "query": request.query,
            "asset_id": request.asset_id,
            "document_type": request.document_type,
            "limit": request.limit,
            "hits": response.total,
        },
    )

    return response