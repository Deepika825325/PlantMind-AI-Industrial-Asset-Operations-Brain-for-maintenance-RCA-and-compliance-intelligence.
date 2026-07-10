from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from apps.api.audit.schemas import AuditLogResponse
from apps.api.audit.service import (
    actor_from_user,
    list_audit_events,
    list_audit_records,
    list_entity_audit_records,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.get(
    "/records",
    response_model=AuditLogResponse,
)
def get_audit_records(
    user=Depends(require_permission("system.admin")),
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    outcome: str | None = None,
    request_id: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AuditLogResponse:
    record_audit_event(
        action="audit.read",
        entity_type="audit_log",
        entity_id="records",
        actor=actor_from_user(user),
        outcome="allowed",
        reason="audit records read",
    )

    records = list_audit_records(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        outcome=outcome,
        request_id=request_id,
        limit=limit,
        offset=offset,
    )

    return AuditLogResponse(
        total=len(records),
        records=records,
    )


@router.get(
    "/events",
    response_model=AuditLogResponse,
)
def get_audit_events(
    user=Depends(require_permission("system.admin")),
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    outcome: str | None = None,
    request_id: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AuditLogResponse:
    record_audit_event(
        action="audit.read",
        entity_type="audit_log",
        entity_id="events",
        actor=actor_from_user(user),
        outcome="allowed",
        reason="audit events read",
    )

    records = list_audit_events(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        outcome=outcome,
        request_id=request_id,
        limit=limit,
        offset=offset,
    )

    return AuditLogResponse(
        total=len(records),
        records=records,
    )


@router.get(
    "/entities/{entity_type}/{entity_id}",
    response_model=AuditLogResponse,
)
def get_entity_audit_records(
    entity_type: str,
    entity_id: str,
    user=Depends(require_permission("system.admin")),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AuditLogResponse:
    record_audit_event(
        action="audit.read",
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="entity audit records read",
    )

    records = list_entity_audit_records(
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )

    return AuditLogResponse(
        total=len(records),
        records=records,
    )