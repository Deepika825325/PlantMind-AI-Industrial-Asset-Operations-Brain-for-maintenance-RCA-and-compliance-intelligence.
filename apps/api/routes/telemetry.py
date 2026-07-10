from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.dependencies import require_permission
from apps.api.telemetry.schemas import (
    TelemetryAssetResponse,
    TelemetryLatestResponse,
    TelemetrySensorResponse,
    TelemetrySummaryResponse,
)
from apps.api.telemetry.service import TelemetryService


router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)

telemetry_service = TelemetryService()


@router.get(
    "/assets/{asset_id}",
    response_model=TelemetryAssetResponse,
)
def get_asset_telemetry(
    asset_id: str,
    user=Depends(require_permission("document.read")),
) -> TelemetryAssetResponse:
    response = telemetry_service.get_asset_telemetry(
        asset_id
    )

    record_audit_event(
        action="telemetry.asset.read",
        entity_type="asset",
        entity_id=asset_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="asset telemetry registry read",
        metadata={
            "sensor_count": response.sensor_count,
        },
    )

    return response


@router.get(
    "/sensors/{sensor_id}",
    response_model=TelemetrySensorResponse,
)
def get_telemetry_sensor(
    sensor_id: str,
    user=Depends(require_permission("document.read")),
) -> TelemetrySensorResponse:
    try:
        response = telemetry_service.get_sensor(
            sensor_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    record_audit_event(
        action="telemetry.sensor.read",
        entity_type="sensor",
        entity_id=sensor_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="telemetry sensor read",
        metadata={
            "asset_id": response.sensor.asset_id,
            "unit": response.sensor.unit,
            "telemetry_point": response.sensor.telemetry_point,
        },
    )

    return response


@router.get(
    "/assets/{asset_id}/latest",
    response_model=TelemetryLatestResponse,
)
def get_asset_latest_telemetry(
    asset_id: str,
    user=Depends(require_permission("document.read")),
) -> TelemetryLatestResponse:
    response = telemetry_service.latest_for_asset(
        asset_id
    )

    record_audit_event(
        action="telemetry.asset.latest.read",
        entity_type="asset",
        entity_id=asset_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="latest asset telemetry read",
        metadata={
            "total_points": response.total_points,
        },
    )

    return response


@router.get(
    "/assets/{asset_id}/summary",
    response_model=TelemetrySummaryResponse,
)
def get_asset_telemetry_summary(
    asset_id: str,
    start_time: str | None = Query(default=None),
    end_time: str | None = Query(default=None),
    window_minutes: int = Query(default=60, ge=1),
    user=Depends(require_permission("document.read")),
) -> TelemetrySummaryResponse:
    response = telemetry_service.summarize_asset(
        asset_id,
        start_time=start_time,
        end_time=end_time,
        window_minutes=window_minutes,
    )

    record_audit_event(
        action="telemetry.asset.summary.read",
        entity_type="asset",
        entity_id=asset_id,
        actor=actor_from_user(user),
        outcome="allowed",
        reason="asset telemetry summary read",
        metadata={
            "start_time": response.start_time,
            "end_time": response.end_time,
            "window_minutes": response.window_minutes,
            "summary_count": len(response.summaries),
            "storage_backend": response.storage_backend,
            "timescale_hypertable_enabled": response.timescale_hypertable_enabled,
        },
    )

    return response