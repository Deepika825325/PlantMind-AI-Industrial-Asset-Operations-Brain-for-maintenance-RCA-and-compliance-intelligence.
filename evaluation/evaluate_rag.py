from __future__ import annotations

from time import perf_counter
from typing import Any
import os

from common import (
    EVALUATION_DIR,
    ask_plantmind_api,
    extractive_answer,
    keyword_coverage,
    lexical_retrieve,
    lexical_unsupported_claim_rate,
    load_json,
    load_retrieval_corpus,
    round_metrics,
    set_metrics,
)


def evaluate_rag(
    api_base: str | None = None,
    offline: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    benchmark = load_json(EVALUATION_DIR / "benchmark_questions.json")
    questions = benchmark.get("questions", [])
    corpus = load_retrieval_corpus()
    api_base = api_base or os.getenv("PLANTMIND_API_BASE", "http://127.0.0.1:8000")

    rows: list[dict[str, Any]] = []
    detailed_results: list[dict[str, Any]] = []
    correctness_scores: list[float] = []
    citation_precisions: list[float] = []
    citation_recalls: list[float] = []
    citation_coverages: list[float] = []
    unsupported_rates: list[float] = []
    latencies: list[float] = []
    api_count = 0
    fallback_count = 0

    for question in questions:
        question_text = question["question"]
        started = perf_counter()
        source_mode = "offline_fallback"
        endpoint = ""
        api_error = ""
        support_texts: list[str] = []
        citations: list[str] = []

        if not offline:
            try:
                answer, citations, support_texts, endpoint = ask_plantmind_api(
                    question_text,
                    api_base,
                )
                source_mode = "api"
                api_count += 1
            except RuntimeError as error:
                api_error = str(error)
                retrieved = lexical_retrieve(question_text, corpus)
                answer = extractive_answer(question_text, retrieved)
                citations = [item["source_id"] for item in retrieved]
                support_texts = [item["text"] for item in retrieved]
                fallback_count += 1
        else:
            retrieved = lexical_retrieve(question_text, corpus)
            answer = extractive_answer(question_text, retrieved)
            citations = [item["source_id"] for item in retrieved]
            support_texts = [item["text"] for item in retrieved]
            fallback_count += 1

        latency_seconds = perf_counter() - started
        expected_keywords = question.get("expected_answer_keywords", [])
        expected_citations = question.get("expected_citation_ids", [])
        answer_correctness = keyword_coverage(answer, expected_keywords)
        citation_metrics = set_metrics(expected_citations, citations)
        citation_coverage = 1.0 if expected_citations and citation_metrics["true_positive"] > 0 else 0.0
        unsupported_rate = lexical_unsupported_claim_rate(answer, support_texts)

        correctness_scores.append(answer_correctness)
        citation_precisions.append(citation_metrics["precision"])
        citation_recalls.append(citation_metrics["recall"])
        citation_coverages.append(citation_coverage)
        unsupported_rates.append(unsupported_rate)
        latencies.append(latency_seconds)

        result = {
            "question_id": question["question_id"],
            "category": question["category"],
            "question": question_text,
            "answer": answer,
            "source_mode": source_mode,
            "endpoint": endpoint,
            "citations": citations,
            "expected_citations": expected_citations,
            "answer_correctness": answer_correctness,
            "citation_precision": citation_metrics["precision"],
            "citation_recall": citation_metrics["recall"],
            "citation_coverage": citation_coverage,
            "unsupported_claim_rate": unsupported_rate,
            "latency_seconds": latency_seconds,
            "manual_retrieval_seconds": question.get("manual_retrieval_seconds"),
            "api_error": api_error,
        }
        detailed_results.append(round_metrics(result))
        rows.append(
            {
                "module": "rag",
                "item_id": question["question_id"],
                "category": question["category"],
                "metric": "question_evaluation",
                "expected": "; ".join(expected_keywords),
                "actual": answer,
                "pass": answer_correctness >= 0.7,
                "notes": f"mode={source_mode}; citations={'; '.join(citations)}",
                "latency_seconds": round(latency_seconds, 4),
            }
        )

    count = max(len(questions), 1)
    metrics = {
        "answer_correctness": sum(correctness_scores) / count,
        "citation_precision": sum(citation_precisions) / count,
        "citation_recall": sum(citation_recalls) / count,
        "citation_coverage": sum(citation_coverages) / count,
        "unsupported_claim_rate": sum(unsupported_rates) / count,
        "average_answer_latency_seconds": sum(latencies) / count,
        "question_count": len(questions),
        "api_answer_count": api_count,
        "offline_fallback_count": fallback_count,
        "corpus_chunk_count": len(corpus),
        "unsupported_claim_metric_note": "Lexical support estimate against returned or retrieved evidence.",
    }
    return round_metrics(metrics), rows, detailed_results


if __name__ == "__main__":
    metrics, _, _ = evaluate_rag()
    print(metrics)
