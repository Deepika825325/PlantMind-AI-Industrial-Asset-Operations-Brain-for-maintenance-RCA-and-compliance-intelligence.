from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission
from apps.api.hybrid_retrieval.schemas import (
    HybridRetrievalIndexRequest,
    HybridRetrievalIndexResult,
    HybridRetrievalSearchRequest,
    HybridRetrievalSearchResponse,
)
from apps.api.hybrid_retrieval.service import HybridRetrievalService


router = APIRouter(
    prefix="/hybrid-retrieval",
    tags=["hybrid-retrieval"],
)

hybrid_retrieval_service = HybridRetrievalService()


@router.post(
    "/index",
    response_model=HybridRetrievalIndexResult,
)
def build_hybrid_retrieval_index(
    request: HybridRetrievalIndexRequest,
    user=Depends(require_permission("document.read")),
) -> HybridRetrievalIndexResult:
    result = hybrid_retrieval_service.build_index(
        collection_name=request.collection_name,
        rebuild=request.rebuild,
    )

    record_audit_event(
        action="retrieval.hybrid_index.build",
        entity_type="retrieval_collection",
        entity_id=result.collection_name,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="hybrid retrieval index built",
        metadata={
            "collection_name": result.collection_name,
            "total_points": result.total_points,
            "indexed_document_ids": result.indexed_document_ids,
        },
    )

    return result


@router.post(
    "/search",
    response_model=HybridRetrievalSearchResponse,
)
def search_hybrid_retrieval(
    request: HybridRetrievalSearchRequest,
    user=Depends(require_permission("document.read")),
) -> HybridRetrievalSearchResponse:
    response = hybrid_retrieval_service.search(
        request,
    )

    record_audit_event(
        action="retrieval.hybrid_search.run",
        entity_type="retrieval_query",
        entity_id="hybrid-search",
        actor=actor_from_user(user),
        outcome="allowed",
        reason="hybrid retrieval search executed",
        metadata={
            "query": request.query,
            "mode": request.mode,
            "asset_ids": request.asset_ids,
            "document_status": request.document_status,
            "include_obsolete": request.include_obsolete,
            "revision": request.revision,
            "top_k": request.top_k,
            "total_hits": response.total_hits,
        },
    )

    return response