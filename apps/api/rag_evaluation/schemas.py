from __future__ import annotations

from pydantic import BaseModel, Field


class RagBenchmarkQuestion(BaseModel):
    question_id: str
    question: str
    asset_id: str | None = None
    document_type: str | None = None
    expected_terms: list[str] = Field(default_factory=list)
    minimum_quality_score: float = 0.25
    minimum_query_coverage: float = 0.20


class RagEvaluationRequest(BaseModel):
    questions: list[RagBenchmarkQuestion] = Field(default_factory=list)


class RagBenchmarkCaseResult(BaseModel):
    question_id: str
    question: str
    asset_id: str | None = None
    passed: bool
    retrieval_status: str
    grounded: bool
    confidence: float
    quality_score: float
    query_coverage: float
    total_citations: int
    matched_expected_terms: list[str] = Field(default_factory=list)
    missing_expected_terms: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class RagEvaluationSummary(BaseModel):
    total_questions: int
    passed_questions: int
    failed_questions: int
    pass_rate: float
    average_confidence: float
    average_quality_score: float
    average_query_coverage: float


class RagEvaluationReport(BaseModel):
    evaluation_id: str
    generated_at: str
    summary: RagEvaluationSummary
    results: list[RagBenchmarkCaseResult] = Field(default_factory=list)
