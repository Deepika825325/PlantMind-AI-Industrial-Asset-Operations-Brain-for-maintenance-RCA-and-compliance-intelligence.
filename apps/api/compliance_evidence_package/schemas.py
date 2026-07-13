from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


EvidenceStatus = Literal[
    "satisfied",
    "failed",
    "missing",
    "warning",
    "not_applicable",
]

AuditReadinessStatus = Literal[
    "ready",
    "partially_ready",
    "blocked",
]

EvidenceSourceType = Literal[
    "document",
    "work_order",
    "approval",
    "post_maintenance_verification",
    "decision",
    "compliance_rule",
]


class AuditEvidenceReference(BaseModel):
    evidence_id: str
    source_type: EvidenceSourceType
    title: str
    status: EvidenceStatus = "satisfied"
    source_id: str | None = None
    immutable_hash: str | None = None
    explanation: str


class ComplianceRequirementPackage(BaseModel):
    requirement_id: str
    title: str
    category: str
    severity: Literal[
        "critical",
        "high",
        "medium",
        "low",
    ] = "medium"
    status: EvidenceStatus
    explanation: str
    applicable_documents: list[AuditEvidenceReference] = Field(
        default_factory=list
    )
    completed_work_orders: list[AuditEvidenceReference] = Field(
        default_factory=list
    )
    approvals: list[AuditEvidenceReference] = Field(
        default_factory=list
    )
    post_maintenance_verifications: list[AuditEvidenceReference] = Field(
        default_factory=list
    )
    missing_evidence: list[AuditEvidenceReference] = Field(
        default_factory=list
    )
    decision_history: list[AuditEvidenceReference] = Field(
        default_factory=list
    )
    readiness_impact: str


class ComplianceAuditPackageSummary(BaseModel):
    asset_id: str
    package_id: str
    package_version: str
    generated_at: str
    readiness_status: AuditReadinessStatus
    readiness_score: float
    requirement_count: int
    satisfied_count: int
    failed_count: int
    missing_count: int
    warning_count: int
    immutable_evidence_hash: str


class ComplianceAuditPackage(BaseModel):
    summary: ComplianceAuditPackageSummary
    requirements: list[ComplianceRequirementPackage]
    applicable_documents: list[AuditEvidenceReference]
    completed_work_orders: list[AuditEvidenceReference]
    approvals: list[AuditEvidenceReference]
    post_maintenance_verifications: list[AuditEvidenceReference]
    missing_evidence: list[AuditEvidenceReference]
    decision_history: list[AuditEvidenceReference]
    failed_requirement_explanations: list[str]
    package_notes: list[str]