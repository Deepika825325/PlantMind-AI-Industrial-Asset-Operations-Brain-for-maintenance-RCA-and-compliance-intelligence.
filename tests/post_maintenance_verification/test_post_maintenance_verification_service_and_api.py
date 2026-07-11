from __future__ import annotations

import inspect
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.post_maintenance_verification.schemas import (
    MaintenanceRecoveryReplayRequest,
    PostMaintenanceVerificationRequest,
    TelemetrySnapshot,
)
from apps.api.post_maintenance_verification.service import (
    PostMaintenanceVerificationService,
)
from apps.api.routes import post_maintenance_verification as verification_route
from apps.api.routes import work_order_lifecycle as lifecycle_route
from apps.api.work_order_lifecycle.service import (
    GovernedWorkOrderLifecycleService,
)


client = TestClient(app)


def _write_work_orders(
    path: Path,
) -> None:
    payload = {
        "work_orders": [
            {
                "work_order_id": "WO-P101-COMPLETE-001",
                "asset_id": "P-101",
                "title": "Conduct post-maintenance vibration test",
                "priority": "high",
                "lifecycle_status": "verification_pending",
                "risk_score": 81.0,
            },
            {
                "work_order_id": "WO-P101-FAILED-001",
                "asset_id": "P-101",
                "title": "Inspect and relubricate drive-end bearing",
                "priority": "critical",
                "lifecycle_status": "verification_pending",
                "risk_score": 92.0,
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


def _dependency_for(
    route_module: Any,
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        route_module,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_user(
    route_module: Any,
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        route_module,
        endpoint_name,
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "post-maintenance-verification-tester",
        "email": "post-maintenance-verification@plantmind.local",
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
def isolated_services(
    work_order_path: Path,
) -> Iterator[
    tuple[
        PostMaintenanceVerificationService,
        GovernedWorkOrderLifecycleService,
    ]
]:
    original_verification_service = (
        verification_route.post_maintenance_verification_service
    )
    original_lifecycle_service = lifecycle_route.work_order_lifecycle_service

    verification_service = PostMaintenanceVerificationService()
    lifecycle_service = GovernedWorkOrderLifecycleService(
        work_order_path=work_order_path
    )

    verification_route.post_maintenance_verification_service = verification_service
    lifecycle_route.work_order_lifecycle_service = lifecycle_service

    try:
        yield verification_service, lifecycle_service
    finally:
        verification_route.post_maintenance_verification_service = (
            original_verification_service
        )
        lifecycle_route.work_order_lifecycle_service = original_lifecycle_service


def _successful_request() -> PostMaintenanceVerificationRequest:
    return PostMaintenanceVerificationRequest(
        work_order_id="WO-P101-COMPLETE-001",
        asset_id="P-101",
        verified_by="maintenance.engineer",
        verified_at="2026-07-10T10:00:00+00:00",
        pre_maintenance=TelemetrySnapshot(
            vibration_mm_s=8.8,
            bearing_temperature_c=94.0,
            health_score=42.0,
            anomaly_score=0.91,
            failure_probability=0.82,
        ),
        post_maintenance=TelemetrySnapshot(
            vibration_mm_s=2.4,
            bearing_temperature_c=66.0,
            health_score=88.0,
            anomaly_score=0.12,
            failure_probability=0.14,
        ),
    )


def test_successful_recovery_replay_normalizes_readings() -> None:
    service = PostMaintenanceVerificationService()

    result = service.replay_recovery(
        MaintenanceRecoveryReplayRequest(
            work_order_id="WO-P101-COMPLETE-001",
            asset_id="P-101",
            scenario="successful_recovery",
            verified_by="maintenance.engineer",
            verified_at="2026-07-10T10:00:00+00:00",
        )
    )

    assert result.outcome == "successful"
    assert result.readings_normalized is True
    assert result.can_mark_verified is True
    assert result.should_reopen_work_order is False
    assert result.passed_metric_count == 5
    assert result.failed_metric_count == 0
    assert result.missing_metric_count == 0

    assert result.post_maintenance.vibration_mm_s is not None
    assert result.post_maintenance.vibration_mm_s <= result.criteria.max_vibration_mm_s
    assert result.post_maintenance.health_score is not None
    assert result.post_maintenance.health_score >= result.criteria.min_health_score


def test_partial_recovery_does_not_allow_verified() -> None:
    service = PostMaintenanceVerificationService()

    result = service.replay_recovery(
        MaintenanceRecoveryReplayRequest(
            work_order_id="WO-P101-COMPLETE-001",
            scenario="partial_recovery",
        )
    )

    assert result.outcome == "partially_successful"
    assert result.readings_normalized is False
    assert result.can_mark_verified is False
    assert result.should_reopen_work_order is False
    assert result.passed_metric_count >= 3
    assert result.failed_metric_count > 0


def test_failed_recovery_reopens_work_order() -> None:
    service = PostMaintenanceVerificationService()

    result = service.replay_recovery(
        MaintenanceRecoveryReplayRequest(
            work_order_id="WO-P101-FAILED-001",
            scenario="failed_recovery",
            verified_at="2026-07-10T10:05:00+00:00",
        )
    )

    assert result.outcome == "failed"
    assert result.can_mark_verified is False
    assert result.should_reopen_work_order is True
    assert result.failed_metric_count >= 3


def test_insufficient_evidence_blocks_verification() -> None:
    service = PostMaintenanceVerificationService()

    result = service.replay_recovery(
        MaintenanceRecoveryReplayRequest(
            work_order_id="WO-P101-COMPLETE-001",
            scenario="insufficient_evidence",
            verified_at="2026-07-10T10:10:00+00:00",
        )
    )

    assert result.outcome == "insufficient_evidence"
    assert result.can_mark_verified is False
    assert result.should_reopen_work_order is False
    assert result.missing_metric_count > 0


def test_verification_history_tracks_results() -> None:
    service = PostMaintenanceVerificationService()

    service.verify(
        _successful_request()
    )
    service.replay_recovery(
        MaintenanceRecoveryReplayRequest(
            work_order_id="WO-P101-COMPLETE-001",
            scenario="failed_recovery",
            verified_at="2026-07-10T10:20:00+00:00",
        )
    )

    history = service.history(
        "WO-P101-COMPLETE-001"
    )

    assert history.work_order_id == "WO-P101-COMPLETE-001"
    assert history.total_verifications == 2
    assert len(history.verifications) == 2


def test_work_order_enters_verified_only_after_successful_verification(
    tmp_path: Path,
) -> None:
    work_order_path = tmp_path / "maintenance_work_orders.json"
    _write_work_orders(
        work_order_path
    )

    with isolated_services(
        work_order_path
    ) as (
        verification_service,
        lifecycle_service,
    ):
        verification = verification_service.verify(
            _successful_request()
        )

        blocked = client.post(
            "/maintenance/work-orders/WO-P101-COMPLETE-001/lifecycle/transition",
            json={
                "target_status": "verified",
                "changed_by": "maintenance.engineer",
                "changed_at": "2026-07-10T10:01:00+00:00",
                "note": "Try to verify without verification reference.",
            },
        )

        assert blocked.status_code == 401

        with authorized_user(
            lifecycle_route,
            "transition_work_order_lifecycle",
        ):
            missing_reference_response = client.post(
                "/maintenance/work-orders/WO-P101-COMPLETE-001/lifecycle/transition",
                json={
                    "target_status": "verified",
                    "changed_by": "maintenance.engineer",
                    "changed_at": "2026-07-10T10:01:00+00:00",
                    "note": "Try to verify without verification reference.",
                },
            )

        assert missing_reference_response.status_code == 409
        assert "successful post-maintenance verification" in missing_reference_response.text

        with authorized_user(
            lifecycle_route,
            "transition_work_order_lifecycle",
        ):
            verified_response = client.post(
                "/maintenance/work-orders/WO-P101-COMPLETE-001/lifecycle/transition",
                json={
                    "target_status": "verified",
                    "changed_by": "maintenance.engineer",
                    "changed_at": "2026-07-10T10:02:00+00:00",
                    "note": "Verification criteria passed.",
                    "verification_reference": verification.verification_id,
                    "verification_outcome": verification.outcome,
                },
            )

        assert verified_response.status_code == 200
        assert verified_response.json()["current_status"] == "verified"
        assert verified_response.json()["audit_event"]["verification_reference"] == (
            verification.verification_id
        )
        assert verified_response.json()["audit_event"]["verification_outcome"] == (
            "successful"
        )

        state = lifecycle_service.get_state(
            "WO-P101-COMPLETE-001"
        )

        assert state.current_status == "verified"


def test_failed_recovery_can_reopen_work_order(
    tmp_path: Path,
) -> None:
    work_order_path = tmp_path / "maintenance_work_orders.json"
    _write_work_orders(
        work_order_path
    )

    with isolated_services(
        work_order_path
    ) as (
        verification_service,
        lifecycle_service,
    ):
        failed = verification_service.replay_recovery(
            MaintenanceRecoveryReplayRequest(
                work_order_id="WO-P101-FAILED-001",
                scenario="failed_recovery",
                verified_at="2026-07-10T10:05:00+00:00",
            )
        )

        with authorized_user(
            lifecycle_route,
            "transition_work_order_lifecycle",
        ):
            reopen_response = client.post(
                "/maintenance/work-orders/WO-P101-FAILED-001/lifecycle/transition",
                json={
                    "target_status": "in_progress",
                    "changed_by": "maintenance.engineer",
                    "changed_at": "2026-07-10T10:06:00+00:00",
                    "note": "Failed recovery, reopen work order.",
                    "verification_reference": failed.verification_id,
                    "verification_outcome": failed.outcome,
                },
            )

        assert reopen_response.status_code == 200
        assert reopen_response.json()["current_status"] == "in_progress"
        assert reopen_response.json()["audit_event"]["verification_outcome"] == (
            "failed"
        )

        state = lifecycle_service.get_state(
            "WO-P101-FAILED-001"
        )

        assert state.current_status == "in_progress"


def test_non_failed_recovery_cannot_reopen_work_order(
    tmp_path: Path,
) -> None:
    work_order_path = tmp_path / "maintenance_work_orders.json"
    _write_work_orders(
        work_order_path
    )

    with isolated_services(
        work_order_path
    ) as (
        verification_service,
        _lifecycle_service,
    ):
        verification = verification_service.verify(
            _successful_request()
        )

        with authorized_user(
            lifecycle_route,
            "transition_work_order_lifecycle",
        ):
            response = client.post(
                "/maintenance/work-orders/WO-P101-COMPLETE-001/lifecycle/transition",
                json={
                    "target_status": "in_progress",
                    "changed_by": "maintenance.engineer",
                    "changed_at": "2026-07-10T10:06:00+00:00",
                    "note": "Try reopen despite successful verification.",
                    "verification_reference": verification.verification_id,
                    "verification_outcome": verification.outcome,
                },
            )

    assert response.status_code == 409
    assert "failed post-maintenance verification" in response.text


def test_post_maintenance_verification_api_replay_history_and_criteria(
    tmp_path: Path,
) -> None:
    work_order_path = tmp_path / "maintenance_work_orders.json"
    _write_work_orders(
        work_order_path
    )

    with isolated_services(
        work_order_path
    ):
        with authorized_user(
            verification_route,
            "get_post_maintenance_verification_criteria",
        ):
            criteria_response = client.get(
                "/maintenance/post-maintenance-verification/criteria"
            )

        assert criteria_response.status_code == 200
        assert "Verified only" in criteria_response.json()["verified_transition_rule"]

        with authorized_user(
            verification_route,
            "replay_post_maintenance_recovery",
        ):
            replay_response = client.post(
                "/maintenance/work-orders/WO-P101-COMPLETE-001/post-maintenance-verification/replay",
                json={
                    "work_order_id": "WO-P101-COMPLETE-001",
                    "asset_id": "P-101",
                    "scenario": "successful_recovery",
                    "verified_by": "maintenance.engineer",
                    "verified_at": "2026-07-10T10:00:00+00:00",
                },
            )

        assert replay_response.status_code == 200
        assert replay_response.json()["outcome"] == "successful"
        assert replay_response.json()["readings_normalized"] is True

        with authorized_user(
            verification_route,
            "get_post_maintenance_verification_history",
        ):
            history_response = client.get(
                "/maintenance/work-orders/WO-P101-COMPLETE-001/post-maintenance-verification/history"
            )

        assert history_response.status_code == 200
        assert history_response.json()["total_verifications"] == 1


def test_post_maintenance_verification_api_requires_authentication() -> None:
    response = client.get(
        "/maintenance/post-maintenance-verification/criteria"
    )

    assert response.status_code == 401