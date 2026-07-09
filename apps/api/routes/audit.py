from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from apps.api.audit.schemas import (
    AuditLogResponse,
)
from apps.api.audit.service import (
    list_audit_records,
)
from apps.api.auth.dependencies import (
    require_permission,
)
from apps.api.auth.rbac import (
    Permission,
)


router = APIRouter(
    prefix="/audit",
    tags=["Audit Trail"],
)


@router.get(
    "/records",
    response_model=AuditLogResponse,
)
def get_audit_records(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    _current_user: dict = Depends(
        require_permission(
            Permission.SYSTEM_ADMIN
        )
    ),
) -> AuditLogResponse:
    records = list_audit_records(
        limit=limit
    )

    return AuditLogResponse(
        total=len(records),
        records=records,
    )
