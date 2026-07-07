import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.core.readiness import (
    validate_data_files,
)


@pytest.fixture
def client():
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as test_client:
        yield test_client


def test_health_endpoint(
    client: TestClient,
):
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["service"] == (
        "PlantMind AI API"
    )
    assert payload["version"] == "0.2.0"

    assert response.headers.get(
        "X-Request-ID"
    )


def test_custom_request_id_is_preserved(
    client: TestClient,
):
    request_id = (
        "plantmind-custom-request-id"
    )

    response = client.get(
        "/health",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 200

    assert response.headers.get(
        "X-Request-ID"
    ) == request_id


def test_readiness_endpoint(
    client: TestClient,
):
    response = client.get(
        "/ready"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ready"
    assert payload["ready"] is True
    assert payload[
        "required_file_count"
    ] == 21
    assert payload[
        "valid_file_count"
    ] == 21
    assert payload[
        "missing_file_count"
    ] == 0
    assert payload[
        "invalid_file_count"
    ] == 0
    assert payload["issues"] == []


def test_data_readiness_service():
    result = validate_data_files()

    assert result["ready"] is True
    assert result["status"] == "ready"
    assert result[
        "required_file_count"
    ] == 21
    assert result[
        "valid_file_count"
    ] == 21
    assert result[
        "missing_file_count"
    ] == 0
    assert result[
        "invalid_file_count"
    ] == 0


def test_file_status_endpoint(
    client: TestClient,
):
    response = client.get(
        "/status/files"
    )

    assert response.status_code == 200

    payload = response.json()

    assert "inventory" in payload
    assert "validation" in payload

    assert payload[
        "validation"
    ]["ready"] is True

    assert payload[
        "inventory"
    ]["demo_file_count"] >= 13

    assert payload[
        "inventory"
    ]["processed_file_count"] >= 8


def test_cache_reload_endpoint(
    client: TestClient,
):
    response = client.post(
        "/admin/reload-cache"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == (
        "cache_reloaded"
    )

    assert payload[
        "readiness"
    ]["ready"] is True

    assert payload[
        "readiness"
    ]["valid_file_count"] == 21


def test_unknown_route_returns_structured_error(
    client: TestClient,
):
    request_id = (
        "plantmind-test-404"
    )

    response = client.get(
        "/unknown-production-route",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 404

    payload = response.json()

    assert payload["error"]["code"] == (
        "RESOURCE_NOT_FOUND"
    )

    assert payload[
        "error"
    ]["request_id"] == request_id

    assert response.headers.get(
        "X-Request-ID"
    ) == request_id


def test_validation_error_is_structured(
    client: TestClient,
):
    request_id = (
        "plantmind-test-validation"
    )

    response = client.get(
        "/ask/search",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 422

    payload = response.json()

    assert payload["error"]["code"] == (
        "REQUEST_VALIDATION_ERROR"
    )

    assert payload[
        "error"
    ]["request_id"] == request_id

    assert isinstance(
        payload["error"]["details"],
        list,
    )

    assert response.headers.get(
        "X-Request-ID"
    ) == request_id


def test_explicit_api_error_is_structured(
    client: TestClient,
):
    response = client.get(
        "/admin/test-error"
    )

    assert response.status_code == 503

    payload = response.json()

    assert payload["error"]["code"] == (
        "DEMO_TEST_ERROR"
    )

    assert payload[
        "error"
    ]["message"] == (
        "Structured error handling "
        "is operational."
    )

    assert payload[
        "error"
    ]["request_id"]

    assert response.headers.get(
        "X-Request-ID"
    ) == payload["error"]["request_id"]

def test_demo_reset_endpoint(
    client: TestClient,
):
    response = client.post(
        "/admin/reset-demo"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == (
        "demo_reset"
    )

    assert payload[
        "cache_cleared"
    ] is True

    assert payload[
        "readiness"
    ]["ready"] is True

    assert payload[
        "readiness"
    ]["required_file_count"] == 21

    assert payload[
        "readiness"
    ]["valid_file_count"] == 21

    assert len(
        payload["restored_files"]
    ) == 3

    assert all(
        restored_file["status"]
        == "restored"
        for restored_file
        in payload["restored_files"]
    )

    assert len(
        payload["seed_validation"]
    ) == 3

    assert response.headers.get(
        "X-Request-ID"
    )

def test_dashboard_operations_summary(
    client: TestClient,
):
    response = client.get(
        "/dashboard/operations-summary",
        headers={
            "X-Request-ID": (
                "plantmind-operations-test"
            ),
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload[
        "assets_at_risk"
    ]["count"] == 3

    assert payload[
        "critical_rca_cases"
    ]["count"] == 1

    assert payload[
        "open_compliance_gaps"
    ]["count"] == 5

    assert payload[
        "urgent_work_orders"
    ]["count"] == 7

    assert payload[
        "audit_readiness"
    ]["score"] == 20

    assert payload[
        "audit_readiness"
    ][
        "evidence_ready_gap_count"
    ] == 1

    assert payload[
        "audit_readiness"
    ][
        "missing_evidence_gap_count"
    ] == 4

    top_action = payload[
        "top_recommended_action"
    ]

    assert top_action is not None

    assert top_action[
        "action_id"
    ] == "P101-CA-001"

    assert top_action[
        "title"
    ] == (
        "Inspect and restore "
        "bearing lubrication"
    )

    assert top_action[
        "priority"
    ] == "Immediate"

    assert top_action[
        "source_id"
    ] == "RCA-P101-001"

    assert response.headers.get(
        "X-Request-ID"
    ) == (
        "plantmind-operations-test"
    )

