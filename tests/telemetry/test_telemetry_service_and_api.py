from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routes import telemetry as telemetry_route
from apps.api.telemetry.schemas import (
    OperatingLimits,
    TelemetryPoint,
    TelemetrySensor,
)
from apps.api.telemetry.service import (
    TelemetryConfig,
    TelemetryService,
)


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        telemetry_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_telemetry_user(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "test-telemetry-reader",
        "email": "telemetry@plantmind.local",
        "role": "data_scientist",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_telemetry_service(
    tmp_path: Path,
) -> Iterator[TelemetryService]:
    original_service = telemetry_route.telemetry_service

    service = TelemetryService(
        TelemetryConfig(
            data_dir=tmp_path / "telemetry",
            production_timescale_enabled=False,
        ),
        seed_demo=True,
    )

    telemetry_route.telemetry_service = service

    try:
        yield service
    finally:
        telemetry_route.telemetry_service = original_service


def test_p101_telemetry_is_seeded_and_queryable_by_time_range(
    tmp_path: Path,
) -> None:
    service = TelemetryService(
        TelemetryConfig(
            data_dir=tmp_path / "telemetry",
        ),
        seed_demo=True,
    )

    response = service.summarize_asset(
        "P-101",
        start_time="2026-07-10T10:00:00+00:00",
        end_time="2026-07-10T11:00:00+00:00",
        window_minutes=60,
    )

    assert response.asset_id == "P-101"
    assert response.storage_backend == "json_demo_store"
    assert len(response.summaries) == 3

    vibration_summary = next(
        summary
        for summary in response.summaries
        if summary.sensor_id == "P101-VIB-001"
    )

    assert vibration_summary.count == 2
    assert vibration_summary.max_value == 8.2
    assert vibration_summary.operating_limit_violations == 2


def test_invalid_sensor_unit_is_rejected(
    tmp_path: Path,
) -> None:
    service = TelemetryService(
        TelemetryConfig(
            data_dir=tmp_path / "telemetry",
        ),
        seed_demo=False,
    )

    with pytest.raises(ValueError) as exc_info:
        service.register_sensor(
            TelemetrySensor(
                sensor_id="BAD-UNIT-001",
                asset_id="P-101",
                name="Bad Unit Sensor",
                telemetry_point="bad_unit",
                unit="banana",
                operating_limits=OperatingLimits(
                    low=0,
                    high=1,
                ),
            )
        )

    assert "Invalid telemetry unit" in str(exc_info.value)


def test_invalid_point_unit_is_rejected(
    tmp_path: Path,
) -> None:
    service = TelemetryService(
        TelemetryConfig(
            data_dir=tmp_path / "telemetry",
        ),
        seed_demo=False,
    )

    service.register_sensor(
        TelemetrySensor(
            sensor_id="P101-VIB-LOCAL",
            asset_id="P-101",
            name="Local Vibration",
            telemetry_point="bearing_vibration",
            unit="mm/s",
            operating_limits=OperatingLimits(
                low=0,
                high=7.1,
            ),
        )
    )

    with pytest.raises(ValueError) as exc_info:
        service.add_telemetry_point(
            TelemetryPoint(
                sensor_id="P101-VIB-LOCAL",
                asset_id="P-101",
                timestamp="2026-07-10T10:00:00+00:00",
                value=7.6,
                unit="degC",
            )
        )

    assert "expected mm/s" in str(exc_info.value)


def test_duplicate_timestamp_replaces_existing_point(
    tmp_path: Path,
) -> None:
    service = TelemetryService(
        TelemetryConfig(
            data_dir=tmp_path / "telemetry",
        ),
        seed_demo=False,
    )

    service.register_sensor(
        TelemetrySensor(
            sensor_id="P101-VIB-LOCAL",
            asset_id="P-101",
            name="Local Vibration",
            telemetry_point="bearing_vibration",
            unit="mm/s",
            operating_limits=OperatingLimits(
                low=0,
                high=7.1,
            ),
        )
    )

    timestamp = "2026-07-10T10:00:00+00:00"

    service.add_telemetry_point(
        TelemetryPoint(
            sensor_id="P101-VIB-LOCAL",
            asset_id="P-101",
            timestamp=timestamp,
            value=5.0,
            unit="mm/s",
        )
    )

    service.add_telemetry_point(
        TelemetryPoint(
            sensor_id="P101-VIB-LOCAL",
            asset_id="P-101",
            timestamp=timestamp,
            value=8.0,
            unit="mm/s",
        )
    )

    summary = service.summarize_asset(
        "P-101",
    )

    local_summary = summary.summaries[0]

    assert local_summary.count == 1
    assert local_summary.latest_value == 8.0
    assert local_summary.operating_limit_violations == 1


def test_get_asset_telemetry_api(
    tmp_path: Path,
) -> None:
    with isolated_telemetry_service(tmp_path):
        with authorized_telemetry_user(
            "get_asset_telemetry"
        ):
            response = client.get(
                "/telemetry/assets/P-101"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["asset_id"] == "P-101"
    assert payload["sensor_count"] == 3
    assert payload["sensors"][0]["asset_id"] == "P-101"


def test_get_telemetry_sensor_api(
    tmp_path: Path,
) -> None:
    with isolated_telemetry_service(tmp_path):
        with authorized_telemetry_user(
            "get_telemetry_sensor"
        ):
            response = client.get(
                "/telemetry/sensors/P101-VIB-001"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["sensor"]["sensor_id"] == "P101-VIB-001"
    assert payload["sensor"]["unit"] == "mm/s"


def test_get_asset_latest_telemetry_api(
    tmp_path: Path,
) -> None:
    with isolated_telemetry_service(tmp_path):
        with authorized_telemetry_user(
            "get_asset_latest_telemetry"
        ):
            response = client.get(
                "/telemetry/assets/P-101/latest"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["asset_id"] == "P-101"
    assert payload["total_points"] == 3
    assert {
        point["sensor_id"]
        for point in payload["points"]
    } == {
        "P101-VIB-001",
        "P101-BTEMP-001",
        "P101-FLOW-001",
    }


def test_get_asset_telemetry_summary_api(
    tmp_path: Path,
) -> None:
    with isolated_telemetry_service(tmp_path):
        with authorized_telemetry_user(
            "get_asset_telemetry_summary"
        ):
            response = client.get(
                "/telemetry/assets/P-101/summary",
                params={
                    "start_time": "2026-07-10T10:00:00+00:00",
                    "end_time": "2026-07-10T11:00:00+00:00",
                    "window_minutes": 60,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["asset_id"] == "P-101"
    assert payload["window_minutes"] == 60
    assert payload["storage_backend"] == "json_demo_store"
    assert len(payload["summaries"]) == 3


def test_telemetry_requires_authentication() -> None:
    response = client.get(
        "/telemetry/assets/P-101"
    )

    assert response.status_code == 401