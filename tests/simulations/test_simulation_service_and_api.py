from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routes import simulations as simulation_route
from apps.api.simulations.schemas import (
    SimulationCreateRequest,
    SimulationSpeedRequest,
)
from apps.api.simulations.service import SimulationService


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        simulation_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_user(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "simulation-tester",
        "email": "simulation@plantmind.local",
        "role": "maintenance_engineer",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_simulation_service() -> Iterator[SimulationService]:
    original_service = simulation_route.simulation_service
    service = SimulationService()
    simulation_route.simulation_service = service

    try:
        yield service
    finally:
        simulation_route.simulation_service = original_service


def test_create_simulation_has_required_labels() -> None:
    service = SimulationService()

    response = service.create_simulation(
        SimulationCreateRequest(
            scenario="bearing_degradation",
            asset_id="P-101",
            record_count=20,
        )
    )

    assert response.mode == "Historical replay"
    assert response.source == "Generated experimental dataset"
    assert response.live_plant_connected is False
    assert response.status == "created"
    assert response.total_records == 20


def test_start_emits_timestamped_sensor_record() -> None:
    service = SimulationService()

    created = service.create_simulation(
        SimulationCreateRequest(
            scenario="normal_operation",
            record_count=20,
        )
    )

    started = service.start_simulation(
        created.simulation_id
    )

    assert started.status == "running"
    assert started.emitted_count == 1
    assert started.latest_record is not None
    assert started.latest_record.timestamp.startswith("2026-07-10T09:00:00")
    assert started.latest_record.vibration_mm_s > 0


def test_speed_changes_number_of_emitted_records() -> None:
    service = SimulationService()

    created = service.create_simulation(
        SimulationCreateRequest(
            scenario="shaft_misalignment",
            record_count=20,
        )
    )

    service.start_simulation(
        created.simulation_id
    )

    service.set_speed(
        created.simulation_id,
        SimulationSpeedRequest(
            speed_multiplier=3.0,
        ),
    )

    after_poll = service.get_simulation(
        created.simulation_id
    )

    assert after_poll.speed_multiplier == 3.0
    assert after_poll.emitted_count == 4


def test_pause_stops_polling_updates() -> None:
    service = SimulationService()

    created = service.create_simulation(
        SimulationCreateRequest(
            scenario="cavitation",
            record_count=20,
        )
    )

    service.start_simulation(
        created.simulation_id
    )

    paused = service.pause_simulation(
        created.simulation_id
    )

    count_before = paused.emitted_count

    polled = service.get_simulation(
        created.simulation_id
    )

    assert polled.status == "paused"
    assert polled.emitted_count == count_before


def test_reset_returns_to_deterministic_initial_state() -> None:
    service = SimulationService()

    created = service.create_simulation(
        SimulationCreateRequest(
            scenario="maintenance_recovery",
            record_count=20,
        )
    )

    first_start = service.start_simulation(
        created.simulation_id
    )

    first_record = first_start.latest_record

    service.get_simulation(
        created.simulation_id
    )
    service.get_simulation(
        created.simulation_id
    )

    reset = service.reset_simulation(
        created.simulation_id
    )

    second_start = service.start_simulation(
        created.simulation_id
    )

    assert reset.status == "created"
    assert reset.cursor == 0
    assert reset.emitted_count == 0
    assert second_start.latest_record == first_record


def test_all_required_scenarios_can_be_created() -> None:
    service = SimulationService()

    scenarios = [
        "normal_operation",
        "bearing_degradation",
        "shaft_misalignment",
        "cavitation",
        "sensor_failure",
        "maintenance_recovery",
    ]

    for scenario in scenarios:
        response = service.create_simulation(
            SimulationCreateRequest(
                scenario=scenario,
                record_count=10,
            )
        )

        assert response.scenario == scenario
        assert response.total_records == 10


def test_simulation_api_create_start_get_pause_resume_reset_speed() -> None:
    with isolated_simulation_service():
        with authorized_user("create_simulation"):
            create_response = client.post(
                "/simulations",
                json={
                    "scenario": "bearing_degradation",
                    "asset_id": "P-101",
                    "record_count": 20,
                },
            )

        assert create_response.status_code == 201

        simulation_id = create_response.json()["simulation_id"]

        with authorized_user("start_simulation"):
            start_response = client.post(
                f"/simulations/{simulation_id}/start"
            )

        assert start_response.status_code == 200
        assert start_response.json()["emitted_count"] == 1

        with authorized_user("set_simulation_speed"):
            speed_response = client.post(
                f"/simulations/{simulation_id}/speed",
                json={
                    "speed_multiplier": 2.0,
                },
            )

        assert speed_response.status_code == 200
        assert speed_response.json()["speed_multiplier"] == 2.0

        with authorized_user("get_simulation"):
            get_response = client.get(
                f"/simulations/{simulation_id}"
            )

        assert get_response.status_code == 200
        assert get_response.json()["emitted_count"] == 3

        with authorized_user("pause_simulation"):
            pause_response = client.post(
                f"/simulations/{simulation_id}/pause"
            )

        assert pause_response.status_code == 200
        paused_count = pause_response.json()["emitted_count"]

        with authorized_user("resume_simulation"):
            resume_response = client.post(
                f"/simulations/{simulation_id}/resume"
            )

        assert resume_response.status_code == 200
        assert resume_response.json()["emitted_count"] > paused_count

        with authorized_user("reset_simulation"):
            reset_response = client.post(
                f"/simulations/{simulation_id}/reset"
            )

        assert reset_response.status_code == 200
        assert reset_response.json()["status"] == "created"
        assert reset_response.json()["emitted_count"] == 0


def test_simulation_api_requires_authentication() -> None:
    response = client.post(
        "/simulations",
        json={
            "scenario": "normal_operation",
        },
    )

    assert response.status_code == 401