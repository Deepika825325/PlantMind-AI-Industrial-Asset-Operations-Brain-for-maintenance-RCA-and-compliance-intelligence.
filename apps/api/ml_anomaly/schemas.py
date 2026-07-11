from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


MlAnomalyLabel = Literal[
    "normal",
    "warning",
    "critical",
]


class MlTelemetryRecord(BaseModel):
    sequence: int
    timestamp: str
    asset_id: str = "P-101"
    vibration_mm_s: float
    bearing_temperature_deg_c: float
    motor_current_a: float
    rpm: float
    health_score: float | None = None
    anomaly_score: float | None = None
    data_quality: str = "good"


class MlAnomalyPredictionRequest(BaseModel):
    asset_id: str = "P-101"
    records: list[MlTelemetryRecord]
    window_size: int = Field(default=6, ge=3, le=60)


class ContributingFeature(BaseModel):
    feature_name: str
    feature_value: float
    baseline_value: float
    normalized_deviation: float
    contribution: float


class MlAnomalyPrediction(BaseModel):
    prediction_id: str
    asset_id: str
    sequence: int
    prediction_timestamp: str
    model_version: str
    feature_version: str
    threshold_version: str
    anomaly_score: float
    anomaly_label: MlAnomalyLabel
    contributing_features: list[ContributingFeature]
    prediction_latency_ms: float


class MlAnomalyPredictionResponse(BaseModel):
    asset_id: str
    model_version: str
    feature_version: str
    threshold_version: str
    prediction_count: int
    predictions: list[MlAnomalyPrediction]


class MlModelCardResponse(BaseModel):
    model_name: str
    model_version: str
    feature_version: str
    threshold_version: str
    asset_id: str
    model_type: str
    training_source: str
    live_plant_connected: bool
    input_features: list[str]
    warning_threshold: float
    critical_threshold: float
    reproducible: bool


class MlPredictionHistoryResponse(BaseModel):
    asset_id: str
    model_version: str
    prediction_count: int
    predictions: list[MlAnomalyPrediction]