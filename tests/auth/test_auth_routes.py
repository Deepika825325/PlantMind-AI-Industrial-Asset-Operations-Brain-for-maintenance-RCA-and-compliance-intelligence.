from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from apps.api.main import app


def test_login_me_refresh_and_logout() -> None:
    client = TestClient(app)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "admin@plantmind.local",
            "password": "plantmind-admin",
        },
    )

    assert login_response.status_code == 200

    token_payload = login_response.json()

    assert token_payload["token_type"] == "bearer"
    assert token_payload["access_token"]
    assert token_payload["refresh_token"]
    assert token_payload["user"]["role"] == "administrator"

    access_token = token_payload["access_token"]
    refresh_token = token_payload["refresh_token"]

    me_response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert me_response.status_code == 200
    assert (
        me_response.json()["email"]
        == "admin@plantmind.local"
    )

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]

    logout_response = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert logout_response.status_code == 200
    assert logout_response.json()["status"] == "logged_out"

    revoked_response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert revoked_response.status_code == 401


def test_invalid_token_is_rejected_by_protected_endpoint() -> None:
    client = TestClient(app)

    response = client.get(
        "/auth/protected-test",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_missing_token_is_rejected_by_protected_endpoint() -> None:
    client = TestClient(app)

    response = client.get(
        "/auth/protected-test"
    )

    assert response.status_code == 401


def test_development_registration_and_login() -> None:
    client = TestClient(app)
    email = (
        f"dev-{uuid.uuid4().hex}"
        "@plantmind.local"
    )

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "new-user-password",
            "full_name": "New Development User",
            "role": "technician",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["user"]["email"] == email

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "new-user-password",
        },
    )

    assert login_response.status_code == 200
    assert (
        login_response.json()["user"]["role"]
        == "technician"
    )


def test_current_demo_routes_remain_open_without_auth() -> None:
    client = TestClient(app)

    health_response = client.get(
        "/health"
    )
    root_response = client.get(
        "/"
    )

    assert health_response.status_code == 200
    assert root_response.status_code == 200
