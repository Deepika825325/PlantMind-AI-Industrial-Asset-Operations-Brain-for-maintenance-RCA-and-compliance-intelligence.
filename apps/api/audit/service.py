from __future__ import annotations

from collections import deque
from typing import Any

from apps.api.audit.schemas import (
    AuditActor,
    AuditRecord,
)


MAX_AUDIT_RECORDS = 1000

_AUDIT_LOG: deque[AuditRecord] = deque(
    maxlen=MAX_AUDIT_RECORDS
)


def actor_from_user(
    user: dict[str, Any] | None,
) -> AuditActor:
    if not user:
        return AuditActor()

    return AuditActor(
        user_id=user.get("user_id"),
        email=user.get("email"),
        role=user.get("role"),
    )


def record_audit_event(
    *,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    outcome: str,
    actor: AuditActor | None = None,
    reason: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditRecord:
    record = AuditRecord(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        outcome=outcome,
        actor=actor or AuditActor(),
        reason=reason,
        metadata=metadata or {},
    )

    _AUDIT_LOG.appendleft(record)

    return record


def list_audit_records(
    *,
    limit: int = 100,
) -> list[AuditRecord]:
    safe_limit = max(
        1,
        min(limit, MAX_AUDIT_RECORDS),
    )

    return list(_AUDIT_LOG)[:safe_limit]


def clear_audit_log() -> None:
    _AUDIT_LOG.clear()
