from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.api.auth.dependencies import require_permission
from apps.api.work_order_lifecycle.schemas import (
    WorkOrderLifecycleAuditResponse,
    WorkOrderLifecycleRulesResponse,
    WorkOrderLifecycleState,
    WorkOrderTransitionRequest,
    WorkOrderTransitionResponse,
)
from apps.api.work_order_lifecycle.service import (
    GovernedWorkOrderLifecycleService,
    WorkOrderLifecycleConflictError,
    WorkOrderNotFoundError,
)


router = APIRouter(
    prefix="/maintenance",
    tags=["work-order-lifecycle"],
)

work_order_lifecycle_service = GovernedWorkOrderLifecycleService()


@router.get(
    "/work-order-lifecycle/rules",
    response_model=WorkOrderLifecycleRulesResponse,
)
def get_work_order_lifecycle_rules(
    user=Depends(require_permission("document.read")),
) -> WorkOrderLifecycleRulesResponse:
    return work_order_lifecycle_service.rules()


@router.get(
    "/work-orders/{work_order_id}/lifecycle",
    response_model=WorkOrderLifecycleState,
)
def get_work_order_lifecycle_state(
    work_order_id: str,
    user=Depends(require_permission("document.read")),
) -> WorkOrderLifecycleState:
    try:
        return work_order_lifecycle_service.get_state(
            work_order_id
        )
    except WorkOrderNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/work-orders/{work_order_id}/lifecycle/audit",
    response_model=WorkOrderLifecycleAuditResponse,
)
def get_work_order_lifecycle_audit(
    work_order_id: str,
    user=Depends(require_permission("document.read")),
) -> WorkOrderLifecycleAuditResponse:
    try:
        return work_order_lifecycle_service.audit(
            work_order_id
        )
    except WorkOrderNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/work-orders/{work_order_id}/lifecycle/transition",
    response_model=WorkOrderTransitionResponse,
)
def transition_work_order_lifecycle(
    work_order_id: str,
    request: WorkOrderTransitionRequest,
    user=Depends(require_permission("evidence.write")),
) -> WorkOrderTransitionResponse:
    try:
        return work_order_lifecycle_service.transition(
            work_order_id=work_order_id,
            request=request,
        )
    except WorkOrderNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except WorkOrderLifecycleConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=exc.message,
        ) from exc