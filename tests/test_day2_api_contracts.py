import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app


FIXTURE_DIR = Path(
    "docs/contracts/responses/v0.2"
)

VOLATILE_FIELDS = {
    "generated_at",
    "checked_at",
    "size_bytes",
}

CONTRACT_CASES = [
    (
        "system-health.json",
        ["/health"],
    ),
    (
        "system-ready.json",
        ["/ready"],
    ),
    (
        "assets-list.json",
        ["/assets"],
    ),
    (
        "asset-p101-detail.json",
        ["/assets/P-101"],
    ),
    (
        "documents-list.json",
        ["/documents"],
    ),
    (
        "document-comp001-detail.json",
        [
            (
                "/documents/"
                "COMP-001_Compliance_Checklist"
            ),
        ],
    ),
    (
        "maintenance-events-list.json",
        [
            "/maintenance/events",
            "/maintenance",
        ],
    ),
    (
        "maintenance-event-wo1001.json",
        [
            "/maintenance/events/WO-1001",
            "/maintenance/WO-1001",
        ],
    ),
    (
        "work-orders-list.json",
        ["/maintenance/work-orders"],
    ),
    (
        "work-order-mwo-p101-001.json",
        [
            (
                "/maintenance/work-orders/"
                "MWO-P101-001"
            ),
        ],
    ),
    (
        "rca-list.json",
        ["/rca"],
    ),
    (
        "rca-p101-001-detail.json",
        ["/rca/RCA-P101-001"],
    ),
    (
        "compliance-rules.json",
        ["/compliance/rules"],
    ),
    (
        "pid-001-detail.json",
        ["/pid/PID-001"],
    ),
    (
        "dashboard-operations-summary.json",
        ["/dashboard/operations-summary"],
    ),
]


def normalize_payload(
    value: Any,
) -> Any:
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}

        for key, item in value.items():
            if key in VOLATILE_FIELDS:
                continue

            if key == "path" and isinstance(
                item,
                str,
            ):
                normalized[key] = item.replace(
                    "\\",
                    "/",
                )
                continue

            normalized[key] = normalize_payload(
                item
            )

        return normalized

    if isinstance(value, list):
        return [
            normalize_payload(item)
            for item in value
        ]

    return value


def load_fixture(
    fixture_name: str,
) -> Any:
    fixture_path = (
        FIXTURE_DIR / fixture_name
    )

    assert fixture_path.is_file(), (
        f"Missing contract fixture: "
        f"{fixture_path}"
    )

    with fixture_path.open(
        "r",
        encoding="utf-8",
    ) as fixture_file:
        return json.load(fixture_file)


def request_first_available(
    client: TestClient,
    endpoints: list[str],
):
    responses = []

    for endpoint in endpoints:
        response = client.get(endpoint)

        responses.append(
            (
                endpoint,
                response.status_code,
            )
        )

        if response.status_code == 200:
            return endpoint, response

    pytest.fail(
        "No contract endpoint returned HTTP 200. "
        f"Attempts: {responses}"
    )


@pytest.fixture(scope="module")
def client():
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("fixture_name", "endpoints"),
    CONTRACT_CASES,
    ids=[
        case[0]
        for case in CONTRACT_CASES
    ],
)
def test_frozen_api_contract(
    client: TestClient,
    fixture_name: str,
    endpoints: list[str],
):
    endpoint, response = (
        request_first_available(
            client,
            endpoints,
        )
    )

    expected = normalize_payload(
        load_fixture(fixture_name)
    )
    actual = normalize_payload(
        response.json()
    )

    assert actual == expected, (
        f"Contract mismatch for "
        f"{fixture_name} at {endpoint}"
    )