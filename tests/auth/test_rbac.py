from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from apps.api.auth.rbac import (
    Permission,
    Role,
    get_permissions_for_role,
    has_permission,
)
from apps.api.main import app


def _register_and_login(
    client: TestClient,
    *,
    role: str,
) -> str:
    email = (
        f"{role.replace('_', '-')}-"
        f"{uuid.uuid4().hex}"
        "@plantmind.local"
    )

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "role-test-password",
            "full_name": f"Role Test {role}",
            "role": role,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "role-test-password",
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


def test_role_permission_matrix() -> None:
    admin_permissions = get_permissions_for_role(
        Role.ADMINISTRATOR
    )
    auditor_permissions = get_permissions_for_role(
        Role.AUDITOR
    )

    assert Permission.ADMIN_RESET_DEMO in admin_permissions
    assert Permission.WORK_ORDER_COMPLETE in admin_permissions
    assert Permission.EVIDENCE_READ in auditor_permissions
    assert Permission.WORK_ORDER_COMPLETE not in auditor_permissions

    assert has_permission(
        "reliability engineer",
        Permission.RCA_APPROVE,
    )
    assert has_permission(
        "maintenance manager",
        Permission.WORK_ORDER_APPROVE_HIGH_PRIORITY,
    )
    assert not has_permission(
        "technician",
        Permission.RCA_APPROVE,
    )


def test_permissions_endpoint_returns_user_permissions() -> None:
    client = TestClient(app)

    token = _login_admin(client)

    response = client.get(
        "/auth/permissions/me",
        headers=_auth_header(token),
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["role"] == "administrator"
    assert (
        Permission.ADMIN_RESET_DEMO
        in payload["permissions"]
    )


def test_technician_can_complete_work_order_but_cannot_approve_rca() -> None:
    client = TestClient(app)

    token = _register_and_login(
        client,
        role="technician",
    )

    complete_response = client.post(
        "/auth/rbac-check/work-orders/complete",
        headers=_auth_header(token),
    )

    approve_response = client.post(
        "/auth/rbac-check/rca/approve",
        headers=_auth_header(token),
    )

    assert complete_response.status_code == 200
    assert approve_response.status_code == 403


def test_reliability_engineer_can_approve_rca() -> None:
    client = TestClient(app)

    token = _register_and_login(
        client,
        role="reliability_engineer",
    )

    response = client.post(
        "/auth/rbac-check/rca/approve",
        headers=_auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["action"] == Permission.RCA_APPROVE


def test_auditor_is_read_only() -> None:
    client = TestClient(app)

    token = _register_and_login(
        client,
        role="auditor",
    )

    read_response = client.get(
        "/auth/rbac-check/evidence/read",
        headers=_auth_header(token),
    )

    complete_response = client.post(
        "/auth/rbac-check/work-orders/complete",
        headers=_auth_header(token),
    )

    reset_response = client.post(
        "/auth/rbac-check/admin/reset-demo",
        headers=_auth_header(token),
    )

    assert read_response.status_code == 200
    assert complete_response.status_code == 403
    assert reset_response.status_code == 403


def test_admin_reset_demo_requires_administrator_when_auth_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "AUTH_REQUIRED",
        "true",
    )

    client = TestClient(app)

    technician_token = _register_and_login(
        client,
        role="technician",
    )
    admin_token = _login_admin(client)

    missing_token_response = client.post(
        "/admin/reset-demo"
    )

    technician_response = client.post(
        "/admin/reset-demo",
        headers=_auth_header(technician_token),
    )

    admin_response = client.post(
        "/admin/reset-demo",
        headers=_auth_header(admin_token),
    )

    assert missing_token_response.status_code == 401
    assert technician_response.status_code == 403
    assert admin_response.status_code == 200
    assert admin_response.json()["status"] in {
        "demo_reset",
        "database_demo_reset",
    }


def test_admin_reset_demo_remains_open_when_auth_is_not_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "AUTH_REQUIRED",
        "false",
    )

    client = TestClient(app)

    response = client.post(
        "/admin/reset-demo"
    )

    assert response.status_code == 200
    assert response.json()["status"] in {
        "demo_reset",
        "database_demo_reset",
    }
