from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


WorkOrderLifecycleStatus = Literal[
    "draft",
    "pending_approval",
    "approved",
    "assigned",
    "in_progress",
    "waiting_for_part",
    "completed",
    "verification_pending",
    "verified",
    "closed",
]

LifecycleAuditEventType = Literal[
    "transition",
    "transition_rejected",
    "approval_required",
]


class WorkOrderTransitionRequest(BaseModel):
    target_status: WorkOrderLifecycleStatus
    changed_by: str = Field(min_length=1)
    changed_at: str
    note: str | None = None
    approver_role: str | None = None
    approval_reference: str | None = None


class WorkOrderLifecycleAuditEvent(BaseModel):
    event_id: str
    work_order_id: str
    event_type: LifecycleAuditEventType
    timestamp: str
    from_status: WorkOrderLifecycleStatus
    to_status: WorkOrderLifecycleStatus
    changed_by: str
    note: str | None = None
    approval_reference: str | None = None
    approver_role: str | None = None
    explanation: str


class WorkOrderLifecycleState(BaseModel):
    work_order_id: str
    asset_id: str
    title: str
    priority: str
    risk_score: float
    high_risk: bool
    approval_required: bool
    current_status: WorkOrderLifecycleStatus
    allowed_next_statuses: list[WorkOrderLifecycleStatus]
    audit_events: list[WorkOrderLifecycleAuditEvent]


class WorkOrderTransitionResponse(BaseModel):
    work_order_id: str
    previous_status: WorkOrderLifecycleStatus
    current_status: WorkOrderLifecycleStatus
    high_risk: bool
    approval_required: bool
    audit_event: WorkOrderLifecycleAuditEvent
    allowed_next_statuses: list[WorkOrderLifecycleStatus]
    explanation: str


class WorkOrderLifecycleRulesResponse(BaseModel):
    lifecycle_order: list[WorkOrderLifecycleStatus]
    allowed_transitions: dict[WorkOrderLifecycleStatus, list[WorkOrderLifecycleStatus]]
    high_risk_threshold: float
    high_risk_priorities: list[str]
    approval_required_rule: str
    invalid_transition_rule: str


class WorkOrderLifecycleAuditResponse(BaseModel):
    work_order_id: str
    audit_event_count: int
    audit_events: list[WorkOrderLifecycleAuditEvent]