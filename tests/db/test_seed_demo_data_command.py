from __future__ import annotations

import os

import pytest

from apps.api.db.seed.seed_demo_data import (
    seed_demo_database_from_url,
)


def test_seed_demo_database_from_url_is_idempotent() -> None:
    database_url = os.getenv(
        "TEST_DATABASE_URL"
    )

    if not database_url:
        pytest.skip(
            "TEST_DATABASE_URL is not set."
        )

    first_counts = seed_demo_database_from_url(
        database_url
    )

    second_counts = seed_demo_database_from_url(
        database_url
    )

    assert first_counts == second_counts

    assert second_counts["assets"] == 3
    assert second_counts["documents"] == 19
    assert second_counts["document_chunks"] == 163
    assert second_counts["rca_cases"] == 1
    assert second_counts["root_causes"] == 3
    assert second_counts["evidence"] == 4
    assert second_counts["maintenance_work_orders"] == 9
    assert second_counts["maintenance_events"] == 6
    assert second_counts["compliance_rules"] == 8
    assert second_counts["compliance_findings"] == 5