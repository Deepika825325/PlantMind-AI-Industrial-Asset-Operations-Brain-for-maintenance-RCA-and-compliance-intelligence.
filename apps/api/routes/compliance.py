from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_loader import get_compliance_matrix


router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.get("")
def get_compliance():
    return get_compliance_matrix()


@router.get("/gaps")
def list_compliance_gaps(
    asset_id: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None)
):
    data = get_compliance_matrix()
    gaps = data.get("gaps", [])

    if asset_id:
        asset_id = asset_id.upper()
        gaps = [
            gap for gap in gaps
            if gap.get("asset_id") == asset_id
        ]

    if severity:
        gaps = [
            gap for gap in gaps
            if gap.get("gap_severity", "").lower() == severity.lower()
        ]

    if status:
        gaps = [
            gap for gap in gaps
            if gap.get("current_status", "").lower() == status.lower()
        ]

    return {
        "total": len(gaps),
        "gaps": gaps
    }


@router.get("/assets/{asset_id}")
def get_asset_compliance(asset_id: str):
    asset_id = asset_id.upper()
    data = get_compliance_matrix()

    summaries = data.get("asset_compliance_summary", [])
    gaps = data.get("gaps", [])

    asset_summary = None

    for summary in summaries:
        if summary.get("asset_id") == asset_id:
            asset_summary = summary
            break

    if not asset_summary:
        raise HTTPException(status_code=404, detail=f"Compliance summary not found for asset: {asset_id}")

    asset_gaps = [
        gap for gap in gaps
        if gap.get("asset_id") == asset_id
    ]

    return {
        "asset_id": asset_id,
        "summary": asset_summary,
        "gaps": asset_gaps
    }