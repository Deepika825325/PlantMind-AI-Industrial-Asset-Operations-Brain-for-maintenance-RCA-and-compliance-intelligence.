from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_loader import get_maintenance_events


router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.get("/events")
def list_maintenance_events(
    asset_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    compliance_related: str | None = Query(default=None)
):
    events = get_maintenance_events()

    if asset_id:
        asset_id = asset_id.upper()
        events = [
            event for event in events
            if event.get("asset_id") == asset_id
        ]

    if status:
        events = [
            event for event in events
            if event.get("status", "").lower() == status.lower()
        ]

    if priority:
        events = [
            event for event in events
            if event.get("priority", "").lower() == priority.lower()
        ]

    if compliance_related:
        events = [
            event for event in events
            if event.get("compliance_related", "").lower() == compliance_related.lower()
        ]

    return {
        "total": len(events),
        "events": events
    }


@router.get("/events/{event_id}")
def get_maintenance_event(event_id: str):
    event_id = event_id.upper()

    for event in get_maintenance_events():
        if event.get("event_id") == event_id:
            return event

    raise HTTPException(status_code=404, detail=f"Maintenance event not found: {event_id}")