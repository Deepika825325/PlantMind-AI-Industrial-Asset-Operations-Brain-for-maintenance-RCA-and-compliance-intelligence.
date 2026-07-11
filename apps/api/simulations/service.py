from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import ceil

from apps.api.simulations.schemas import (
    SimulationCreateRequest,
    SimulationRecord,
    SimulationResponse,
    SimulationScenario,
    SimulationSpeedRequest,
    SimulationStatus,
)


MODE_LABEL = "Historical replay"
SOURCE_LABEL = "Generated experimental dataset"
LIVE_PLANT_CONNECTED = False


@dataclass
class SimulationState:
    simulation_id: str
    scenario: SimulationScenario
    asset_id: str
    status: SimulationStatus
    speed_multiplier: float
    records: list[SimulationRecord]
    cursor: int = 0
    emitted_records: list[SimulationRecord] = field(default_factory=list)


class SimulationService:
    def __init__(self) -> None:
        self._simulations: dict[str, SimulationState] = {}

    def create_simulation(
        self,
        request: SimulationCreateRequest,
    ) -> SimulationResponse:
        simulation_id = self._simulation_id(
            scenario=request.scenario,
            asset_id=request.asset_id,
            record_count=request.record_count,
        )

        records = self._generate_records(
            scenario=request.scenario,
            asset_id=request.asset_id,
            record_count=request.record_count,
        )

        state = SimulationState(
            simulation_id=simulation_id,
            scenario=request.scenario,
            asset_id=request.asset_id,
            status="created",
            speed_multiplier=1.0,
            records=records,
        )

        self._simulations[simulation_id] = state

        return self._to_response(state)

    def start_simulation(
        self,
        simulation_id: str,
    ) -> SimulationResponse:
        state = self._get_state(simulation_id)

        state.status = "running"

        if state.cursor == 0:
            self._emit_next(state)

        return self._to_response(state)

    def pause_simulation(
        self,
        simulation_id: str,
    ) -> SimulationResponse:
        state = self._get_state(simulation_id)

        if state.status != "completed":
            state.status = "paused"

        return self._to_response(state)

    def resume_simulation(
        self,
        simulation_id: str,
    ) -> SimulationResponse:
        state = self._get_state(simulation_id)

        if state.status != "completed":
            state.status = "running"
            self._emit_next(state)

        return self._to_response(state)

    def reset_simulation(
        self,
        simulation_id: str,
    ) -> SimulationResponse:
        state = self._get_state(simulation_id)

        state.status = "created"
        state.cursor = 0
        state.emitted_records = []
        state.speed_multiplier = 1.0

        return self._to_response(state)

    def set_speed(
        self,
        simulation_id: str,
        request: SimulationSpeedRequest,
    ) -> SimulationResponse:
        state = self._get_state(simulation_id)

        state.speed_multiplier = request.speed_multiplier

        return self._to_response(state)

    def get_simulation(
        self,
        simulation_id: str,
    ) -> SimulationResponse:
        state = self._get_state(simulation_id)

        if state.status == "running":
            self._emit_next(state)

        return self._to_response(state)

    def _emit_next(
        self,
        state: SimulationState,
    ) -> None:
        records_to_emit = max(
            1,
            ceil(state.speed_multiplier),
        )

        for _ in range(records_to_emit):
            if state.cursor >= len(state.records):
                state.status = "completed"
                break

            state.emitted_records.append(
                state.records[state.cursor]
            )
            state.cursor += 1

        if state.cursor >= len(state.records):
            state.status = "completed"

    def _get_state(
        self,
        simulation_id: str,
    ) -> SimulationState:
        if simulation_id not in self._simulations:
            raise FileNotFoundError(
                f"Simulation not found: {simulation_id}"
            )

        return self._simulations[simulation_id]

    def _to_response(
        self,
        state: SimulationState,
    ) -> SimulationResponse:
        latest_record = (
            state.emitted_records[-1]
            if state.emitted_records
            else None
        )

        return SimulationResponse(
            simulation_id=state.simulation_id,
            mode=MODE_LABEL,
            source=SOURCE_LABEL,
            live_plant_connected=LIVE_PLANT_CONNECTED,
            scenario=state.scenario,
            asset_id=state.asset_id,
            status=state.status,
            speed_multiplier=state.speed_multiplier,
            cursor=state.cursor,
            total_records=len(state.records),
            emitted_count=len(state.emitted_records),
            latest_record=latest_record,
            emitted_records=state.emitted_records[-20:],
        )

    def _simulation_id(
        self,
        *,
        scenario: SimulationScenario,
        asset_id: str,
        record_count: int,
    ) -> str:
        digest = hashlib.sha256(
            f"{scenario}:{asset_id}:{record_count}".encode(
                "utf-8"
            )
        ).hexdigest()[:12]

        return f"SIM-{asset_id.replace('-', '')}-{scenario.upper()}-{digest}"

    def _generate_records(
        self,
        *,
        scenario: SimulationScenario,
        asset_id: str,
        record_count: int,
    ) -> list[SimulationRecord]:
        start = datetime(
            2026,
            7,
            10,
            9,
            0,
            0,
            tzinfo=timezone.utc,
        )

        records: list[SimulationRecord] = []

        for index in range(record_count):
            progress = index / max(record_count - 1, 1)
            timestamp = start + timedelta(
                seconds=index * 10,
            )

            vibration = 2.2
            temperature = 63.0
            current = 18.5
            rpm = 1480.0
            health = 96.0
            anomaly = 0.03
            quality = "good"

            if scenario == "normal_operation":
                vibration += 0.15 * progress
                temperature += 1.0 * progress
                current += 0.2 * progress
                health -= 1.5 * progress
                anomaly += 0.02 * progress

            elif scenario == "bearing_degradation":
                vibration += 6.4 * progress
                temperature += 28.0 * progress
                current += 4.0 * progress
                health -= 55.0 * progress
                anomaly += 0.86 * progress

            elif scenario == "shaft_misalignment":
                vibration += 4.2 * progress
                temperature += 11.0 * progress
                current += 5.5 * progress
                rpm -= 35.0 * progress
                health -= 38.0 * progress
                anomaly += 0.62 * progress

            elif scenario == "cavitation":
                vibration += 3.5 * progress
                temperature += 7.0 * progress
                current += 2.5 * progress
                rpm += 8.0 * progress
                health -= 32.0 * progress
                anomaly += 0.58 * progress

            elif scenario == "sensor_failure":
                vibration += 0.05
                temperature += 0.05
                current += 0.05
                rpm += 0.0
                health -= 12.0 * progress
                anomaly += 0.45 * progress

                if index > record_count // 2:
                    vibration = records[-1].vibration_mm_s if records else vibration
                    temperature = records[-1].bearing_temperature_deg_c if records else temperature
                    quality = "stuck_sensor"

            elif scenario == "maintenance_recovery":
                if progress < 0.5:
                    local = progress / 0.5
                    vibration += 5.4 * local
                    temperature += 23.0 * local
                    current += 3.2 * local
                    health -= 48.0 * local
                    anomaly += 0.78 * local
                else:
                    local = (progress - 0.5) / 0.5
                    vibration = 7.6 - 5.0 * local
                    temperature = 86.0 - 22.0 * local
                    current = 22.0 - 3.1 * local
                    health = 52.0 + 39.0 * local
                    anomaly = 0.82 - 0.70 * local

            records.append(
                SimulationRecord(
                    sequence=index,
                    timestamp=timestamp.isoformat(),
                    asset_id=asset_id,
                    vibration_mm_s=round(vibration, 4),
                    bearing_temperature_deg_c=round(temperature, 4),
                    motor_current_a=round(current, 4),
                    rpm=round(rpm, 4),
                    health_score=round(max(0.0, min(100.0, health)), 4),
                    anomaly_score=round(max(0.0, min(1.0, anomaly)), 4),
                    data_quality=quality,
                    scenario=scenario,
                )
            )

        return records