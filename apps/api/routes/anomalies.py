from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.anomaly_rules.schemas import (
    AnomalyEvaluationRequest,
    AnomalyEvaluationResponse,
    AssetAnomalyHistoryResponse,
    RuleCatalogResponse,
)
from apps.api.anomaly_rules.service import AnomalyRuleService
from apps.api.auth.dependencies import require_permission


router = APIRouter(
    prefix="/anomalies",
    tags=["anomalies"],
)

anomaly_rule_service = AnomalyRuleService()


@router.get(
    "/rules",
    response_model=RuleCatalogResponse,
)
def list_anomaly_rules(
    user=Depends(require_permission("document.read")),
) -> RuleCatalogResponse:
    return anomaly_rule_service.list_rules()


@router.post(
    "/evaluate",
    response_model=AnomalyEvaluationResponse,
)
def evaluate_anomaly_rules(
    request: AnomalyEvaluationRequest,
    user=Depends(require_permission("evidence.write")),
) -> AnomalyEvaluationResponse:
    return anomaly_rule_service.evaluate(
        request
    )


@router.get(
    "/assets/{asset_id}",
    response_model=AssetAnomalyHistoryResponse,
)
def get_asset_anomaly_history(
    asset_id: str,
    user=Depends(require_permission("document.read")),
) -> AssetAnomalyHistoryResponse:
    return anomaly_rule_service.get_asset_history(
        asset_id
    )