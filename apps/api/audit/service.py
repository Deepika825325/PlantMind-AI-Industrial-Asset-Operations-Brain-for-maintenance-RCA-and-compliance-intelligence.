from __future__ import annotations

from threading import RLock
from typing import Any

from apps.api.audit.schemas import (
    AuditActor,
    AuditRecord,
)
from apps.api.core.request_context import (
    get_request_id,
)

_AUDIT_LOCK = RLock()
_AUDIT_RECORDS: list[AuditRecord] = []




def actor_from_user(
    user: Any | None,
) -> AuditActor:
    if user is None:
        return AuditActor()

    if isinstance(user, dict):
        return AuditActor(
            user_id=(
                user.get("user_id")
                or user.get("id")
                or user.get("sub")
            ),
            email=user.get("email"),
            role=user.get("role"),
        )

    return AuditActor(
        user_id=(
            getattr(user, "user_id", None)
            or getattr(user, "id", None)
            or getattr(user, "sub", None)
        ),
        email=getattr(user, "email", None),
        role=getattr(user, "role", None),
    )

def _coerce_actor(
    actor: AuditActor | dict[str, Any] | None = None,
    *,
    user_id: str | None = None,
    email: str | None = None,
    role: str | None = None,
) -> AuditActor:
    if isinstance(actor, AuditActor):
        return actor

    if isinstance(actor, dict):
        return AuditActor(
            user_id=actor.get("user_id") or user_id,
            email=actor.get("email") or email,
            role=actor.get("role") or role,
        )

    return AuditActor(
        user_id=user_id,
        email=email,
        role=role,
    )


def record_audit_event(
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    actor: AuditActor | dict[str, Any] | None = None,
    outcome: str = "allowed",
    reason: str | None = None,
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
    *,
    user_id: str | None = None,
    email: str | None = None,
    role: str | None = None,
) -> AuditRecord:
    record = AuditRecord(
        request_id=request_id or get_request_id(),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor=_coerce_actor(
            actor,
            user_id=user_id,
            email=email,
            role=role,
        ),
        outcome=outcome,
        reason=reason,
        metadata=metadata or {},
        immutable=True,
    )

    with _AUDIT_LOCK:
        _AUDIT_RECORDS.append(record)

    return record


def record_audit(
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    actor: AuditActor | dict[str, Any] | None = None,
    outcome: str = "allowed",
    reason: str | None = None,
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
    *,
    user_id: str | None = None,
    email: str | None = None,
    role: str | None = None,
) -> AuditRecord:
    return record_audit_event(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
        outcome=outcome,
        reason=reason,
        metadata=metadata,
        request_id=request_id,
        user_id=user_id,
        email=email,
        role=role,
    )


def list_audit_records(
    *,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    outcome: str | None = None,
    request_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditRecord]:
    with _AUDIT_LOCK:
        records = list(_AUDIT_RECORDS)

    if action:
        records = [
            record
            for record in records
            if record.action == action
        ]

    if entity_type:
        records = [
            record
            for record in records
            if record.entity_type == entity_type
        ]

    if entity_id:
        records = [
            record
            for record in records
            if record.entity_id == entity_id
        ]

    if outcome:
        records = [
            record
            for record in records
            if record.outcome == outcome
        ]

    if request_id:
        records = [
            record
            for record in records
            if record.request_id == request_id
        ]

    records = list(
        reversed(records)
    )

    return records[
        offset : offset + limit
    ]


def list_audit_events(
    **filters: Any,
) -> list[AuditRecord]:
    return list_audit_records(**filters)


def list_entity_audit_records(
    entity_type: str,
    entity_id: str,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditRecord]:
    return list_audit_records(
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )


def clear_audit_records() -> None:
    with _AUDIT_LOCK:
        _AUDIT_RECORDS.clear()

def get_audit_log(
    **filters: Any,
) -> list[AuditRecord]:
    return list_audit_records(**filters)


def clear_audit_log() -> None:
    clear_audit_records()
