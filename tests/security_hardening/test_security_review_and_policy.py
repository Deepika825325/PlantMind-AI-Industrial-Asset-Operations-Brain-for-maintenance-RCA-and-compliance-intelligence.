from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routes import security_review as security_review_route
from apps.api.security_hardening.policy import security_policy


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        security_review_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_admin(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "security-review-tester",
        "email": "security-review@plantmind.local",
        "role": "admin",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


def test_admin_security_review_requires_authorization() -> None:
    response = client.get(
        "/admin/security-review"
    )

    assert response.status_code == 401


def test_admin_security_review_reports_security_controls() -> None:
    with authorized_admin(
        "get_security_review"
    ):
        response = client.get(
            "/admin/security-review"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "passed"
    assert payload["secrets_policy"]["status"] == "passed"
    assert payload["rate_limiting"]["status"] == "enabled"
    assert payload["upload_size_limits"]["status"] == "enabled"
    assert payload["cors_restrictions"]["status"] == "restricted"
    assert payload["jwt_expiry"]["status"] == "bounded"
    assert payload["input_validation"]["status"] == "enabled"
    assert payload["admin_route_protection"]["status"] == "enabled"


def test_security_policy_blocks_oversized_uploads() -> None:
    assert security_policy.is_upload_allowed(
        security_policy.max_upload_bytes
    )
    assert not security_policy.is_upload_allowed(
        security_policy.max_upload_bytes + 1
    )


def test_security_headers_are_added_to_api_responses() -> None:
    response = client.get(
        "/observability/health"
    )

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "Permissions-Policy" in response.headers