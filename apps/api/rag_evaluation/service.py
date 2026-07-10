from __future__ import annotations

import re
from datetime import datetime, timezone

from apps.api.rag_answering.schemas import RagAnswerRequest
from apps.api.rag_answering.service import IngestionRagAnsweringService
from apps.api.rag_evaluation.schemas import (
    RagBenchmarkCaseResult,
    RagBenchmarkQuestion,
    RagEvaluationReport,
    RagEvaluationSummary,
)


class RagEvaluationService:
    def __init__(
        self,
        rag_answering_service: IngestionRagAnsweringService,
    ) -> None:
        self.rag_answering_service = rag_answering_service

    def evaluate_questions(
        self,
        questions: list[RagBenchmarkQuestion],
    ) -> RagEvaluationReport:
        results = [
            self._evaluate_question(
                question,
            )
            for question in questions
        ]

        summary = self._summary(
            results,
        )

        return RagEvaluationReport(
            evaluation_id=self._evaluation_id(),
            generated_at=datetime.now(
                timezone.utc,
            ).isoformat(),
            summary=summary,
            results=results,
        )

    def _evaluate_question(
        self,
        benchmark: RagBenchmarkQuestion,
    ) -> RagBenchmarkCaseResult:
        answer = self.rag_answering_service.answer_question(
            RagAnswerRequest(
                question=benchmark.question,
                asset_id=benchmark.asset_id,
                document_type=benchmark.document_type,
            )
        )

        answer_text = self._normalized_answer_text(
            answer.answer,
            [
                citation.quoted_text
                for citation in answer.citations
            ],
            answer.quality.matched_query_terms,
        )

        expected_terms = [
            term.lower()
            for term in benchmark.expected_terms
        ]

        matched_expected_terms = sorted(
            {
                term
                for term in expected_terms
                if term in answer_text
            }
        )

        missing_expected_terms = sorted(
            {
                term
                for term in expected_terms
                if term not in answer_text
            }
        )

        passed = (
            answer.retrieval_status == "answered_with_ingested_context"
            and answer.quality.grounded
            and answer.quality.quality_score >= benchmark.minimum_quality_score
            and answer.quality.query_coverage >= benchmark.minimum_query_coverage
            and not missing_expected_terms
        )

        warnings = list(
            answer.quality.warnings,
        )

        if missing_expected_terms:
            warnings.append(
                "missing_expected_terms",
            )

        if answer.quality.quality_score < benchmark.minimum_quality_score:
            warnings.append(
                "quality_score_below_threshold",
            )

        if answer.quality.query_coverage < benchmark.minimum_query_coverage:
            warnings.append(
                "query_coverage_below_threshold",
            )

        return RagBenchmarkCaseResult(
            question_id=benchmark.question_id,
            question=benchmark.question,
            asset_id=benchmark.asset_id,
            passed=passed,
            retrieval_status=answer.retrieval_status,
            grounded=answer.quality.grounded,
            confidence=answer.confidence,
            quality_score=answer.quality.quality_score,
            query_coverage=answer.quality.query_coverage,
            total_citations=answer.total_citations,
            matched_expected_terms=matched_expected_terms,
            missing_expected_terms=missing_expected_terms,
            warnings=sorted(
                set(warnings),
            ),
        )

    def _summary(
        self,
        results: list[RagBenchmarkCaseResult],
    ) -> RagEvaluationSummary:
        total = len(results)
        passed = sum(
            1
            for result in results
            if result.passed
        )
        failed = total - passed

        return RagEvaluationSummary(
            total_questions=total,
            passed_questions=passed,
            failed_questions=failed,
            pass_rate=self._average(
                [1.0 if result.passed else 0.0 for result in results],
            ),
            average_confidence=self._average(
                [result.confidence for result in results],
            ),
            average_quality_score=self._average(
                [result.quality_score for result in results],
            ),
            average_query_coverage=self._average(
                [result.query_coverage for result in results],
            ),
        )

    def _normalized_answer_text(
        self,
        answer: str,
        quoted_texts: list[str],
        matched_terms: list[str],
    ) -> str:
        combined = " ".join(
            [answer]
            + quoted_texts
            + matched_terms
        ).lower()

        return re.sub(
            r"\s+",
            " ",
            combined,
        )

    def _average(
        self,
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            4,
        )

    def _evaluation_id(
        self,
    ) -> str:
        timestamp = datetime.now(
            timezone.utc,
        ).strftime("%Y%m%d%H%M%S%f")

        return f"RAG-EVAL-{timestamp}"