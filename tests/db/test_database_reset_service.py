from __future__ import annotations

import os

import pytest

from apps.api.db.session import (
    clear_database_runtime_cache,
)
from apps.api.repositories.registry import (
    get_repository_registry,
)
from apps.api.services.demo_reset_service import (
    reset_demo_state,
)


def test_database_mode_reset_is_deterministic(
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

    first = reset_demo_state()
    second = reset_demo_state()

    assert first["status"] == "database_demo_reset"
    assert second["status"] == "database_demo_reset"

    assert first["relationship_validation"]["status"] == "valid"
    assert second["relationship_validation"]["status"] == "valid"

    expected_counts = {
        "assets": 3,
        "documents": 19,
        "document_chunks": 163,
        "rca_cases": 1,
        "root_causes_for_p101": 3,
        "evidence_for_p101": 4,
        "rca_linked_work_orders_for_p101": 4,
        "work_orders": 9,
        "compliance_rules": 8,
    }

    assert (
        first["relationship_validation"]["counts"]
        == expected_counts
    )
    assert (
        second["relationship_validation"]["counts"]
        == expected_counts
    )

    assert (
        first["relationship_validation"]["signature"]
        == second["relationship_validation"]["signature"]
    )

    assert first["seed_counts"] == second["seed_counts"]

    assert first["seed_counts"]["assets"] == 3
    assert first["seed_counts"]["documents"] == 19
    assert first["seed_counts"]["document_chunks"] == 163
    assert first["seed_counts"]["rca_cases"] == 1
    assert first["seed_counts"]["maintenance_work_orders"] == 9
    assert first["seed_counts"]["compliance_rules"] == 8

    get_repository_registry.cache_clear()
    clear_database_runtime_cache()
