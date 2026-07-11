from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.asset_health.schemas import (
    AssetHealthHistoryResponse,
    AssetHealthModelCard,
    AssetHealthReplayRequest,
    AssetHealthReplayResponse,
    AssetHealthScoreRequest,
    AssetHealthScoreResponse,
)
from apps.api.asset_health.service import ExplainableAssetHealthScorer
from apps.api.auth.dependencies import require_permission


router = APIRouter(
    prefix="/asset-health",
    tags=["asset-health"],
)

asset_health_scorer = ExplainableAssetHealthScorer()


@router.get(
    "/model",
    response_model=AssetHealthModelCard,
)
def get_asset_health_model(
    user=Depends(require_permission("document.read")),
) -> AssetHealthModelCard:
    return asset_health_scorer.model_card()


@router.post(
    "/score",
    response_model=AssetHealthScoreResponse,
)
def score_asset_health(
    request: AssetHealthScoreRequest,
    user=Depends(require_permission("evidence.write")),
) -> AssetHealthScoreResponse:
    return asset_health_scorer.score(
        request
    )


@router.post(
    "/replay",
    response_model=AssetHealthReplayResponse,
)
def score_asset_health_replay(
    request: AssetHealthReplayRequest,
    user=Depends(require_permission("evidence.write")),
) -> AssetHealthReplayResponse:
    return asset_health_scorer.replay(
        request
    )


@router.get(
    "/assets/{asset_id}/history",
    response_model=AssetHealthHistoryResponse,
)
def get_asset_health_history(
    asset_id: str,
    user=Depends(require_permission("document.read")),
) -> AssetHealthHistoryResponse:
    return asset_health_scorer.history(
        asset_id
    )