from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


FailureMode = Literal[
    "healthy",
    "lubrication_degradation",
    "bearing_damage",
    "shaft_misalignment",
    "cavitation",
    "unknown_anomaly",
]


class FailureTelemetryRecord(BaseModel):
    sequence: int
    timestamp: str
    asset_id: str = "P-101"
    vibration_mm_s: float | None = None
    bearing_temperature_deg_c: float | None = None
    motor_current_a: float | None = None
    rpm: float | None = None
    health_score: float | None = None
    anomaly_score: float | None = None
    data_quality: str = "good"
    scenario: str | None = None


class FailureClassificationRequest(BaseModel):
    asset_id: str = "P-101"
    records: list[FailureTelemetryRecord] = Field(min_length=1)


class FeatureEvidence(BaseModel):
    feature_name: str
    feature_value: float | str | None
    expected_pattern: str
    explanation: str


class FailureHypothesis(BaseModel):
    failure_mode: FailureMode
    label: str
    confidence: float = Field(ge=0, le=1)
    supporting_features: list[FeatureEvidence] = Field(default_factory=list)
    contradictory_features: list[FeatureEvidence] = Field(default_factory=list)


class FailureClassificationResponse(BaseModel):
    asset_id: str
    model_version: str
    confidence_method: str
    evaluated_record_count: int
    latest_timestamp: str
    primary_hypothesis: FailureHypothesis
    alternatives: list[FailureHypothesis]


class FailureClassificationModelCard(BaseModel):
    model_name: str
    model_version: str
    model_type: str
    supported_classes: list[FailureMode]
    confidence_method: str
    live_plant_connected: bool
    rul_supported: bool
    notes: list[str]


class FailureClassificationHistoryResponse(BaseModel):
    asset_id: str
    model_version: str
    classification_count: int
    classifications: list[FailureClassificationResponse]