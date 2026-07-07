from fastapi import APIRouter

from apps.api.services.data_loader import (
    get_assets,
    get_compliance_matrix,
    get_dashboard_summary,
    get_health_scores,
    get_maintenance_events,
)

from apps.api.services.operations_summary_service import (
    get_operations_summary,
)


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary():
    return get_dashboard_summary()


@router.get("/overview")
def get_dashboard_overview():
    assets = get_assets()
    health_scores = get_health_scores()
    compliance = get_compliance_matrix()
    events = get_maintenance_events()
    summary = get_dashboard_summary()

    return {
        "summary": summary,
        "assets": assets,
        "health_scores": health_scores,
        "asset_compliance_summary": compliance.get("asset_compliance_summary", []),
        "top_maintenance_events": events[:5],
    }

@router.get("/operations-summary")
def get_dashboard_operations_summary():
    return get_operations_summary()
