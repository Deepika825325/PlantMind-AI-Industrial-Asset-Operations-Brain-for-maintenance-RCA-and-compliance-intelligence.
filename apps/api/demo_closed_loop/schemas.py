from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DemoStepStatus = Literal[
    "pending",
    "passed",
    "failed",
]


class P101DemoStep(BaseModel):
    step_id: str
    title: str
    status: DemoStepStatus
    description: str
    evidence_used: list[str] = Field(
        default_factory=list
    )
    ai_confidence: float | None = None
    human_approval_required: bool
    linked_endpoint: str
    timestamp: str | None = None


class P101ClosedLoopState(BaseModel):
    demo_id: str
    asset_id: str
    asset_name: str
    status: Literal[
        "not_started",
        "running",
        "completed",
    ]
    current_step: int
    total_steps: int
    completed_steps: int
    summary: str
    judge_message: str
    steps: list[P101DemoStep]


class P101ClosedLoopTimelineResponse(BaseModel):
    demo_id: str
    asset_id: str
    timeline: list[P101DemoStep]


class P101ClosedLoopRunResponse(BaseModel):
    state: P101ClosedLoopState

class P101AnomalySignalContribution(BaseModel):
    signal_name: str
    display_name: str
    baseline_value: float
    observed_value: float
    unit: str
    deviation_percent: float
    contribution_weight: float
    explanation: str


class P101AnomalyExplanation(BaseModel):
    asset_id: str
    model_name: str
    model_version: str
    dataset_version: str
    feature_version: str
    anomaly_label: str
    anomaly_score: float
    confidence: float
    explanation_summary: str
    primary_driver: str
    baseline_window: str
    observation_window: str
    signal_contributions: list[P101AnomalySignalContribution]
    supporting_evidence_ids: list[str]
    model_registry_endpoint: str
    telemetry_endpoint: str
    human_review_required: bool
    human_review_reason: str
    judge_message: str


class P101FailureHypothesis(BaseModel):
    rank: int
    failure_mode: str
    display_name: str
    probability: float
    confidence_label: str
    supporting_signals: list[str]
    supporting_evidence_ids: list[str]
    contradictory_evidence: list[str]
    missing_tests: list[str]
    recommended_next_action: str
    human_approval_required: bool
    decision_reason: str


class P101FailureHypothesisRanking(BaseModel):
    asset_id: str
    rca_case_id: str
    primary_hypothesis: str
    hypotheses: list[P101FailureHypothesis]
    linked_rca_evidence_ids: list[str]
    governance_note: str
    judge_message: str


class P101SopEvidenceItem(BaseModel):
    evidence_id: str
    document_id: str
    document_title: str
    document_type: str
    citation_label: str
    excerpt: str
    relevance: str
    supports_decision: str
    required_action: str
    verification_requirement: str


class P101SopEvidenceResponse(BaseModel):
    asset_id: str
    rca_case_id: str
    question: str
    answer: str
    maintenance_decision: str
    sop_evidence: list[P101SopEvidenceItem]
    inspection_evidence: list[P101SopEvidenceItem]
    incident_evidence: list[P101SopEvidenceItem]
    compliance_evidence: list[P101SopEvidenceItem]
    citation_trail: list[str]
    confidence: float
    rag_status: str
    governance_note: str
    judge_message: str


class P101EvaluationMetric(BaseModel):
    metric_name: str
    display_name: str
    score: float
    status: str
    evidence: list[str]
    judge_readout: str


class P101EvaluationGap(BaseModel):
    gap_id: str
    title: str
    severity: str
    explanation: str
    mitigation: str


class P101EvaluationSummaryResponse(BaseModel):
    asset_id: str
    demo_name: str
    evaluation_version: str
    overall_score: float
    readiness_level: str
    metrics: list[P101EvaluationMetric]
    passed_checks: list[str]
    open_gaps: list[P101EvaluationGap]
    recommended_demo_order: list[str]
    endpoints_validated: list[str]
    governance_note: str
    judge_message: str
