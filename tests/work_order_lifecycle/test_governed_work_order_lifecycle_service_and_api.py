from __future__ import annotations

import inspect
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routes import work_order_lifecycle as lifecycle_route
from apps.api.work_order_lifecycle.schemas import WorkOrderTransitionRequest
from apps.api.work_order_lifecycle.service import (
    ALLOWED_TRANSITIONS,
    GovernedWorkOrderLifecycleService,
    HIGH_RISK_THRESHOLD,
    WorkOrderLifecycleConflictError,
)


client = TestClient(app)



def _response_text(
    response: Any,
) -> str:
    return json.dumps(
        response.json(),
        sort_keys=True,
    )


def _write_work_orders(
    path: Path,
) -> None:
    payload = {
        "work_orders": [
            {
                "work_order_id": "WO-P101-HIGH-001",
                "asset_id": "P-101",
                "title": "Inspect and relubricate drive-end bearing",
                "priority": "critical",
                "status": "draft",
                "risk_score": 92.0,
            },
            {
                "work_order_id": "WO-P101-COMPLETE-001",
                "asset_id": "P-101",
                "title": "Conduct post-maintenance vibration test",
                "priority": "medium",
                "lifecycle_status": "completed",
                "risk_score": 42.0,
            },
            {
                "work_order_id": "WO-C201-NORMAL-001",
                "asset_id": "C-201",
                "title": "Inspect compressor lubrication system",
                "priority": "medium",
                "status": "draft",
                "risk_score": 35.0,
            },
        ]
    }

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )


@pytest.fixture()
def work_order_path(
    tmp_path: Path,
) -> Path:
    path = tmp_path / "maintenance_work_orders.json"
    _write_work_orders(
        path
    )
    return path


def _service(
    work_order_path: Path,
) -> GovernedWorkOrderLifecycleService:
    return GovernedWorkOrderLifecycleService(
        work_order_path=work_order_path
    )


def _transition_request(
    target_status: str,
    *,
    changed_at: str = "2026-07-10T09:00:00+00:00",
    approval_reference: str | None = None,
    approver_role: str | None = None,
) -> WorkOrderTransitionRequest:
    return WorkOrderTransitionRequest(
        target_status=target_status,
        changed_by="maintenance.engineer",
        changed_at=changed_at,
        note=f"Move to {target_status}.",
        approval_reference=approval_reference,
        approver_role=approver_role,
    )


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        lifecycle_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_user(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "work-order-lifecycle-tester",
        "email": "work-order-lifecycle@plantmind.local",
        "role": "maintenance_engineer",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_lifecycle_service(
    work_order_path: Path,
) -> Iterator[GovernedWorkOrderLifecycleService]:
    original_service = lifecycle_route.work_order_lifecycle_service
    service = GovernedWorkOrderLifecycleService(
        work_order_path=work_order_path
    )
    lifecycle_route.work_order_lifecycle_service = service

    try:
        yield service
    finally:
        lifecycle_route.work_order_lifecycle_service = original_service


def test_lifecycle_rules_expose_required_status_order() -> None:
    service = GovernedWorkOrderLifecycleService()

    rules = service.rules()

    assert rules.lifecycle_order == [
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
    assert rules.allowed_transitions == ALLOWED_TRANSITIONS
    assert rules.high_risk_threshold == HIGH_RISK_THRESHOLD
    assert "Completed cannot directly become closed" in rules.invalid_transition_rule


def test_initial_state_extends_existing_work_order_data(
    work_order_path: Path,
) -> None:
    service = _service(
        work_order_path
    )

    state = service.get_state(
        "WO-P101-HIGH-001"
    )

    assert state.work_order_id == "WO-P101-HIGH-001"
    assert state.asset_id == "P-101"
    assert state.title == "Inspect and relubricate drive-end bearing"
    assert state.current_status == "draft"
    assert state.high_risk is True
    assert state.approval_required is True
    assert state.allowed_next_statuses == ["pending_approval"]


def test_invalid_completed_to_closed_transition_returns_conflict(
    work_order_path: Path,
) -> None:
    service = _service(
        work_order_path
    )

    with pytest.raises(
        WorkOrderLifecycleConflictError,
        match="completed cannot directly become closed",
    ):
        service.transition(
            work_order_id="WO-P101-COMPLETE-001",
            request=_transition_request(
                "closed"
            ),
        )

    audit = service.audit(
        "WO-P101-COMPLETE-001"
    )

    assert audit.audit_event_count == 1
    assert audit.audit_events[0].event_type == "transition_rejected"
    assert audit.audit_events[0].from_status == "completed"
    assert audit.audit_events[0].to_status == "closed"


def test_completed_must_enter_verification_pending_before_closed(
    work_order_path: Path,
) -> None:
    service = _service(
        work_order_path
    )

    first = service.transition(
        work_order_id="WO-P101-COMPLETE-001",
        request=_transition_request(
            "verification_pending",
            changed_at="2026-07-10T09:01:00+00:00",
        ),
    )
    second = service.transition(
        work_order_id="WO-P101-COMPLETE-001",
        request=_transition_request(
            "verified",
            changed_at="2026-07-10T09:02:00+00:00",
        ),
    )
    third = service.transition(
        work_order_id="WO-P101-COMPLETE-001",
        request=_transition_request(
            "closed",
            changed_at="2026-07-10T09:03:00+00:00",
        ),
    )

    assert first.current_status == "verification_pending"
    assert second.current_status == "verified"
    assert third.current_status == "closed"

    audit = service.audit(
        "WO-P101-COMPLETE-001"
    )

    assert audit.audit_event_count == 3
    assert [
        event.event_type
        for event in audit.audit_events
    ] == [
        "transition",
        "transition",
        "transition",
    ]


def test_high_risk_order_requires_approval_before_approved(
    work_order_path: Path,
) -> None:
    service = _service(
        work_order_path
    )

    pending = service.transition(
        work_order_id="WO-P101-HIGH-001",
        request=_transition_request(
            "pending_approval",
            changed_at="2026-07-10T09:00:00+00:00",
        ),
    )

    assert pending.current_status == "pending_approval"
    assert pending.high_risk is True
    assert pending.approval_required is True

    with pytest.raises(
        WorkOrderLifecycleConflictError,
        match="High-risk work order requires approval_reference",
    ):
        service.transition(
            work_order_id="WO-P101-HIGH-001",
            request=_transition_request(
                "approved",
                changed_at="2026-07-10T09:01:00+00:00",
            ),
        )

    approved = service.transition(
        work_order_id="WO-P101-HIGH-001",
        request=_transition_request(
            "approved",
            changed_at="2026-07-10T09:02:00+00:00",
            approval_reference="APP-P101-001",
            approver_role="maintenance_manager",
        ),
    )

    assert approved.current_status == "approved"
    assert approved.audit_event.approval_reference == "APP-P101-001"
    assert approved.audit_event.approver_role == "maintenance_manager"

    audit = service.audit(
        "WO-P101-HIGH-001"
    )

    assert audit.audit_event_count == 3
    assert [
        event.event_type
        for event in audit.audit_events
    ] == [
        "transition",
        "transition_rejected",
        "transition",
    ]


def test_normal_risk_order_can_be_approved_without_high_risk_approval(
    work_order_path: Path,
) -> None:
    service = _service(
        work_order_path
    )

    service.transition(
        work_order_id="WO-C201-NORMAL-001",
        request=_transition_request(
            "pending_approval",
            changed_at="2026-07-10T09:00:00+00:00",
        ),
    )

    approved = service.transition(
        work_order_id="WO-C201-NORMAL-001",
        request=_transition_request(
            "approved",
            changed_at="2026-07-10T09:01:00+00:00",
        ),
    )

    assert approved.high_risk is False
    assert approved.current_status == "approved"


def test_every_valid_transition_creates_audit_event(
    work_order_path: Path,
) -> None:
    service = _service(
        work_order_path
    )

    lifecycle = [
        "pending_approval",
        "approved",
        "assigned",
        "in_progress",
        "completed",
        "verification_pending",
        "verified",
        "closed",
    ]

    for index, target_status in enumerate(
        lifecycle,
        start=1,
    ):
        service.transition(
            work_order_id="WO-C201-NORMAL-001",
            request=_transition_request(
                target_status,
                changed_at=f"2026-07-10T09:{index:02d}:00+00:00",
            ),
        )

    audit = service.audit(
        "WO-C201-NORMAL-001"
    )

    assert audit.audit_event_count == len(lifecycle)
    assert all(
        event.event_type == "transition"
        for event in audit.audit_events
    )
    assert audit.audit_events[-1].to_status == "closed"


def test_work_order_lifecycle_api_rules_state_transition_conflict_and_audit(
    work_order_path: Path,
) -> None:
    with isolated_lifecycle_service(
        work_order_path
    ):
        with authorized_user("get_work_order_lifecycle_rules"):
            rules_response = client.get(
                "/maintenance/work-order-lifecycle/rules"
            )

        assert rules_response.status_code == 200
        assert rules_response.json()["high_risk_threshold"] == HIGH_RISK_THRESHOLD

        with authorized_user("get_work_order_lifecycle_state"):
            state_response = client.get(
                "/maintenance/work-orders/WO-P101-HIGH-001/lifecycle"
            )

        assert state_response.status_code == 200
        assert state_response.json()["current_status"] == "draft"
        assert state_response.json()["approval_required"] is True

        with authorized_user("transition_work_order_lifecycle"):
            pending_response = client.post(
                "/maintenance/work-orders/WO-P101-HIGH-001/lifecycle/transition",
                json={
                    "target_status": "pending_approval",
                    "changed_by": "maintenance.engineer",
                    "changed_at": "2026-07-10T09:00:00+00:00",
                    "note": "Submit for approval.",
                },
            )

        assert pending_response.status_code == 200
        assert pending_response.json()["current_status"] == "pending_approval"

        with authorized_user("transition_work_order_lifecycle"):
            conflict_response = client.post(
                "/maintenance/work-orders/WO-P101-HIGH-001/lifecycle/transition",
                json={
                    "target_status": "approved",
                    "changed_by": "maintenance.engineer",
                    "changed_at": "2026-07-10T09:01:00+00:00",
                    "note": "Try approval without manager approval.",
                },
            )

        assert conflict_response.status_code == 409
        assert "High-risk work order requires approval_reference" in _response_text(
            conflict_response
        )

        with authorized_user("transition_work_order_lifecycle"):
            approved_response = client.post(
                "/maintenance/work-orders/WO-P101-HIGH-001/lifecycle/transition",
                json={
                    "target_status": "approved",
                    "changed_by": "maintenance.engineer",
                    "changed_at": "2026-07-10T09:02:00+00:00",
                    "note": "Approved by maintenance manager.",
                    "approval_reference": "APP-P101-001",
                    "approver_role": "maintenance_manager",
                },
            )

        assert approved_response.status_code == 200
        assert approved_response.json()["current_status"] == "approved"

        with authorized_user("get_work_order_lifecycle_audit"):
            audit_response = client.get(
                "/maintenance/work-orders/WO-P101-HIGH-001/lifecycle/audit"
            )

        assert audit_response.status_code == 200
        assert audit_response.json()["audit_event_count"] == 3


def test_completed_to_closed_api_returns_409(
    work_order_path: Path,
) -> None:
    with isolated_lifecycle_service(
        work_order_path
    ):
        with authorized_user("transition_work_order_lifecycle"):
            response = client.post(
                "/maintenance/work-orders/WO-P101-COMPLETE-001/lifecycle/transition",
                json={
                    "target_status": "closed",
                    "changed_by": "maintenance.engineer",
                    "changed_at": "2026-07-10T09:00:00+00:00",
                    "note": "Invalid direct close.",
                },
            )

    assert response.status_code == 409
    assert "completed cannot directly become closed" in _response_text(
        response
    )


def test_lifecycle_api_requires_authentication() -> None:
    response = client.get(
        "/maintenance/work-order-lifecycle/rules"
    )

    assert response.status_code == 401