from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from apps.api.telemetry.schemas import (
    OperatingLimits,
    TelemetryAssetResponse,
    TelemetryLatestResponse,
    TelemetryPoint,
    TelemetrySensor,
    TelemetrySensorResponse,
    TelemetrySensorSummary,
    TelemetrySummaryResponse,
)


ALLOWED_UNITS = {
    "mm/s",
    "degC",
    "bar",
    "kPa",
    "%",
    "rpm",
    "A",
    "V",
}


@dataclass(frozen=True)
class TelemetryConfig:
    data_dir: Path = Path("data/telemetry")
    production_timescale_enabled: bool = False


class TelemetryService:
    def __init__(
        self,
        config: TelemetryConfig | None = None,
        *,
        seed_demo: bool = True,
    ) -> None:
        env_timescale_enabled = (
            os.getenv("PLANTMIND_TIMESCALE_ENABLED", "false").lower()
            in {"1", "true", "yes"}
        )

        base_config = config or TelemetryConfig()

        self.config = TelemetryConfig(
            data_dir=base_config.data_dir,
            production_timescale_enabled=(
                base_config.production_timescale_enabled
                or env_timescale_enabled
            ),
        )

        self.config.data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.sensors: dict[str, TelemetrySensor] = {}
        self.points_by_sensor: dict[str, dict[str, TelemetryPoint]] = {}

        if seed_demo:
            self._seed_demo_p101()

    def register_sensor(
        self,
        sensor: TelemetrySensor,
    ) -> TelemetrySensor:
        self._validate_unit(sensor.unit)

        self.sensors[sensor.sensor_id] = sensor
        self.points_by_sensor.setdefault(
            sensor.sensor_id,
            {},
        )

        return sensor

    def add_telemetry_point(
        self,
        point: TelemetryPoint,
    ) -> TelemetryPoint:
        sensor = self.get_sensor(point.sensor_id).sensor

        if point.asset_id != sensor.asset_id:
            raise ValueError(
                f"Telemetry point asset_id {point.asset_id} does not match sensor asset_id {sensor.asset_id}."
            )

        if point.unit != sensor.unit:
            raise ValueError(
                f"Invalid telemetry unit {point.unit}; expected {sensor.unit} for sensor {sensor.sensor_id}."
            )

        parsed_timestamp = self._parse_timestamp(
            point.timestamp
        )

        enriched_point = point.model_copy(
            update={
                "timestamp": parsed_timestamp.isoformat(),
                "operating_limit_status": self._operating_limit_status(
                    value=point.value,
                    limits=sensor.operating_limits,
                ),
                "derived_features": {
                    **point.derived_features,
                    "absolute_value": abs(point.value),
                    "limit_margin": self._limit_margin(
                        value=point.value,
                        limits=sensor.operating_limits,
                    ),
                },
            }
        )

        self.points_by_sensor.setdefault(
            point.sensor_id,
            {},
        )[enriched_point.timestamp] = enriched_point

        return enriched_point

    def get_asset_telemetry(
        self,
        asset_id: str,
    ) -> TelemetryAssetResponse:
        sensors = [
            sensor
            for sensor in self.sensors.values()
            if sensor.asset_id == asset_id
            and sensor.enabled
        ]

        return TelemetryAssetResponse(
            asset_id=asset_id,
            sensor_count=len(sensors),
            sensors=sorted(
                sensors,
                key=lambda sensor: sensor.sensor_id,
            ),
        )

    def get_sensor(
        self,
        sensor_id: str,
    ) -> TelemetrySensorResponse:
        if sensor_id not in self.sensors:
            raise FileNotFoundError(
                f"Telemetry sensor not found: {sensor_id}"
            )

        return TelemetrySensorResponse(
            sensor=self.sensors[sensor_id],
        )

    def latest_for_asset(
        self,
        asset_id: str,
    ) -> TelemetryLatestResponse:
        latest_points: list[TelemetryPoint] = []

        for sensor in self.get_asset_telemetry(asset_id).sensors:
            sensor_points = self._sorted_points(
                sensor.sensor_id
            )

            if sensor_points:
                latest_points.append(
                    sensor_points[-1]
                )

        return TelemetryLatestResponse(
            asset_id=asset_id,
            total_points=len(latest_points),
            points=latest_points,
        )

    def summarize_asset(
        self,
        asset_id: str,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        window_minutes: int = 60,
    ) -> TelemetrySummaryResponse:
        start = (
            self._parse_timestamp(start_time)
            if start_time
            else None
        )
        end = (
            self._parse_timestamp(end_time)
            if end_time
            else None
        )

        summaries: list[TelemetrySensorSummary] = []

        for sensor in self.get_asset_telemetry(asset_id).sensors:
            points = self._filter_points(
                sensor_id=sensor.sensor_id,
                start=start,
                end=end,
            )

            summaries.append(
                self._summarize_sensor(
                    sensor=sensor,
                    points=points,
                )
            )

        return TelemetrySummaryResponse(
            asset_id=asset_id,
            start_time=start.isoformat() if start else None,
            end_time=end.isoformat() if end else None,
            window_minutes=window_minutes,
            storage_backend=(
                "timescale_hypertable"
                if self.config.production_timescale_enabled
                else "json_demo_store"
            ),
            timescale_hypertable_enabled=self.config.production_timescale_enabled,
            summaries=summaries,
        )

    def _summarize_sensor(
        self,
        sensor: TelemetrySensor,
        points: list[TelemetryPoint],
    ) -> TelemetrySensorSummary:
        values = [
            point.value
            for point in points
        ]

        quality_counts: dict[str, int] = {}

        for point in points:
            quality_counts[point.quality_status] = (
                quality_counts.get(point.quality_status, 0)
                + 1
            )

        violation_count = sum(
            1
            for point in points
            if point.operating_limit_status != "normal"
        )

        latest_value = values[-1] if values else None
        trend_delta = (
            values[-1] - values[0]
            if len(values) >= 2
            else None
        )

        return TelemetrySensorSummary(
            sensor_id=sensor.sensor_id,
            asset_id=sensor.asset_id,
            telemetry_point=sensor.telemetry_point,
            unit=sensor.unit,
            count=len(values),
            min_value=min(values) if values else None,
            max_value=max(values) if values else None,
            avg_value=(
                round(sum(values) / len(values), 4)
                if values
                else None
            ),
            latest_value=latest_value,
            trend_delta=round(trend_delta, 4) if trend_delta is not None else None,
            quality_counts=quality_counts,
            operating_limit_violations=violation_count,
        )

    def _filter_points(
        self,
        sensor_id: str,
        start: datetime | None,
        end: datetime | None,
    ) -> list[TelemetryPoint]:
        points = self._sorted_points(
            sensor_id
        )

        filtered: list[TelemetryPoint] = []

        for point in points:
            timestamp = self._parse_timestamp(
                point.timestamp
            )

            if start and timestamp < start:
                continue

            if end and timestamp > end:
                continue

            filtered.append(point)

        return filtered

    def _sorted_points(
        self,
        sensor_id: str,
    ) -> list[TelemetryPoint]:
        return [
            point
            for _timestamp, point in sorted(
                self.points_by_sensor.get(sensor_id, {}).items()
            )
        ]

    def _validate_unit(
        self,
        unit: str,
    ) -> None:
        if unit not in ALLOWED_UNITS:
            raise ValueError(
                f"Invalid telemetry unit '{unit}'. Allowed units: {sorted(ALLOWED_UNITS)}"
            )

    def _operating_limit_status(
        self,
        value: float,
        limits: OperatingLimits,
    ) -> str:
        if limits.high is not None and value > limits.high:
            return "high_violation"

        if limits.low is not None and value < limits.low:
            return "low_violation"

        return "normal"

    def _limit_margin(
        self,
        value: float,
        limits: OperatingLimits,
    ) -> float:
        if limits.high is not None:
            return round(
                limits.high - value,
                4,
            )

        if limits.low is not None:
            return round(
                value - limits.low,
                4,
            )

        return 0.0

    def _parse_timestamp(
        self,
        value: str | None,
    ) -> datetime:
        if value is None:
            return datetime.now(
                timezone.utc,
            )

        normalized = value.replace(
            "Z",
            "+00:00",
        )

        parsed = datetime.fromisoformat(
            normalized,
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc,
            )

        return parsed.astimezone(
            timezone.utc,
        )

    def _seed_demo_p101(
        self,
    ) -> None:
        self.register_sensor(
            TelemetrySensor(
                sensor_id="P101-VIB-001",
                asset_id="P-101",
                name="P-101 Drive-End Bearing Vibration",
                telemetry_point="bearing_vibration",
                unit="mm/s",
                operating_limits=OperatingLimits(
                    low=0.0,
                    high=7.1,
                    high_high=9.0,
                ),
            )
        )

        self.register_sensor(
            TelemetrySensor(
                sensor_id="P101-BTEMP-001",
                asset_id="P-101",
                name="P-101 Drive-End Bearing Temperature",
                telemetry_point="bearing_temperature",
                unit="degC",
                operating_limits=OperatingLimits(
                    low=20.0,
                    high=85.0,
                    high_high=95.0,
                ),
            )
        )

        self.register_sensor(
            TelemetrySensor(
                sensor_id="P101-FLOW-001",
                asset_id="P-101",
                name="P-101 Cooling Water Flow",
                telemetry_point="cooling_water_flow",
                unit="%",
                operating_limits=OperatingLimits(
                    low=60.0,
                    high=100.0,
                ),
            )
        )

        demo_points = [
            ("P101-VIB-001", "2026-07-10T09:00:00+00:00", 5.8, "mm/s", "good"),
            ("P101-VIB-001", "2026-07-10T10:00:00+00:00", 7.6, "mm/s", "suspect"),
            ("P101-VIB-001", "2026-07-10T11:00:00+00:00", 8.2, "mm/s", "suspect"),
            ("P101-BTEMP-001", "2026-07-10T09:00:00+00:00", 78.0, "degC", "good"),
            ("P101-BTEMP-001", "2026-07-10T10:00:00+00:00", 86.5, "degC", "suspect"),
            ("P101-BTEMP-001", "2026-07-10T11:00:00+00:00", 88.0, "degC", "suspect"),
            ("P101-FLOW-001", "2026-07-10T09:00:00+00:00", 74.0, "%", "good"),
            ("P101-FLOW-001", "2026-07-10T10:00:00+00:00", 66.0, "%", "good"),
            ("P101-FLOW-001", "2026-07-10T11:00:00+00:00", 58.0, "%", "suspect"),
        ]

        for sensor_id, timestamp, value, unit, quality in demo_points:
            sensor = self.sensors[sensor_id]

            self.add_telemetry_point(
                TelemetryPoint(
                    sensor_id=sensor_id,
                    asset_id=sensor.asset_id,
                    timestamp=timestamp,
                    value=value,
                    unit=unit,
                    quality_status=quality,
                )
            )