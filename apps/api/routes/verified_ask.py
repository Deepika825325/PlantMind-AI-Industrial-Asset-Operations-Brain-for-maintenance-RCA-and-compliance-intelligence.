from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission
from apps.api.hybrid_retrieval.service import HybridRetrievalService
from apps.api.verified_ask.schemas import (
    VerifiedAskRequest,
    VerifiedAskResponse,
)
from apps.api.verified_ask.service import VerifiedAskService


router = APIRouter(
    prefix="/ask-plantmind",
    tags=["ask-plantmind"],
)

hybrid_retrieval_service = HybridRetrievalService()
verified_ask_service = VerifiedAskService(
    retrieval_service=hybrid_retrieval_service,
)


@router.post(
    "/verified",
    response_model=VerifiedAskResponse,
)
def ask_plantmind_verified(
    request: VerifiedAskRequest,
    user=Depends(require_permission("document.read")),
) -> VerifiedAskResponse:
    response = verified_ask_service.answer(
        request
    )

    record_audit_event(
        action="ask_plantmind.verified_answer",
        entity_type="ask_request",
        entity_id=response.request_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="verified Ask PlantMind answer generated",
        metadata={
            "question": request.question,
            "asset_ids": request.asset_ids,
            "answer_status": response.answer_status,
            "grounded": response.grounded,
            "citations_verified": response.citations_verified,
            "confidence": response.confidence,
            "evidence_count": len(response.evidence),
            "missing_information_count": len(response.missing_information),
            "contradictory_evidence_count": len(response.contradictory_evidence),
            "unsupported_claim_count": len(response.unsupported_claims),
        },
    )

    return response