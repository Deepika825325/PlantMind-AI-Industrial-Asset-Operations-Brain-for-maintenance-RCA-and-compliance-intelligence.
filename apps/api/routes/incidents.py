from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.auth.dependencies import require_permission
from apps.api.incidents.schemas import (
    CreateIncidentRequest,
    IncidentCreateResponse,
    IncidentListResponse,
    IncidentStatisticsResponse,
    IndustrialIncident,
    LinkIncidentRcaRequest,
    UpdateIncidentStatusRequest,
)
from apps.api.incidents.service import IncidentManagementService


router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)

incident_service = IncidentManagementService()


@router.post(
    "",
    response_model=IncidentCreateResponse,
)
def create_incident(
    request: CreateIncidentRequest,
    user=Depends(require_permission("evidence.write")),
) -> IncidentCreateResponse:
    return incident_service.create_from_source(
        request
    )


@router.get(
    "",
    response_model=IncidentListResponse,
)
def list_incidents(
    asset_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    user=Depends(require_permission("document.read")),
) -> IncidentListResponse:
    return incident_service.list_incidents(
        asset_id=asset_id,
        status=status,
    )


@router.get(
    "/statistics",
    response_model=IncidentStatisticsResponse,
)
def get_incident_statistics(
    user=Depends(require_permission("document.read")),
) -> IncidentStatisticsResponse:
    return incident_service.statistics()


@router.get(
    "/{incident_id}",
    response_model=IndustrialIncident,
)
def get_incident(
    incident_id: str,
    user=Depends(require_permission("document.read")),
) -> IndustrialIncident:
    incident = incident_service.get_incident(
        incident_id
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    return incident


@router.post(
    "/{incident_id}/status",
    response_model=IndustrialIncident,
)
def update_incident_status(
    incident_id: str,
    request: UpdateIncidentStatusRequest,
    user=Depends(require_permission("evidence.write")),
) -> IndustrialIncident:
    incident = incident_service.update_status(
        incident_id=incident_id,
        request=request,
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    return incident


@router.post(
    "/{incident_id}/rca",
    response_model=IndustrialIncident,
)
def link_incident_rca(
    incident_id: str,
    request: LinkIncidentRcaRequest,
    user=Depends(require_permission("evidence.write")),
) -> IndustrialIncident:
    incident = incident_service.link_rca(
        incident_id=incident_id,
        request=request,
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    return incident