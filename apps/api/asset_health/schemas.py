from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


HealthFactorName = Literal[
    "sensor_anomaly_score",
    "failure_probability",
    "open_incident_severity",
    "work_order_status",
    "compliance_risk",
    "asset_criticality",
    "recent_failure_history",
    "sensor_quality",
]

HealthBand = Literal[
    "healthy",
    "watch",
    "degraded",
    "critical",
]

SeverityLevel = Literal[
    "none",
    "low",
    "medium",
    "high",
    "critical",
]

AssetCriticality = Literal[
    "low",
    "medium",
    "high",
    "critical",
]

ReplayState = Literal[
    "normal_operation",
    "bearing_degradation",
    "shaft_misalignment",
    "cavitation",
    "sensor_failure",
    "maintenance_recovery",
]


class AssetHealthInput(BaseModel):
    asset_id: str = "P-101"
    timestamp: str
    sensor_anomaly_score: float = Field(ge=0, le=1)
    failure_probability: float = Field(ge=0, le=1)
    open_incident_severity: SeverityLevel = "none"
    open_work_orders: int = Field(default=0, ge=0)
    overdue_work_orders: int = Field(default=0, ge=0)
    compliance_risk_score: float = Field(default=0, ge=0, le=1)
    asset_criticality: AssetCriticality = "high"
    recent_failure_count: int = Field(default=0, ge=0)
    sensor_quality_score: float = Field(default=1, ge=0, le=1)
    replay_state: ReplayState | None = None


class AssetHealthScoreRequest(BaseModel):
    reading: AssetHealthInput


class AssetHealthReplayRequest(BaseModel):
    asset_id: str = "P-101"
    readings: list[AssetHealthInput] = Field(min_length=1)


class HealthFactorContribution(BaseModel):
    factor_name: HealthFactorName
    label: str
    input_value: float | int | str
    risk_points: float
    max_risk_points: float
    contribution_direction: Literal[
        "lowers_health",
        "raises_health",
        "neutral",
    ]
    explanation: str


class HealthScoreDelta(BaseModel):
    previous_score: float | None
    current_score: float
    delta: float
    direction: Literal[
        "improved",
        "declined",
        "unchanged",
        "initial",
    ]
    explanation: str


class AssetHealthScoreResponse(BaseModel):
    asset_id: str
    timestamp: str
    model_version: str
    scoring_method: str
    base_score: float
    health_score: float
    health_band: HealthBand
    total_risk_points: float
    replay_state: ReplayState | None = None
    factor_contributions: list[HealthFactorContribution]
    score_delta: HealthScoreDelta
    explanation: str


class AssetHealthReplayResponse(BaseModel):
    asset_id: str
    model_version: str
    score_count: int
    scores: list[AssetHealthScoreResponse]


class AssetHealthModelCard(BaseModel):
    model_name: str
    model_version: str
    scoring_method: str
    base_score: float
    factor_weights: dict[HealthFactorName, float]
    hidden_score: bool
    notes: list[str]


class AssetHealthHistoryResponse(BaseModel):
    asset_id: str
    model_version: str
    score_count: int
    scores: list[AssetHealthScoreResponse]