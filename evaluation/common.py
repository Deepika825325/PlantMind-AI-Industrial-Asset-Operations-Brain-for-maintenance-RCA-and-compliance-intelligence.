from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any


BENCHMARK_PATH = Path("evaluation/ground_truth/benchmark_questions.json")
REPORTS_DIR = Path("evaluation/reports")


def load_benchmark() -> list[dict[str, Any]]:
    return json.loads(
        BENCHMARK_PATH.read_text(
            encoding="utf-8",
        )
    )


def ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def precision_recall_f1(
    expected: list[str],
    predicted: list[str],
) -> dict[str, float]:
    expected_set = set(expected)
    predicted_set = set(predicted)

    true_positive = len(expected_set & predicted_set)

    precision = (
        true_positive / len(predicted_set)
        if predicted_set
        else 0.0
    )
    recall = (
        true_positive / len(expected_set)
        if expected_set
        else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def recall_at_k(
    expected_document: str,
    retrieved_documents: list[str],
    k: int = 5,
) -> float:
    if not expected_document:
        return 0.0

    return 1.0 if expected_document in retrieved_documents[:k] else 0.0


def mean(values: list[float]) -> float:
    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        4,
    )


def write_json(
    path: Path,
    payload: Any,
) -> None:
    ensure_reports_dir()
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def write_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    ensure_reports_dir()

    if not rows:
        path.write_text(
            "",
            encoding="utf-8",
        )
        return

    fieldnames = sorted(
        {
            field
            for row in rows
            for field in row.keys()
        }
    )

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def timed_call(function):
    start = time.perf_counter()
    result = function()
    latency_ms = (time.perf_counter() - start) * 1000

    return result, round(latency_ms, 3)
