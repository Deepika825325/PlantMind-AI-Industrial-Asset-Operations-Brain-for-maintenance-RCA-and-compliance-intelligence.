from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_loader import get_maintenance_events
from apps.api.services.maintenance_service import (
    filter_work_orders,
    get_asset_work_orders,
    get_maintenance_recommendations,
    get_rca_work_orders,
    get_work_order,
    get_work_order_statistics
)


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
        normalized_asset_id = asset_id.upper()
        events = [
            event
            for event in events
            if event.get("asset_id", "").upper() == normalized_asset_id
        ]

    if status:
        events = [
            event
            for event in events
            if event.get("status", "").lower() == status.lower()
        ]

    if priority:
        events = [
            event
            for event in events
            if event.get("priority", "").lower() == priority.lower()
        ]

    if compliance_related:
        events = [
            event
            for event in events
            if event.get("compliance_related", "").lower()
            == compliance_related.lower()
        ]

    return {
        "total": len(events),
        "events": events
    }


@router.get("/events/{event_id}")
def get_maintenance_event(event_id: str):
    normalized_event_id = event_id.upper()

    for event in get_maintenance_events():
        if event.get("event_id", "").upper() == normalized_event_id:
            return event

    raise HTTPException(
        status_code=404,
        detail=f"Maintenance event not found: {normalized_event_id}"
    )


@router.get("/work-orders")
def list_work_orders(
    asset_id: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    status: str | None = Query(default=None),
    maintenance_type: str | None = Query(default=None),
    rca_case_id: str | None = Query(default=None),
    due_date: str | None = Query(default=None),
    due_before: str | None = Query(default=None),
    due_after: str | None = Query(default=None)
):
    work_orders = filter_work_orders(
        asset_id=asset_id,
        priority=priority,
        status=status,
        maintenance_type=maintenance_type,
        rca_case_id=rca_case_id,
        due_date=due_date,
        due_before=due_before,
        due_after=due_after
    )

    return {
        "total": len(work_orders),
        "work_orders": work_orders,
        "filters": {
            "asset_id": asset_id,
            "priority": priority,
            "status": status,
            "maintenance_type": maintenance_type,
            "rca_case_id": rca_case_id,
            "due_date": due_date,
            "due_before": due_before,
            "due_after": due_after
        }
    }


@router.get("/work-orders/statistics")
def get_work_orders_statistics():
    return get_work_order_statistics()


@router.get("/work-orders/{work_order_id}")
def get_work_order_by_id(work_order_id: str):
    work_order = get_work_order(work_order_id)

    if work_order:
        return work_order

    raise HTTPException(
        status_code=404,
        detail=f"Maintenance work order not found: {work_order_id.upper()}"
    )


@router.get("/assets/{asset_id}/work-orders")
def list_asset_work_orders(asset_id: str):
    work_orders = get_asset_work_orders(asset_id)

    return {
        "asset_id": asset_id.upper(),
        "total": len(work_orders),
        "work_orders": work_orders
    }


@router.get("/rca/{case_id}/work-orders")
def list_rca_work_orders(case_id: str):
    work_orders = get_rca_work_orders(case_id)

    return {
        "rca_case_id": case_id.upper(),
        "total": len(work_orders),
        "work_orders": work_orders
    }


@router.get("/recommendations")
def list_maintenance_recommendations(
    asset_id: str | None = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20)
):
    recommendations = get_maintenance_recommendations(
        asset_id=asset_id,
        limit=limit
    )

    return {
        "total": len(recommendations),
        "asset_id": asset_id.upper() if asset_id else None,
        "recommendations": recommendations
    }