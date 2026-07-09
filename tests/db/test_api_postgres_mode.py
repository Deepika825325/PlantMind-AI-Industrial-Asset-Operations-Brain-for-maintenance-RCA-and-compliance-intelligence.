from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from apps.api.db.seed.seed_demo_data import (
    seed_demo_database_from_url,
)
from apps.api.repositories.registry import (
    get_repository_registry,
)


@pytest.fixture(scope="module")
def postgres_api_client() -> Iterator[TestClient]:
    database_url = os.getenv(
        "TEST_DATABASE_URL"
    )

    if not database_url:
        pytest.skip(
            "TEST_DATABASE_URL is not set."
        )

    seed_demo_database_from_url(
        database_url
    )

    previous_backend = os.getenv(
        "PLANTMIND_DATA_BACKEND"
    )
    previous_database_url = os.getenv(
        "DATABASE_URL"
    )

    os.environ[
        "PLANTMIND_DATA_BACKEND"
    ] = "postgres"
    os.environ[
        "DATABASE_URL"
    ] = database_url

    get_repository_registry.cache_clear()

    from apps.api.main import app

    try:
        with TestClient(app) as client:
            yield client
    finally:
        get_repository_registry.cache_clear()

        if previous_backend is None:
            os.environ.pop(
                "PLANTMIND_DATA_BACKEND",
                None,
            )
        else:
            os.environ[
                "PLANTMIND_DATA_BACKEND"
            ] = previous_backend

        if previous_database_url is None:
            os.environ.pop(
                "DATABASE_URL",
                None,
            )
        else:
            os.environ[
                "DATABASE_URL"
            ] = previous_database_url


def test_postgres_mode_asset_endpoints(
    postgres_api_client: TestClient,
) -> None:
    list_response = postgres_api_client.get(
        "/assets"
    )

    assert list_response.status_code == 200

    asset_payload = list_response.json()

    assert asset_payload["total"] == 3

    detail_response = postgres_api_client.get(
        "/assets/P-101"
    )

    assert detail_response.status_code == 200
    assert (
        detail_response.json()["asset_id"]
        == "P-101"
    )


def test_postgres_mode_document_endpoints(
    postgres_api_client: TestClient,
) -> None:
    list_response = postgres_api_client.get(
        "/documents"
    )

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 19

    chunks_response = postgres_api_client.get(
        "/documents/"
        "IR-P101-001_Pump_Vibration_Inspection"
        "/chunks"
    )

    assert chunks_response.status_code == 200
    assert (
        chunks_response.json()["total_chunks"]
        > 0
    )


def test_postgres_mode_maintenance_endpoints(
    postgres_api_client: TestClient,
) -> None:
    list_response = postgres_api_client.get(
        "/maintenance/work-orders"
    )

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 9

    detail_response = postgres_api_client.get(
        "/maintenance/work-orders/MWO-P101-001"
    )

    assert detail_response.status_code == 200
    assert (
        detail_response.json()["work_order_id"]
        == "MWO-P101-001"
    )


def test_postgres_mode_rca_endpoints(
    postgres_api_client: TestClient,
) -> None:
    list_response = postgres_api_client.get(
        "/rca"
    )

    assert list_response.status_code == 200
    payload = list_response.json()

    assert payload["total_count"] == 1
    assert payload["filtered_count"] == 1
    assert len(payload["cases"]) == 1

    detail_response = postgres_api_client.get(
        "/rca/RCA-P101-001"
    )

    assert detail_response.status_code == 200
    assert (
        detail_response.json()["case_id"]
        == "RCA-P101-001"
    )


def test_postgres_mode_compliance_endpoints(
    postgres_api_client: TestClient,
) -> None:
    rules_response = postgres_api_client.get(
        "/compliance/rules"
    )

    assert rules_response.status_code == 200
    assert len(
        rules_response.json()["rules"]
    ) == 8

    all_gaps_response = postgres_api_client.get(
        "/compliance/gaps"
    )

    assert all_gaps_response.status_code == 200

    all_gaps_payload = all_gaps_response.json()

    assert all_gaps_payload["total"] == 15
    assert len(all_gaps_payload["gaps"]) == 15

    p101_gaps_response = postgres_api_client.get(
        "/compliance/gaps",
        params={
            "asset_id": "P-101",
        },
    )

    assert p101_gaps_response.status_code == 200

    p101_gaps_payload = p101_gaps_response.json()

    assert p101_gaps_payload["total"] == 5
    assert len(p101_gaps_payload["gaps"]) == 5
    assert all(
        gap["asset_id"] == "P-101"
        for gap in p101_gaps_payload["gaps"]
    )
