from __future__ import annotations

from pydantic import BaseModel, Field


class VerifiedAskRequest(BaseModel):
    question: str
    asset_ids: list[str] = Field(default_factory=list)
    top_k: int = 5
    include_obsolete: bool = False


class VerifiedEvidenceCitation(BaseModel):
    evidence_id: str
    document_id: str
    page: int
    section: str | None = None
    revision: int
    quote: str
    confidence: float
    source_quality: float
    approval_status: str
    is_obsolete: bool = False


class ContradictoryEvidence(BaseModel):
    evidence_id: str
    reason: str
    quote: str


class VerifiedAskResponse(BaseModel):
    request_id: str
    question: str
    direct_answer: str
    confidence: float
    answer_status: str
    grounded: bool
    citations_verified: bool
    evidence: list[VerifiedEvidenceCitation] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    contradictory_evidence: list[ContradictoryEvidence] = Field(default_factory=list)
    recommended_next_action: str
    unsupported_claims: list[str] = Field(default_factory=list)