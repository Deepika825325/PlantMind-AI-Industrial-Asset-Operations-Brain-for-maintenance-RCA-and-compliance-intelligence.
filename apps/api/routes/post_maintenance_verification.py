from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.api.auth.dependencies import require_permission
from apps.api.post_maintenance_verification.schemas import (
    MaintenanceRecoveryReplayRequest,
    PostMaintenanceVerificationHistoryResponse,
    PostMaintenanceVerificationRequest,
    PostMaintenanceVerificationResult,
    VerificationCriteriaResponse,
)
from apps.api.post_maintenance_verification.service import (
    PostMaintenanceVerificationService,
)


router = APIRouter(
    prefix="/maintenance",
    tags=["post-maintenance-verification"],
)

post_maintenance_verification_service = PostMaintenanceVerificationService()


@router.get(
    "/post-maintenance-verification/criteria",
    response_model=VerificationCriteriaResponse,
)
def get_post_maintenance_verification_criteria(
    user=Depends(require_permission("document.read")),
) -> VerificationCriteriaResponse:
    return post_maintenance_verification_service.criteria()


@router.post(
    "/work-orders/{work_order_id}/post-maintenance-verification",
    response_model=PostMaintenanceVerificationResult,
)
def verify_post_maintenance_outcome(
    work_order_id: str,
    request: PostMaintenanceVerificationRequest,
    user=Depends(require_permission("evidence.write")),
) -> PostMaintenanceVerificationResult:
    if request.work_order_id != work_order_id:
        raise HTTPException(
            status_code=400,
            detail="Path work_order_id must match request work_order_id.",
        )

    return post_maintenance_verification_service.verify(
        request
    )


@router.post(
    "/work-orders/{work_order_id}/post-maintenance-verification/replay",
    response_model=PostMaintenanceVerificationResult,
)
def replay_post_maintenance_recovery(
    work_order_id: str,
    request: MaintenanceRecoveryReplayRequest,
    user=Depends(require_permission("evidence.write")),
) -> PostMaintenanceVerificationResult:
    if request.work_order_id != work_order_id:
        raise HTTPException(
            status_code=400,
            detail="Path work_order_id must match request work_order_id.",
        )

    return post_maintenance_verification_service.replay_recovery(
        request
    )


@router.get(
    "/work-orders/{work_order_id}/post-maintenance-verification/history",
    response_model=PostMaintenanceVerificationHistoryResponse,
)
def get_post_maintenance_verification_history(
    work_order_id: str,
    user=Depends(require_permission("document.read")),
) -> PostMaintenanceVerificationHistoryResponse:
    return post_maintenance_verification_service.history(
        work_order_id
    )