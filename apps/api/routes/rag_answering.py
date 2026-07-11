from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission
from apps.api.ingestion.service import DocumentIngestionService
from apps.api.rag_answering.schemas import (
    RagAnswerRequest,
    RagAnswerResponse,
)
from apps.api.rag_answering.service import (
    IngestionRagAnsweringService,
)
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
)

router = APIRouter(
    prefix="/rag-answering",
    tags=["rag-answering"],
)

ingestion_service = DocumentIngestionService()
rag_indexing_service = IngestionRagIndexingService(
    ingestion_service=ingestion_service,
)
rag_answering_service = IngestionRagAnsweringService(
    rag_indexing_service=rag_indexing_service,
)


@router.post(
    "/ingestion/answer",
    response_model=RagAnswerResponse,
)
def answer_from_ingested_documents(
    request: RagAnswerRequest,
    user=Depends(require_permission("model.read")),
) -> RagAnswerResponse:
    try:
        response = rag_answering_service.answer_question(
            request
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="rag_answer.generate",
        entity_type="rag_answer",
        entity_id=response.answer_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="RAG answer generated from ingested documents",
        metadata={
            "question": request.question,
            "asset_id": request.asset_id,
            "document_type": request.document_type,
            "limit": request.limit,
            "retrieval_status": response.retrieval_status,
            "total_citations": response.total_citations,
            "confidence": response.confidence,
            "grounded": response.quality.grounded,
            "quality_score": response.quality.quality_score,
            "query_coverage": response.quality.query_coverage,
            "warnings": response.quality.warnings,
        },
    )

    return response