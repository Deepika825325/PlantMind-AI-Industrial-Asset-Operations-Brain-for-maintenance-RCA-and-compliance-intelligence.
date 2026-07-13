from __future__ import annotations

from fastapi import APIRouter, Response

from apps.api.observability.metrics import metrics_store


router = APIRouter(
    tags=["observability"],
)


@router.get(
    "/metrics",
    response_class=Response,
)
def prometheus_metrics() -> Response:
    return Response(
        content=metrics_store.snapshot_prometheus_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@router.get(
    "/observability/health",
)
def observability_health() -> dict[str, str]:
    return {
        "status": "ok",
        "component": "observability",
    }