from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps.api.work_order_lifecycle.schemas import (
    WorkOrderLifecycleAuditEvent,
    WorkOrderLifecycleAuditResponse,
    WorkOrderLifecycleRulesResponse,
    WorkOrderLifecycleState,
    WorkOrderTransitionRequest,
    WorkOrderTransitionResponse,
)


ALLOWED_TRANSITIONS = {
    "draft": [
        "pending_approval",
    ],
    "pending_approval": [
        "approved",
    ],
    "approved": [
        "assigned",
    ],
    "assigned": [
        "in_progress",
    ],
    "in_progress": [
        "waiting_for_part",
        "completed",
    ],
    "waiting_for_part": [
        "in_progress",
    ],
    "completed": [
        "verification_pending",
    ],
    "verification_pending": [
        "verified",
        "in_progress",
    ],
    "verified": [
        "closed",
    ],
    "closed": [],
}

LIFECYCLE_ORDER = [
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

HIGH_RISK_THRESHOLD = 75.0
HIGH_RISK_PRIORITIES = [
    "high",
    "critical",
]


class WorkOrderNotFoundError(Exception):
    pass


class WorkOrderLifecycleConflictError(Exception):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message
        )
        self.message = message


class GovernedWorkOrderLifecycleService:
    def __init__(
        self,
        work_order_path: Path | None = None,
    ) -> None:
        self.work_order_path = work_order_path or Path(
            "data/demo/maintenance_work_orders.json"
        )
        self._work_orders_by_id = self._load_work_orders()
        self._current_status_by_id: dict[
            str,
            str,
        ] = {}
        self._audit_events_by_id: dict[
            str,
            list[WorkOrderLifecycleAuditEvent],
        ] = {}

    def rules(
        self,
    ) -> WorkOrderLifecycleRulesResponse:
        return WorkOrderLifecycleRulesResponse(
            lifecycle_order=LIFECYCLE_ORDER,
            allowed_transitions=ALLOWED_TRANSITIONS,
            high_risk_threshold=HIGH_RISK_THRESHOLD,
            high_risk_priorities=HIGH_RISK_PRIORITIES,
            approval_required_rule=(
                "High-risk work orders require approval_reference and "
                "approver_role before moving from pending_approval to approved."
            ),
            invalid_transition_rule=(
                "A work order can only move to one of its allowed next statuses. "
                "Completed cannot directly become closed; it must move through "
                "verification_pending and verified first."
            ),
        )

    def get_state(
        self,
        work_order_id: str,
    ) -> WorkOrderLifecycleState:
        work_order = self._get_work_order(
            work_order_id
        )

        current_status = self._current_status_by_id.get(
            work_order_id,
            self._initial_status(
                work_order
            ),
        )

        return WorkOrderLifecycleState(
            work_order_id=work_order_id,
            asset_id=str(
                work_order.get(
                    "asset_id",
                    "UNKNOWN",
                )
            ),
            title=str(
                work_order.get(
                    "title",
                    "Untitled work order",
                )
            ),
            priority=str(
                work_order.get(
                    "priority",
                    "medium",
                )
            ),
            risk_score=self._risk_score(
                work_order
            ),
            high_risk=self._is_high_risk(
                work_order
            ),
            approval_required=self._approval_required(
                work_order=work_order,
                current_status=current_status,
            ),
            current_status=current_status,
            allowed_next_statuses=ALLOWED_TRANSITIONS[
                current_status
            ],
            audit_events=self._audit_events_by_id.get(
                work_order_id,
                [],
            ),
        )

    def transition(
        self,
        *,
        work_order_id: str,
        request: WorkOrderTransitionRequest,
    ) -> WorkOrderTransitionResponse:
        work_order = self._get_work_order(
            work_order_id
        )

        current_status = self._current_status_by_id.get(
            work_order_id,
            self._initial_status(
                work_order
            ),
        )

        allowed_next = ALLOWED_TRANSITIONS[
            current_status
        ]

        if request.target_status not in allowed_next:
            self._record_rejected_transition(
                work_order_id=work_order_id,
                from_status=current_status,
                request=request,
                reason=self._invalid_transition_message(
                    current_status=current_status,
                    target_status=request.target_status,
                ),
            )

            raise WorkOrderLifecycleConflictError(
                self._invalid_transition_message(
                    current_status=current_status,
                    target_status=request.target_status,
                )
            )

        if self._requires_approval(
            work_order=work_order,
            current_status=current_status,
            target_status=request.target_status,
        ) and not (
            request.approval_reference
            and request.approver_role
        ):
            reason = (
                "High-risk work order requires approval_reference and "
                "approver_role before it can move to approved."
            )

            self._record_rejected_transition(
                work_order_id=work_order_id,
                from_status=current_status,
                request=request,
                reason=reason,
            )

            raise WorkOrderLifecycleConflictError(
                reason
            )

        if self._requires_successful_verification(
            current_status=current_status,
            target_status=request.target_status,
        ) and not (
            request.verification_reference
            and request.verification_outcome == "successful"
        ):
            reason = (
                "Work order can enter verified only after successful "
                "post-maintenance verification with verification_reference."
            )

            self._record_rejected_transition(
                work_order_id=work_order_id,
                from_status=current_status,
                request=request,
                reason=reason,
            )

            raise WorkOrderLifecycleConflictError(
                reason
            )

        if self._requires_failed_recovery_for_reopen(
            current_status=current_status,
            target_status=request.target_status,
        ) and not (
            request.verification_reference
            and request.verification_outcome == "failed"
        ):
            reason = (
                "Verification-pending work order can reopen to in_progress "
                "only after failed post-maintenance verification."
            )

            self._record_rejected_transition(
                work_order_id=work_order_id,
                from_status=current_status,
                request=request,
                reason=reason,
            )

            raise WorkOrderLifecycleConflictError(
                reason
            )

        audit_event = self._audit_event(
            work_order_id=work_order_id,
            event_type="transition",
            timestamp=request.changed_at,
            from_status=current_status,
            to_status=request.target_status,
            changed_by=request.changed_by,
            note=request.note,
            approval_reference=request.approval_reference,
            approver_role=request.approver_role,
            verification_reference=request.verification_reference,
            verification_outcome=request.verification_outcome,
            explanation=(
                f"Work order moved from {current_status} to "
                f"{request.target_status} through governed transition "
                "validation."
            ),
        )

        self._audit_events_by_id.setdefault(
            work_order_id,
            [],
        ).append(
            audit_event
        )

        self._current_status_by_id[
            work_order_id
        ] = request.target_status

        return WorkOrderTransitionResponse(
            work_order_id=work_order_id,
            previous_status=current_status,
            current_status=request.target_status,
            high_risk=self._is_high_risk(
                work_order
            ),
            approval_required=self._approval_required(
                work_order=work_order,
                current_status=request.target_status,
            ),
            audit_event=audit_event,
            allowed_next_statuses=ALLOWED_TRANSITIONS[
                request.target_status
            ],
            explanation=(
                "Transition accepted. Audit event created and lifecycle "
                "state updated."
            ),
        )

    def audit(
        self,
        work_order_id: str,
    ) -> WorkOrderLifecycleAuditResponse:
        self._get_work_order(
            work_order_id
        )

        events = self._audit_events_by_id.get(
            work_order_id,
            [],
        )

        return WorkOrderLifecycleAuditResponse(
            work_order_id=work_order_id,
            audit_event_count=len(events),
            audit_events=events,
        )

    def _load_work_orders(
        self,
    ) -> dict[str, dict[str, Any]]:
        if not self.work_order_path.exists():
            return {}

        raw = json.loads(
            self.work_order_path.read_text(
                encoding="utf-8-sig"
            )
        )

        if isinstance(
            raw,
            list,
        ):
            items = raw
        elif isinstance(
            raw,
            dict,
        ):
            items = (
                raw.get(
                    "work_orders"
                )
                or raw.get(
                    "items"
                )
                or raw.get(
                    "data"
                )
                or []
            )
        else:
            items = []

        work_orders: dict[
            str,
            dict[str, Any],
        ] = {}

        for item in items:
            if not isinstance(
                item,
                dict,
            ):
                continue

            work_order_id = item.get(
                "work_order_id"
            )

            if work_order_id:
                work_orders[
                    str(
                        work_order_id
                    )
                ] = item

        return work_orders

    def _get_work_order(
        self,
        work_order_id: str,
    ) -> dict[str, Any]:
        work_order = self._work_orders_by_id.get(
            work_order_id
        )

        if not work_order:
            raise WorkOrderNotFoundError(
                f"Work order {work_order_id} was not found."
            )

        return work_order

    def _initial_status(
        self,
        work_order: dict[str, Any],
    ) -> str:
        lifecycle_status = work_order.get(
            "lifecycle_status"
        )

        if lifecycle_status in ALLOWED_TRANSITIONS:
            return str(
                lifecycle_status
            )

        status = str(
            work_order.get(
                "status",
                "draft",
            )
        ).lower()

        status_map = {
            "draft": "draft",
            "open": "draft",
            "new": "draft",
            "recommended": "draft",
            "pending": "pending_approval",
            "approved": "approved",
            "assigned": "assigned",
            "in_progress": "in_progress",
            "waiting_for_part": "waiting_for_part",
            "completed": "completed",
            "verification_pending": "verification_pending",
            "verified": "verified",
            "closed": "closed",
        }

        return status_map.get(
            status,
            "draft",
        )

    def _risk_score(
        self,
        work_order: dict[str, Any],
    ) -> float:
        value = work_order.get(
            "risk_score",
            0.0,
        )

        try:
            return float(
                value
            )
        except TypeError:
            return 0.0
        except ValueError:
            return 0.0

    def _is_high_risk(
        self,
        work_order: dict[str, Any],
    ) -> bool:
        priority = str(
            work_order.get(
                "priority",
                "",
            )
        ).lower()

        return (
            self._risk_score(
                work_order
            )
            >= HIGH_RISK_THRESHOLD
            or priority in HIGH_RISK_PRIORITIES
        )

    def _approval_required(
        self,
        *,
        work_order: dict[str, Any],
        current_status: str,
    ) -> bool:
        return (
            self._is_high_risk(
                work_order
            )
            and current_status in {
                "draft",
                "pending_approval",
            }
        )

    def _requires_approval(
        self,
        *,
        work_order: dict[str, Any],
        current_status: str,
        target_status: str,
    ) -> bool:
        return (
            self._is_high_risk(
                work_order
            )
            and current_status == "pending_approval"
            and target_status == "approved"
        )

    def _requires_successful_verification(
        self,
        *,
        current_status: str,
        target_status: str,
    ) -> bool:
        return (
            current_status == "verification_pending"
            and target_status == "verified"
        )

    def _requires_failed_recovery_for_reopen(
        self,
        *,
        current_status: str,
        target_status: str,
    ) -> bool:
        return (
            current_status == "verification_pending"
            and target_status == "in_progress"
        )

    def _invalid_transition_message(
        self,
        *,
        current_status: str,
        target_status: str,
    ) -> str:
        if (
            current_status == "completed"
            and target_status == "closed"
        ):
            return (
                "Invalid transition: completed cannot directly become closed. "
                "Move to verification_pending, then verified, then closed."
            )

        allowed = ", ".join(
            ALLOWED_TRANSITIONS[
                current_status
            ]
        ) or "none"

        return (
            f"Invalid transition from {current_status} to {target_status}. "
            f"Allowed next statuses: {allowed}."
        )

    def _record_rejected_transition(
        self,
        *,
        work_order_id: str,
        from_status: str,
        request: WorkOrderTransitionRequest,
        reason: str,
    ) -> None:
        audit_event = self._audit_event(
            work_order_id=work_order_id,
            event_type="transition_rejected",
            timestamp=request.changed_at,
            from_status=from_status,
            to_status=request.target_status,
            changed_by=request.changed_by,
            note=request.note,
            approval_reference=request.approval_reference,
            approver_role=request.approver_role,
            verification_reference=request.verification_reference,
            verification_outcome=request.verification_outcome,
            explanation=reason,
        )

        self._audit_events_by_id.setdefault(
            work_order_id,
            [],
        ).append(
            audit_event
        )

    def _audit_event(
        self,
        *,
        work_order_id: str,
        event_type: str,
        timestamp: str,
        from_status: str,
        to_status: str,
        changed_by: str,
        note: str | None,
        approval_reference: str | None,
        approver_role: str | None,
        verification_reference: str | None,
        verification_outcome: str | None,
        explanation: str,
    ) -> WorkOrderLifecycleAuditEvent:
        digest = hashlib.sha256(
            (
                f"{work_order_id}:"
                f"{event_type}:"
                f"{timestamp}:"
                f"{from_status}:"
                f"{to_status}:"
                f"{changed_by}:"
                f"{approval_reference or ''}:"
                f"{verification_reference or ''}:"
                f"{verification_outcome or ''}"
            ).encode(
                "utf-8"
            )
        ).hexdigest()[:12]

        return WorkOrderLifecycleAuditEvent(
            event_id=f"WO-AUDIT-{digest}",
            work_order_id=work_order_id,
            event_type=event_type,
            timestamp=timestamp,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            note=note,
            approval_reference=approval_reference,
            approver_role=approver_role,
            verification_reference=verification_reference,
            verification_outcome=verification_outcome,
            explanation=explanation,
        )