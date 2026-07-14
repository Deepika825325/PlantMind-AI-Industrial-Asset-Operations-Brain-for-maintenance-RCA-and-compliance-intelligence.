from __future__ import annotations

from fastapi import APIRouter

from apps.api.demo_closed_loop.schemas import (
    P101AnomalyExplanation,
    P101ClosedLoopRunResponse,
    P101ClosedLoopState,
    P101ClosedLoopTimelineResponse,
)
from apps.api.demo_closed_loop.service import (
    P101ClosedLoopDemoService,
)


router = APIRouter(
    prefix="/demo/p101",
    tags=["demo-p101"],
)

demo_service = P101ClosedLoopDemoService()


@router.post(
    "/reset",
    response_model=P101ClosedLoopState,
)
def reset_p101_closed_loop_demo() -> P101ClosedLoopState:
    return demo_service.reset()


@router.post(
    "/run-closed-loop",
    response_model=P101ClosedLoopRunResponse,
)
def run_p101_closed_loop_demo() -> P101ClosedLoopRunResponse:
    return demo_service.run_closed_loop()


@router.get(
    "/status",
    response_model=P101ClosedLoopState,
)
def get_p101_closed_loop_status() -> P101ClosedLoopState:
    return demo_service.status()


@router.get(
    "/timeline",
    response_model=P101ClosedLoopTimelineResponse,
)
def get_p101_closed_loop_timeline() -> P101ClosedLoopTimelineResponse:
    return demo_service.timeline()


@router.get(
    "/anomaly-explanation",
    response_model=P101AnomalyExplanation,
)
def get_p101_anomaly_explanation() -> P101AnomalyExplanation:
    return demo_service.anomaly_explanation()
