from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


VerificationOutcome = Literal[
    "successful",
    "partially_successful",
    "failed",
    "insufficient_evidence",
]

VerificationMetricStatus = Literal[
    "passed",
    "failed",
    "missing",
]


class TelemetrySnapshot(BaseModel):
    vibration_mm_s: float | None = None
    bearing_temperature_c: float | None = None
    health_score: float | None = None
    anomaly_score: float | None = None
    failure_probability: float | None = None


class VerificationCriteria(BaseModel):
    max_vibration_mm_s: float = 3.5
    max_bearing_temperature_c: float = 75.0
    min_health_score: float = 80.0
    max_anomaly_score: float = 0.3
    max_failure_probability: float = 0.25
    minimum_passed_metrics_for_partial_success: int = 3


class MetricComparison(BaseModel):
    metric_name: str
    pre_value: float | None
    post_value: float | None
    target: float
    status: VerificationMetricStatus
    explanation: str


class PostMaintenanceVerificationRequest(BaseModel):
    work_order_id: str
    asset_id: str = "P-101"
    verification_id: str | None = None
    verified_by: str = "maintenance_engineer"
    verified_at: str
    pre_maintenance: TelemetrySnapshot
    post_maintenance: TelemetrySnapshot
    criteria: VerificationCriteria = Field(default_factory=VerificationCriteria)


class MaintenanceRecoveryReplayRequest(BaseModel):
    work_order_id: str = "WO-P101-COMPLETE-001"
    asset_id: str = "P-101"
    scenario: Literal[
        "successful_recovery",
        "partial_recovery",
        "failed_recovery",
        "insufficient_evidence",
    ] = "successful_recovery"
    verified_by: str = "maintenance_engineer"
    verified_at: str = "2026-07-10T10:00:00+00:00"


class PostMaintenanceVerificationResult(BaseModel):
    verification_id: str
    work_order_id: str
    asset_id: str
    verified_by: str
    verified_at: str
    outcome: VerificationOutcome
    pre_maintenance: TelemetrySnapshot
    post_maintenance: TelemetrySnapshot
    criteria: VerificationCriteria
    metric_comparisons: list[MetricComparison]
    passed_metric_count: int
    failed_metric_count: int
    missing_metric_count: int
    readings_normalized: bool
    can_mark_verified: bool
    should_reopen_work_order: bool
    explanation: str


class PostMaintenanceVerificationHistoryResponse(BaseModel):
    work_order_id: str
    total_verifications: int
    verifications: list[PostMaintenanceVerificationResult]


class VerificationCriteriaResponse(BaseModel):
    default_criteria: VerificationCriteria
    verification_rule: str
    verified_transition_rule: str
    failed_recovery_rule: str