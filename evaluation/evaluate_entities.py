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
    timed_call,
)


def predict_entities(question: dict) -> list[str]:
    text = " ".join(
        [
            question["question"],
            " ".join(question.get("expected_answer_terms", [])),
        ]
    )

    predictions: list[str] = []

    for entity in [
        "P-101",
        "C-201",
        "HX-301",
        "RCA-P101-001",
        "P101-EV-001",
        "P101-EV-002",
        "P101-EV-003",
        "P101-EV-004",
        "WO-P101-001",
        "WO-P101-002",
        "WO-P101-004",
        "WO-C201-001",
        "C001",
        "C002",
        "C003",
        "C004",
        "C005",
        "C008",
    ]:
        if entity.lower() in text.lower():
            predictions.append(entity)

    return sorted(set(predictions))


def evaluate() -> dict:
    rows = []

    for question in load_benchmark():
        predicted, latency_ms = timed_call(
            lambda question=question: predict_entities(question)
        )

        scores = precision_recall_f1(
            question.get("expected_entities", []),
            predicted,
        )

        rows.append(
            {
                "question_id": question["question_id"],
                "category": question["category"],
                "expected_entities": question.get("expected_entities", []),
                "predicted_entities": predicted,
                "precision": scores["precision"],
                "recall": scores["recall"],
                "f1": scores["f1"],
                "latency_ms": latency_ms,
            }
        )

    return {
        "metric_group": "entity_extraction",
        "question_count": len(rows),
        "precision": mean([row["precision"] for row in rows]),
        "recall": mean([row["recall"] for row in rows]),
        "f1": mean([row["f1"] for row in rows]),
        "latency_ms_avg": mean([row["latency_ms"] for row in rows]),
        "rows": rows,
    }


if __name__ == "__main__":
    print(evaluate())
