from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SimulationScenario = Literal[
    "normal_operation",
    "bearing_degradation",
    "shaft_misalignment",
    "cavitation",
    "sensor_failure",
    "maintenance_recovery",
]

SimulationStatus = Literal[
    "created",
    "running",
    "paused",
    "completed",
]


class SimulationCreateRequest(BaseModel):
    scenario: SimulationScenario
    asset_id: str = "P-101"
    record_count: int = Field(default=60, ge=10, le=600)


class SimulationSpeedRequest(BaseModel):
    speed_multiplier: float = Field(default=1.0, gt=0, le=20)


class SimulationRecord(BaseModel):
    sequence: int
    timestamp: str
    asset_id: str
    vibration_mm_s: float
    bearing_temperature_deg_c: float
    motor_current_a: float
    rpm: float
    health_score: float
    anomaly_score: float
    data_quality: str
    scenario: SimulationScenario


class SimulationResponse(BaseModel):
    simulation_id: str
    mode: str
    source: str
    live_plant_connected: bool
    scenario: SimulationScenario
    asset_id: str
    status: SimulationStatus
    speed_multiplier: float
    cursor: int
    total_records: int
    emitted_count: int
    latest_record: SimulationRecord | None = None
    emitted_records: list[SimulationRecord] = Field(default_factory=list)