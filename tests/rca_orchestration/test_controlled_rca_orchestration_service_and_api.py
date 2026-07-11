from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.rca_orchestration.schemas import (
    ControlledRcaRequest,
    RcaApprovalRequest,
)
from apps.api.rca_orchestration.service import (
    WORKFLOW_VERSION,
    ControlledRcaOrchestrationService,
)
from apps.api.routes import rca_orchestration as route_module


client = TestClient(app)


def _request() -> ControlledRcaRequest:
    return ControlledRcaRequest(
        incident_id="INC-P-101-DEMO",
        asset_id="P-101",
        rca_case_id="RCA-P101-001",
        requested_by="maintenance_engineer",
        include_similar_cases=True,
    )


def _dependency_for(
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
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "rca-orchestration-tester",
        "email": "rca-orchestration@plantmind.local",
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
def isolated_rca_service() -> Iterator[ControlledRcaOrchestrationService]:
    original_service = route_module.controlled_rca_service
    service = ControlledRcaOrchestrationService()
    route_module.controlled_rca_service = service

    try:
        yield service
    finally:
        route_module.controlled_rca_service = original_service


def test_workflow_runs_all_required_deterministic_steps() -> None:
    service = ControlledRcaOrchestrationService()

    response = service.run(
        _request()
    )

    assert response.workflow_version == WORKFLOW_VERSION
    assert response.rca_case_id == "RCA-P101-001"
    assert response.incident_id == "INC-P-101-DEMO"
    assert response.asset_id == "P-101"

    assert [
        step.step_name
        for step in response.steps
    ] == [
        "load_incident",
        "retrieve_telemetry",
        "retrieve_evidence",
        "retrieve_approved_documents",
        "retrieve_similar_cases",
        "generate_candidate_causes",
        "rank_causes",
        "identify_contradictions",
        "identify_missing_tests",
        "draft_rca",
        "request_engineer_approval",
    ]

    assert all(
        step.status == "completed"
        for step in response.steps
    )
    assert all(
        step.explanation
        for step in response.steps
    )


def test_rca_p101_includes_new_telemetry_evidence() -> None:
    service = ControlledRcaOrchestrationService()

    response = service.run(
        _request()
    )

    telemetry_ids = {
        evidence.evidence_id
        for evidence in response.telemetry_evidence
    }

    assert {
        "TEL-P101-NEW-001",
        "TEL-P101-NEW-002",
        "TEL-P101-NEW-003",
    }.issubset(telemetry_ids)

    assert all(
        evidence.evidence_type == "telemetry"
        for evidence in response.telemetry_evidence
    )

    assert any(
        evidence.direction == "supporting"
        for evidence in response.telemetry_evidence
    )

    assert any(
        evidence.direction == "contradictory"
        for evidence in response.telemetry_evidence
    )


def test_supporting_and_contradictory_evidence_are_shown() -> None:
    service = ControlledRcaOrchestrationService()

    response = service.run(
        _request()
    )

    assert response.supporting_evidence
    assert response.contradictory_evidence
    assert response.contextual_evidence

    assert all(
        evidence.direction == "supporting"
        for evidence in response.supporting_evidence
    )

    assert all(
        evidence.direction == "contradictory"
        for evidence in response.contradictory_evidence
    )

    supporting_ids = {
        evidence.evidence_id
        for evidence in response.supporting_evidence
    }
    contradictory_ids = {
        evidence.evidence_id
        for evidence in response.contradictory_evidence
    }

    top_cause = response.candidate_causes[0]

    assert top_cause.cause_id == "CAUSE-P101-BEARING-DAMAGE"
    assert top_cause.rank == 1
    assert set(top_cause.supporting_evidence_ids).intersection(
        supporting_ids | {
            evidence.evidence_id
            for evidence in response.telemetry_evidence
        }
    )
    assert set(top_cause.contradictory_evidence_ids).intersection(
        contradictory_ids
    )


def test_missing_tests_block_confirmation_until_engineer_review() -> None:
    service = ControlledRcaOrchestrationService()

    response = service.run(
        _request()
    )

    assert response.missing_tests
    assert all(
        test.required_before_confirmation
        for test in response.missing_tests
    )

    assert response.draft.approval_status == "approval_required"
    assert response.draft.engineer_approval_required is True
    assert response.draft.auto_confirmation_blocked is True
    assert response.draft.safety_closure_blocked is True
    assert response.draft.critical_work_order_approval_blocked is True


def test_guardrails_prevent_unrestricted_agent_behavior() -> None:
    service = ControlledRcaOrchestrationService()

    response = service.run(
        _request()
    )

    guardrail_text = " ".join(
        response.guardrails
    ).lower()

    assert "draft" in guardrail_text
    assert "rank" in guardrail_text
    assert "retrieve" in guardrail_text
    assert "recommend" in guardrail_text
    assert "cannot confirm root cause automatically" in guardrail_text
    assert "cannot close a safety incident" in guardrail_text
    assert "cannot approve a critical work order" in guardrail_text
    assert "engineer approval is required" in guardrail_text


def test_approval_endpoint_records_engineer_decision() -> None:
    service = ControlledRcaOrchestrationService()

    service.run(
        _request()
    )

    approval = service.approve(
        RcaApprovalRequest(
            rca_case_id="RCA-P101-001",
            approved_by="engineer.deepika",
            approved_at="2026-07-10T11:00:00+00:00",
            decision="approved",
            note="Evidence reviewed and approved for governed confirmation.",
        )
    )

    assert approval.rca_case_id == "RCA-P101-001"
    assert approval.approval_status == "approved"
    assert approval.confirmation_allowed is True
    assert "Engineer approval recorded" in approval.explanation


def test_rejection_keeps_confirmation_blocked() -> None:
    service = ControlledRcaOrchestrationService()

    approval = service.approve(
        RcaApprovalRequest(
            rca_case_id="RCA-P101-001",
            approved_by="engineer.deepika",
            approved_at="2026-07-10T11:05:00+00:00",
            decision="rejected",
            note="Need bearing inspection before approval.",
        )
    )

    assert approval.approval_status == "rejected"
    assert approval.confirmation_allowed is False
    assert "remains blocked" in approval.explanation


def test_history_tracks_orchestration_runs() -> None:
    service = ControlledRcaOrchestrationService()

    service.run(
        _request()
    )
    service.run(
        _request()
    )

    history = service.history(
        "RCA-P101-001"
    )

    assert history.rca_case_id == "RCA-P101-001"
    assert history.total_runs == 2
    assert len(history.runs) == 2


def test_controlled_rca_api_run_approval_and_history() -> None:
    with isolated_rca_service():
        with authorized_user("run_controlled_rca"):
            run_response = client.post(
                "/rca-orchestration/run",
                json=_request().model_dump(),
            )

        assert run_response.status_code == 200
        payload = run_response.json()

        assert payload["workflow_version"] == WORKFLOW_VERSION
        assert payload["rca_case_id"] == "RCA-P101-001"
        assert payload["draft"]["approval_status"] == "approval_required"
        assert payload["draft"]["auto_confirmation_blocked"] is True
        assert len(payload["telemetry_evidence"]) >= 3
        assert len(payload["supporting_evidence"]) >= 1
        assert len(payload["contradictory_evidence"]) >= 1

        with authorized_user("approve_controlled_rca"):
            approval_response = client.post(
                "/rca-orchestration/approval",
                json={
                    "rca_case_id": "RCA-P101-001",
                    "approved_by": "engineer.deepika",
                    "approved_at": "2026-07-10T11:00:00+00:00",
                    "decision": "approved",
                    "note": "Approved after evidence review.",
                },
            )

        assert approval_response.status_code == 200
        assert approval_response.json()["approval_status"] == "approved"
        assert approval_response.json()["confirmation_allowed"] is True

        with authorized_user("get_controlled_rca_history"):
            history_response = client.get(
                "/rca-orchestration/cases/RCA-P101-001/history"
            )

        assert history_response.status_code == 200
        assert history_response.json()["total_runs"] == 1


def test_controlled_rca_api_requires_authentication() -> None:
    response = client.post(
        "/rca-orchestration/run",
        json=_request().model_dump(),
    )

    assert response.status_code == 401