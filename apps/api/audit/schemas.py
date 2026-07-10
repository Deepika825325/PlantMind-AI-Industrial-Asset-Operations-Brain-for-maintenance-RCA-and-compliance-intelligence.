from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AuditActor(BaseModel):
    user_id: str | None = None
    email: str | None = None
    role: str | None = None


class AuditRecord(BaseModel):
    audit_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    request_id: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    outcome: str
    actor: AuditActor
    reason: str | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict
    )
    immutable: bool = True
    created_at: str = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )


class AuditLogResponse(BaseModel):
    total: int
    records: list[AuditRecord]