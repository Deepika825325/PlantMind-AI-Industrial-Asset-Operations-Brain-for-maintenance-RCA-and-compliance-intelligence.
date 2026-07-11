from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from apps.api.audit.service import (
    clear_audit_log,
    list_audit_records,
    record_audit_event,
)
from apps.api.auth.rbac import (
    Permission,
)
from apps.api.main import app


def _register_and_login(
    client: TestClient,
    *,
    role: str,
) -> str:
    email = (
        f"audit-{role.replace('_', '-')}-"
        f"{uuid.uuid4().hex}"
        "@plantmind.local"
    )

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "audit-test-password",
            "full_name": f"Audit Test {role}",
            "role": role,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "audit-test-password",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def _login_admin(
    client: TestClient,
) -> str:
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@plantmind.local",
            "password": "plantmind-admin",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def _auth_header(
    token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def test_audit_service_records_event() -> None:
    clear_audit_log()

    record = record_audit_event(
        action="test.action",
        entity_type="test_entity",
        entity_id="TEST-001",
        outcome="allowed",
        reason="Unit test event.",
        metadata={
            "source": "test",
        },
    )

    records = list_audit_records()

    assert len(records) == 1
    assert records[0].audit_id == record.audit_id
    assert records[0].action == "test.action"
    assert records[0].entity_type == "test_entity"
    assert records[0].entity_id == "TEST-001"
    assert records[0].outcome == "allowed"


def test_admin_can_read_audit_records_and_technician_cannot() -> None:
    clear_audit_log()

    client = TestClient(app)

    admin_token = _login_admin(client)
    technician_token = _register_and_login(
        client,
        role="technician",
    )

    admin_response = client.get(
        "/audit/records",
        headers=_auth_header(admin_token),
    )

    technician_response = client.get(
        "/audit/records",
        headers=_auth_header(technician_token),
    )

    assert admin_response.status_code == 200
    assert admin_response.json()["total"] >= 1
    assert technician_response.status_code == 403


def test_denied_rbac_action_is_audited() -> None:
    clear_audit_log()

    client = TestClient(app)

    technician_token = _register_and_login(
        client,
        role="technician",
    )

    response = client.post(
        "/auth/rbac-check/rca/approve",
        headers=_auth_header(technician_token),
    )

    assert response.status_code == 403

    records = list_audit_records(
        limit=20
    )

    matching_records = [
        record
        for record in records
        if record.action == Permission.RCA_APPROVE
        and record.outcome == "denied"
        and record.actor.role == "technician"
    ]

    assert matching_records


def test_allowed_rbac_action_is_audited() -> None:
    clear_audit_log()

    client = TestClient(app)

    reliability_token = _register_and_login(
        client,
        role="reliability_engineer",
    )

    response = client.post(
        "/auth/rbac-check/rca/approve",
        headers=_auth_header(reliability_token),
    )

    assert response.status_code == 200

    records = list_audit_records(
        limit=20
    )

    matching_records = [
        record
        for record in records
        if record.action == Permission.RCA_APPROVE
        and record.outcome == "allowed"
        and record.actor.role == "reliability_engineer"
    ]

    assert matching_records


def test_optional_admin_action_records_skipped_auth_audit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_audit_log()

    monkeypatch.setenv(
        "AUTH_REQUIRED",
        "false",
    )

    client = TestClient(app)

    response = client.post(
        "/admin/reload-cache"
    )

    assert response.status_code == 200

    records = list_audit_records(
        limit=20
    )

    matching_records = [
        record
        for record in records
        if record.action == Permission.ADMIN_RELOAD_CACHE
        and record.outcome == "skipped_auth_not_required"
    ]

    assert matching_records
