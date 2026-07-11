from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.auth.dependencies import require_permission
from apps.api.rca_orchestration.schemas import (
    ControlledRcaHistoryResponse,
    ControlledRcaRequest,
    ControlledRcaResponse,
    RcaApprovalRequest,
    RcaApprovalResponse,
)
from apps.api.rca_orchestration.service import ControlledRcaOrchestrationService


router = APIRouter(
    prefix="/rca-orchestration",
    tags=["rca-orchestration"],
)

controlled_rca_service = ControlledRcaOrchestrationService()


@router.post(
    "/run",
    response_model=ControlledRcaResponse,
)
def run_controlled_rca(
    request: ControlledRcaRequest,
    user=Depends(require_permission("evidence.write")),
) -> ControlledRcaResponse:
    return controlled_rca_service.run(
        request
    )


@router.post(
    "/approval",
    response_model=RcaApprovalResponse,
)
def approve_controlled_rca(
    request: RcaApprovalRequest,
    user=Depends(require_permission("evidence.write")),
) -> RcaApprovalResponse:
    return controlled_rca_service.approve(
        request
    )


@router.get(
    "/cases/{rca_case_id}/history",
    response_model=ControlledRcaHistoryResponse,
)
def get_controlled_rca_history(
    rca_case_id: str,
    user=Depends(require_permission("document.read")),
) -> ControlledRcaHistoryResponse:
    return controlled_rca_service.history(
        rca_case_id
    )