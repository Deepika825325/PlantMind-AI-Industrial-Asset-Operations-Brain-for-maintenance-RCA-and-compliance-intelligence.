from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.auth.dependencies import require_permission
from apps.api.simulations.schemas import (
    SimulationCreateRequest,
    SimulationResponse,
    SimulationSpeedRequest,
)
from apps.api.simulations.service import SimulationService


router = APIRouter(
    prefix="/simulations",
    tags=["simulations"],
)

simulation_service = SimulationService()


@router.post(
    "",
    response_model=SimulationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_simulation(
    request: SimulationCreateRequest,
    user=Depends(require_permission("evidence.write")),
) -> SimulationResponse:
    return simulation_service.create_simulation(
        request
    )


@router.post(
    "/{simulation_id}/start",
    response_model=SimulationResponse,
)
def start_simulation(
    simulation_id: str,
    user=Depends(require_permission("evidence.write")),
) -> SimulationResponse:
    try:
        return simulation_service.start_simulation(
            simulation_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{simulation_id}/pause",
    response_model=SimulationResponse,
)
def pause_simulation(
    simulation_id: str,
    user=Depends(require_permission("evidence.write")),
) -> SimulationResponse:
    try:
        return simulation_service.pause_simulation(
            simulation_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{simulation_id}/resume",
    response_model=SimulationResponse,
)
def resume_simulation(
    simulation_id: str,
    user=Depends(require_permission("evidence.write")),
) -> SimulationResponse:
    try:
        return simulation_service.resume_simulation(
            simulation_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{simulation_id}/reset",
    response_model=SimulationResponse,
)
def reset_simulation(
    simulation_id: str,
    user=Depends(require_permission("evidence.write")),
) -> SimulationResponse:
    try:
        return simulation_service.reset_simulation(
            simulation_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{simulation_id}/speed",
    response_model=SimulationResponse,
)
def set_simulation_speed(
    simulation_id: str,
    request: SimulationSpeedRequest,
    user=Depends(require_permission("evidence.write")),
) -> SimulationResponse:
    try:
        return simulation_service.set_speed(
            simulation_id,
            request,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{simulation_id}",
    response_model=SimulationResponse,
)
def get_simulation(
    simulation_id: str,
    user=Depends(require_permission("document.read")),
) -> SimulationResponse:
    try:
        return simulation_service.get_simulation(
            simulation_id
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc