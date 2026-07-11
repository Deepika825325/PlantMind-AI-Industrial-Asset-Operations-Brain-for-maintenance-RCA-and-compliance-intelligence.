from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


AnomalySeverity = Literal[
    "info",
    "warning",
    "critical",
]

AnomalyRuleType = Literal[
    "threshold_breach",
    "rate_of_change_breach",
    "persistence_rule",
    "missing_signal",
    "stuck_sensor",
    "impossible_value",
    "combined_signal_rule",
]


class TelemetryRecordForRules(BaseModel):
    sequence: int
    timestamp: str
    asset_id: str
    vibration_mm_s: float | None = None
    bearing_temperature_deg_c: float | None = None
    motor_current_a: float | None = None
    rpm: float | None = None
    health_score: float | None = None
    anomaly_score: float | None = None
    data_quality: str = "unknown"
    scenario: str | None = None


class AnomalyRuleDefinition(BaseModel):
    rule_id: str
    rule_version: str
    rule_type: AnomalyRuleType
    name: str
    severity: AnomalySeverity
    description: str
    condition: str
    enabled: bool = True


class AnomalyRecord(BaseModel):
    anomaly_id: str
    rule_id: str
    rule_version: str
    rule_type: AnomalyRuleType
    severity: AnomalySeverity
    asset_id: str
    timestamp: str
    sequence: int
    metric: str
    observed_value: float | None = None
    threshold: float | None = None
    message: str
    deduplication_key: str
    contributing_records: list[int] = Field(default_factory=list)


class AnomalyEvaluationRequest(BaseModel):
    asset_id: str = "P-101"
    records: list[TelemetryRecordForRules]
    suppress_duplicates: bool = True


class AnomalyEvaluationResponse(BaseModel):
    asset_id: str
    rule_version: str
    evaluated_record_count: int
    rules_evaluated: int
    anomaly_count: int
    duplicate_alerts_suppressed: int
    anomalies: list[AnomalyRecord] = Field(default_factory=list)


class AssetAnomalyHistoryResponse(BaseModel):
    asset_id: str
    rule_version: str
    anomaly_count: int
    anomalies: list[AnomalyRecord] = Field(default_factory=list)


class RuleCatalogResponse(BaseModel):
    rule_version: str
    total_rules: int
    rules: list[AnomalyRuleDefinition]