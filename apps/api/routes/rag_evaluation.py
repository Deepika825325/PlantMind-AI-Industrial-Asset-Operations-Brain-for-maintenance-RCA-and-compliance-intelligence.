from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission
from apps.api.ingestion.service import DocumentIngestionService
from apps.api.rag_answering.service import IngestionRagAnsweringService
from apps.api.rag_evaluation.schemas import (
    RagEvaluationReport,
    RagEvaluationRequest,
)
from apps.api.rag_evaluation.service import RagEvaluationService
from apps.api.rag_indexing.service import IngestionRagIndexingService

router = APIRouter(
    prefix="/rag-evaluation",
    tags=["rag-evaluation"],
)

ingestion_service = DocumentIngestionService()
rag_indexing_service = IngestionRagIndexingService(
    ingestion_service=ingestion_service,
)
rag_answering_service = IngestionRagAnsweringService(
    rag_indexing_service=rag_indexing_service,
)
rag_evaluation_service = RagEvaluationService(
    rag_answering_service=rag_answering_service,
)


@router.post(
    "/ingestion/run",
    response_model=RagEvaluationReport,
)
def run_ingestion_rag_evaluation(
    request: RagEvaluationRequest,
    user=Depends(require_permission("model.read")),
) -> RagEvaluationReport:
    try:
        report = rag_evaluation_service.evaluate_questions(
            request.questions
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="rag_evaluation.run",
        entity_type="rag_evaluation",
        entity_id=report.evaluation_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="RAG evaluation benchmark executed",
        metadata={
            "total_questions": report.summary.total_questions,
            "passed_questions": report.summary.passed_questions,
            "failed_questions": report.summary.failed_questions,
            "pass_rate": report.summary.pass_rate,
            "average_quality_score": report.summary.average_quality_score,
            "average_query_coverage": report.summary.average_query_coverage,
        },
    )

    return report