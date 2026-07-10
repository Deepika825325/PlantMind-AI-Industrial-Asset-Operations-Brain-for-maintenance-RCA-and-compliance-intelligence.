from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from apps.api.hybrid_retrieval.schemas import (
    HybridRetrievalSearchRequest,
)
from apps.api.hybrid_retrieval.service import HybridRetrievalService
from apps.api.verified_ask.schemas import (
    ContradictoryEvidence,
    VerifiedAskRequest,
    VerifiedAskResponse,
    VerifiedEvidenceCitation,
)


QUESTION_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9-]+")

NEGATIVE_PATTERNS = [
    r"\bno evidence\b",
    r"\bnot observed\b",
    r"\bnormal\b",
    r"\bwithin limit\b",
    r"\bno abnormal\b",
]

RISK_PATTERNS = [
    r"\bincreased\b",
    r"\bhigh\b",
    r"\babnormal\b",
    r"\bmissing\b",
    r"\boverdue\b",
    r"\bfailure\b",
    r"\bdegradation\b",
]


@dataclass(frozen=True)
class VerifiedAskConfig:
    minimum_supported_score: float = 0.18
    maximum_quote_chars: int = 420


class VerifiedAskService:
    def __init__(
        self,
        retrieval_service: HybridRetrievalService,
        config: VerifiedAskConfig | None = None,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.config = config or VerifiedAskConfig()

    def answer(
        self,
        request: VerifiedAskRequest,
    ) -> VerifiedAskResponse:
        request_id = str(
            uuid.uuid4()
        )

        retrieval_response = self.retrieval_service.search(
            HybridRetrievalSearchRequest(
                query=request.question,
                mode="hybrid",
                asset_ids=request.asset_ids,
                include_obsolete=request.include_obsolete,
                top_k=request.top_k,
            )
        )

        supported_hits = [
            hit
            for hit in retrieval_response.hits
            if hit.hybrid_score >= self.config.minimum_supported_score
        ]

        if not supported_hits:
            return self._safe_answer(
                request=request,
                request_id=request_id,
            )

        evidence = [
            VerifiedEvidenceCitation(
                evidence_id=f"EVID-{index + 1:03d}",
                document_id=hit.metadata.document_id,
                page=hit.metadata.page,
                section=hit.metadata.section,
                revision=hit.metadata.revision,
                quote=self._trim_quote(
                    hit.text
                ),
                confidence=min(
                    1.0,
                    max(
                        0.0,
                        hit.hybrid_score,
                    ),
                ),
                source_quality=hit.metadata.source_quality,
                approval_status=hit.metadata.approval_status,
                is_obsolete=hit.metadata.is_obsolete,
            )
            for index, hit in enumerate(
                supported_hits
            )
        ]

        contradictory_evidence = self._detect_contradictions(
            evidence,
        )

        missing_information = self._missing_information(
            question=request.question,
            evidence=evidence,
        )

        confidence = self._overall_confidence(
            evidence=evidence,
            contradictory_evidence=contradictory_evidence,
            missing_information=missing_information,
        )

        direct_answer = self._compose_grounded_answer(
            request=request,
            evidence=evidence,
            contradictory_evidence=contradictory_evidence,
        )

        return VerifiedAskResponse(
            request_id=request_id,
            question=request.question,
            direct_answer=direct_answer,
            confidence=confidence,
            answer_status="supported",
            grounded=True,
            citations_verified=True,
            evidence=evidence,
            missing_information=missing_information,
            contradictory_evidence=contradictory_evidence,
            recommended_next_action=self._recommended_next_action(
                evidence=evidence,
                contradictory_evidence=contradictory_evidence,
                missing_information=missing_information,
            ),
            unsupported_claims=[],
        )

    def _safe_answer(
        self,
        request: VerifiedAskRequest,
        request_id: str,
    ) -> VerifiedAskResponse:
        return VerifiedAskResponse(
            request_id=request_id,
            question=request.question,
            direct_answer=(
                "I cannot confirm this from the currently indexed "
                "PlantMind evidence. No factual answer has been generated "
                "because supporting citations were not found."
            ),
            confidence=0.0,
            answer_status="insufficient_evidence",
            grounded=False,
            citations_verified=True,
            evidence=[],
            missing_information=[
                "No retrieved document chunk met the minimum evidence score.",
                "Upload or index a relevant approved document before using this answer operationally.",
            ],
            contradictory_evidence=[],
            recommended_next_action=(
                "Add the relevant approved procedure, inspection report, "
                "or RCA evidence to the document index and rerun Ask PlantMind."
            ),
            unsupported_claims=[],
        )

    def _compose_grounded_answer(
        self,
        request: VerifiedAskRequest,
        evidence: list[VerifiedEvidenceCitation],
        contradictory_evidence: list[ContradictoryEvidence],
    ) -> str:
        primary = evidence[0]

        asset_context = (
            f" for {', '.join(request.asset_ids)}"
            if request.asset_ids
            else ""
        )

        answer = (
            f"Based on the verified PlantMind evidence{asset_context}, "
            f"the strongest cited source says: {primary.quote}"
        )

        if len(evidence) > 1:
            answer += (
                f" This is supported by {len(evidence)} retrieved citations."
            )

        if contradictory_evidence:
            answer += (
                " However, possible contradictory evidence was also found, "
                "so this should be reviewed before operational approval."
            )

        return answer

    def _detect_contradictions(
        self,
        evidence: list[VerifiedEvidenceCitation],
    ) -> list[ContradictoryEvidence]:
        has_negative = any(
            self._matches_any_pattern(
                citation.quote,
                NEGATIVE_PATTERNS,
            )
            for citation in evidence
        )

        has_risk = any(
            self._matches_any_pattern(
                citation.quote,
                RISK_PATTERNS,
            )
            for citation in evidence
        )

        if not (
            has_negative and has_risk
        ):
            return []

        contradictions: list[ContradictoryEvidence] = []

        for citation in evidence:
            if self._matches_any_pattern(
                citation.quote,
                NEGATIVE_PATTERNS,
            ):
                contradictions.append(
                    ContradictoryEvidence(
                        evidence_id=citation.evidence_id,
                        reason=(
                            "This citation contains normal/no-evidence language "
                            "while other citations indicate abnormal or risk-related conditions."
                        ),
                        quote=citation.quote,
                    )
                )

        return contradictions

    def _missing_information(
        self,
        question: str,
        evidence: list[VerifiedEvidenceCitation],
    ) -> list[str]:
        question_terms = self._important_terms(
            question,
        )

        evidence_text = " ".join(
            citation.quote
            for citation in evidence
        ).lower()

        missing_terms = [
            term
            for term in question_terms
            if term not in evidence_text
        ]

        if not missing_terms:
            return []

        return [
            "Evidence did not explicitly cover these question terms: "
            + ", ".join(missing_terms[:8])
        ]

    def _important_terms(
        self,
        text: str,
    ) -> list[str]:
        stopwords = {
            "what",
            "why",
            "how",
            "is",
            "are",
            "the",
            "a",
            "an",
            "for",
            "to",
            "of",
            "and",
            "or",
            "in",
            "on",
            "with",
            "from",
            "does",
            "do",
            "this",
            "that",
            "plantmind",
        }

        terms = [
            token.lower()
            for token in QUESTION_TOKEN_PATTERN.findall(text)
            if len(token) >= 3
        ]

        return [
            term
            for term in terms
            if term not in stopwords
        ]

    def _overall_confidence(
        self,
        evidence: list[VerifiedEvidenceCitation],
        contradictory_evidence: list[ContradictoryEvidence],
        missing_information: list[str],
    ) -> float:
        if not evidence:
            return 0.0

        confidence = sum(
            citation.confidence * citation.source_quality
            for citation in evidence
        ) / len(evidence)

        if contradictory_evidence:
            confidence *= 0.75

        if missing_information:
            confidence *= 0.85

        return round(
            max(
                0.0,
                min(
                    1.0,
                    confidence,
                ),
            ),
            4,
        )

    def _recommended_next_action(
        self,
        evidence: list[VerifiedEvidenceCitation],
        contradictory_evidence: list[ContradictoryEvidence],
        missing_information: list[str],
    ) -> str:
        if contradictory_evidence:
            return (
                "Review contradictory evidence with maintenance or reliability engineering "
                "before approving the recommendation."
            )

        if missing_information:
            return (
                "Use the cited evidence as a starting point, but collect the missing "
                "information before final operational approval."
            )

        if any(
            citation.is_obsolete
            for citation in evidence
        ):
            return (
                "Do not use obsolete evidence for approval; retrieve the latest approved revision."
            )

        return (
            "Use the cited document pages as the evidence trail and proceed with engineering review."
        )

    def _trim_quote(
        self,
        text: str,
    ) -> str:
        normalized = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if len(normalized) <= self.config.maximum_quote_chars:
            return normalized

        return normalized[
            : self.config.maximum_quote_chars
        ].rstrip() + "..."

    def _matches_any_pattern(
        self,
        text: str,
        patterns: list[str],
    ) -> bool:
        return any(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
            for pattern in patterns
        )