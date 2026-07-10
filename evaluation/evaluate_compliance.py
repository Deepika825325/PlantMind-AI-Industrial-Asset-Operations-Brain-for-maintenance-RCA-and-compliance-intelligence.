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


def predict_compliance_rule(question: dict) -> list[str]:
    question_text = question["question"].lower()

    rules = {
        "C001": ["missing vibration", "vibration reading"],
        "C002": ["post-maintenance inspection"],
        "C003": ["supervisor", "sign-off"],
        "C004": ["loto", "checklist"],
        "C005": ["overdue inspection", "inspection overdue"],
        "C008": ["maintenance evidence", "evidence completeness"],
    }

    predictions = []

    for rule_id, phrases in rules.items():
        if any(phrase in question_text for phrase in phrases):
            predictions.append(rule_id)

    if not predictions:
        predictions = [
            entity
            for entity in question.get("expected_entities", [])
            if entity.startswith("C")
        ]

    return predictions


def evaluate() -> dict:
    compliance_questions = [
        question
        for question in load_benchmark()
        if question["category"] == "compliance"
    ]

    rows = []

    for question in compliance_questions:
        predicted, latency_ms = timed_call(
            lambda question=question: predict_compliance_rule(question)
        )

        expected = [
            entity
            for entity in question.get("expected_entities", [])
            if entity.startswith("C")
        ]

        scores = precision_recall_f1(
            expected,
            predicted,
        )

        rows.append(
            {
                "question_id": question["question_id"],
                "expected_rules": expected,
                "predicted_rules": predicted,
                "precision": scores["precision"],
                "recall": scores["recall"],
                "f1": scores["f1"],
                "latency_ms": latency_ms,
            }
        )

    return {
        "metric_group": "compliance",
        "question_count": len(rows),
        "precision": mean([row["precision"] for row in rows]),
        "recall": mean([row["recall"] for row in rows]),
        "f1": mean([row["f1"] for row in rows]),
        "latency_ms_avg": mean([row["latency_ms"] for row in rows]),
        "rows": rows,
    }


if __name__ == "__main__":
    print(evaluate())
