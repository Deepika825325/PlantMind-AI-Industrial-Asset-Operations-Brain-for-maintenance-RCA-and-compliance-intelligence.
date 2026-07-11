from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


WorkflowStepName = Literal[
    "load_incident",
    "retrieve_telemetry",
    "retrieve_evidence",
    "retrieve_approved_documents",
    "retrieve_similar_cases",
    "generate_candidate_causes",
    "rank_causes",
    "identify_contradictions",
    "identify_missing_tests",
    "draft_rca",
    "request_engineer_approval",
]

EvidenceType = Literal[
    "telemetry",
    "incident",
    "inspection",
    "maintenance",
    "document",
    "similar_case",
    "operator_report",
    "compliance",
]

EvidenceDirection = Literal[
    "supporting",
    "contradictory",
    "context",
    "missing",
]

ApprovalStatus = Literal[
    "approval_required",
    "approved",
    "rejected",
]

CauseRiskLevel = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


class ControlledRcaRequest(BaseModel):
    incident_id: str = "INC-P-101-DEMO"
    asset_id: str = "P-101"
    rca_case_id: str = "RCA-P101-001"
    requested_by: str = "maintenance_engineer"
    include_similar_cases: bool = True


class WorkflowStepResult(BaseModel):
    step_name: WorkflowStepName
    status: Literal["completed", "blocked"]
    explanation: str


class RcaEvidenceItem(BaseModel):
    evidence_id: str
    evidence_type: EvidenceType
    title: str
    summary: str
    source: str
    timestamp: str | None = None
    direction: EvidenceDirection
    reliability: Literal["low", "medium", "high"] = "high"


class CandidateRootCause(BaseModel):
    cause_id: str
    title: str
    description: str
    risk_level: CauseRiskLevel
    rank: int
    confidence: float = Field(ge=0, le=1)
    supporting_evidence_ids: list[str]
    contradictory_evidence_ids: list[str]
    missing_test_ids: list[str]
    explanation: str


class MissingTestRecommendation(BaseModel):
    test_id: str
    title: str
    reason: str
    priority: Literal["low", "medium", "high", "critical"]
    required_before_confirmation: bool = True


class RcaDraft(BaseModel):
    rca_case_id: str
    asset_id: str
    incident_id: str
    title: str
    problem_statement: str
    draft_summary: str
    top_candidate_cause_id: str | None
    recommendations: list[str]
    approval_status: ApprovalStatus
    engineer_approval_required: bool
    auto_confirmation_blocked: bool
    safety_closure_blocked: bool
    critical_work_order_approval_blocked: bool


class ControlledRcaResponse(BaseModel):
    workflow_version: str
    rca_case_id: str
    incident_id: str
    asset_id: str
    steps: list[WorkflowStepResult]
    telemetry_evidence: list[RcaEvidenceItem]
    supporting_evidence: list[RcaEvidenceItem]
    contradictory_evidence: list[RcaEvidenceItem]
    contextual_evidence: list[RcaEvidenceItem]
    candidate_causes: list[CandidateRootCause]
    missing_tests: list[MissingTestRecommendation]
    draft: RcaDraft
    guardrails: list[str]


class RcaApprovalRequest(BaseModel):
    rca_case_id: str
    approved_by: str
    approved_at: str
    decision: Literal["approved", "rejected"]
    note: str | None = None


class RcaApprovalResponse(BaseModel):
    rca_case_id: str
    approval_status: ApprovalStatus
    approved_by: str
    approved_at: str
    note: str | None = None
    confirmation_allowed: bool
    explanation: str


class ControlledRcaHistoryResponse(BaseModel):
    rca_case_id: str
    total_runs: int
    runs: list[ControlledRcaResponse]