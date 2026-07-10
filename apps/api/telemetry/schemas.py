from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SensorQualityStatus = Literal[
    "good",
    "suspect",
    "bad",
    "missing",
]

OperatingLimitStatus = Literal[
    "normal",
    "low_violation",
    "high_violation",
    "unknown",
]


class OperatingLimits(BaseModel):
    low: float | None = None
    high: float | None = None
    low_low: float | None = None
    high_high: float | None = None


class TelemetrySensor(BaseModel):
    sensor_id: str
    asset_id: str
    name: str
    telemetry_point: str
    unit: str
    quality_status: SensorQualityStatus = "good"
    operating_limits: OperatingLimits
    source_system: str = "demo_telemetry"
    enabled: bool = True


class TelemetryPoint(BaseModel):
    sensor_id: str
    asset_id: str
    timestamp: str
    value: float
    unit: str
    quality_status: SensorQualityStatus = "good"
    operating_limit_status: OperatingLimitStatus = "normal"
    derived_features: dict[str, float | int | str] = Field(default_factory=dict)


class TelemetryAssetResponse(BaseModel):
    asset_id: str
    sensor_count: int
    sensors: list[TelemetrySensor]


class TelemetrySensorResponse(BaseModel):
    sensor: TelemetrySensor


class TelemetryLatestResponse(BaseModel):
    asset_id: str
    total_points: int
    points: list[TelemetryPoint]


class TelemetrySensorSummary(BaseModel):
    sensor_id: str
    asset_id: str
    telemetry_point: str
    unit: str
    count: int
    min_value: float | None = None
    max_value: float | None = None
    avg_value: float | None = None
    latest_value: float | None = None
    trend_delta: float | None = None
    quality_counts: dict[str, int] = Field(default_factory=dict)
    operating_limit_violations: int = 0


class TelemetrySummaryResponse(BaseModel):
    asset_id: str
    start_time: str | None = None
    end_time: str | None = None
    window_minutes: int
    storage_backend: str
    timescale_hypertable_enabled: bool
    summaries: list[TelemetrySensorSummary]