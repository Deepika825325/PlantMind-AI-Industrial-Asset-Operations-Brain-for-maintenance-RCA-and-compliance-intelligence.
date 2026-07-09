from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from apps.api.db.session import (
    clear_database_runtime_cache,
)
from apps.api.repositories.registry import (
    get_repository_registry,
)


def test_admin_reset_demo_endpoint_supports_postgres_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_url = os.getenv(
        "TEST_DATABASE_URL"
    )

    if not database_url:
        pytest.skip(
            "TEST_DATABASE_URL is not set."
        )

    monkeypatch.setenv(
        "PLANTMIND_DATA_BACKEND",
        "postgres",
    )
    monkeypatch.setenv(
        "DATABASE_URL",
        database_url,
    )

    get_repository_registry.cache_clear()
    clear_database_runtime_cache()

    from apps.api.main import app

    with TestClient(app) as client:
        response = client.post(
            "/admin/reset-demo"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "database_demo_reset"
    assert payload["data_mode"] == "postgres"
    assert payload["cache_cleared"] is True
    assert (
        payload["relationship_validation"]["status"]
        == "valid"
    )

    counts = payload["relationship_validation"]["counts"]

    assert counts["assets"] == 3
    assert counts["documents"] == 19
    assert counts["document_chunks"] == 163
    assert counts["rca_cases"] == 1
    assert counts["root_causes_for_p101"] == 3
    assert counts["evidence_for_p101"] == 4
    assert counts["rca_linked_work_orders_for_p101"] == 4
    assert counts["work_orders"] == 9
    assert counts["compliance_rules"] == 8

    get_repository_registry.cache_clear()
    clear_database_runtime_cache()
