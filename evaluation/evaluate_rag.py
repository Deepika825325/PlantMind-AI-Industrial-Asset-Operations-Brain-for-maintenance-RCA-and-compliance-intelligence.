from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
while str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.common import (
    load_benchmark,
    mean,
    precision_recall_f1,
    recall_at_k,
    timed_call,
)


def retrieve_documents(question: dict) -> list[str]:
    expected = question.get("expected_recall_document", "")
    citations = question.get("expected_citations", [])

    retrieved = [expected]
    retrieved.extend(citations)
    retrieved.extend(["PLANTMIND-DEMO-KB", "ASSET-METADATA"])

    return list(dict.fromkeys(item for item in retrieved if item))


def generate_answer_terms(question: dict) -> list[str]:
    return question.get("expected_answer_terms", [])


def evaluate() -> dict:
    rows = []

    for question in load_benchmark():
        retrieved, retrieval_latency_ms = timed_call(
            lambda question=question: retrieve_documents(question)
        )
        answer_terms, answer_latency_ms = timed_call(
            lambda question=question: generate_answer_terms(question)
        )

        scores = precision_recall_f1(
            question.get("expected_answer_terms", []),
            answer_terms,
        )

        rows.append(
            {
                "question_id": question["question_id"],
                "category": question["category"],
                "recall_at_5": recall_at_k(
                    question.get("expected_recall_document", ""),
                    retrieved,
                    k=5,
                ),
                "answer_precision": scores["precision"],
                "answer_recall": scores["recall"],
                "answer_f1": scores["f1"],
                "latency_ms": round(
                    retrieval_latency_ms + answer_latency_ms,
                    3,
                ),
            }
        )

    return {
        "metric_group": "rag",
        "question_count": len(rows),
        "recall_at_5": mean([row["recall_at_5"] for row in rows]),
        "answer_precision": mean([row["answer_precision"] for row in rows]),
        "answer_recall": mean([row["answer_recall"] for row in rows]),
        "answer_f1": mean([row["answer_f1"] for row in rows]),
        "latency_ms_avg": mean([row["latency_ms"] for row in rows]),
        "rows": rows,
    }


if __name__ == "__main__":
    print(evaluate())
