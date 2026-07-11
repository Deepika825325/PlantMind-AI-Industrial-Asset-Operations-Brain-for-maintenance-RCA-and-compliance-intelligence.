from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.auth.dependencies import require_permission
from apps.api.ml_anomaly.schemas import (
    MlAnomalyPredictionRequest,
    MlAnomalyPredictionResponse,
    MlModelCardResponse,
    MlPredictionHistoryResponse,
)
from apps.api.ml_anomaly.service import P101MultivariateAnomalyModel


router = APIRouter(
    prefix="/ml-anomalies",
    tags=["ml-anomalies"],
)

ml_anomaly_model = P101MultivariateAnomalyModel()


@router.get(
    "/model",
    response_model=MlModelCardResponse,
)
def get_ml_anomaly_model_card(
    user=Depends(require_permission("document.read")),
) -> MlModelCardResponse:
    return ml_anomaly_model.model_card()


@router.post(
    "/predict",
    response_model=MlAnomalyPredictionResponse,
)
def predict_ml_anomalies(
    request: MlAnomalyPredictionRequest,
    user=Depends(require_permission("evidence.write")),
) -> MlAnomalyPredictionResponse:
    return ml_anomaly_model.predict(
        request
    )


@router.get(
    "/assets/{asset_id}/predictions",
    response_model=MlPredictionHistoryResponse,
)
def get_asset_ml_predictions(
    asset_id: str,
    user=Depends(require_permission("document.read")),
) -> MlPredictionHistoryResponse:
    return ml_anomaly_model.prediction_history(
        asset_id
    )