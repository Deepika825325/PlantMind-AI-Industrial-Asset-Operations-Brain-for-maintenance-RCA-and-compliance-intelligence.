from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_loader import get_asset_by_id, get_assets, get_health_scores


router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("")
def list_assets(
    risk_level: str | None = Query(default=None),
    asset_type: str | None = Query(default=None)
):
    assets = get_assets()

    if risk_level:
        assets = [
            asset for asset in assets
            if asset.get("risk_level", "").lower() == risk_level.lower()
        ]

    if asset_type:
        assets = [
            asset for asset in assets
            if asset.get("asset_type", "").lower() == asset_type.lower()
        ]

    return {
        "total": len(assets),
        "assets": assets
    }


@router.get("/health-scores")
def list_health_scores():
    health_scores = get_health_scores()

    return {
        "total": len(health_scores),
        "health_scores": health_scores
    }


@router.get("/{asset_id}")
def get_asset(asset_id: str):
    asset = get_asset_by_id(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")

    return asset


@router.get("/{asset_id}/health")
def get_asset_health(asset_id: str):
    asset_id = asset_id.upper()
    health_scores = get_health_scores()

    for health in health_scores:
        if health.get("asset_id") == asset_id:
            return health

    raise HTTPException(status_code=404, detail=f"Health score not found for asset: {asset_id}")