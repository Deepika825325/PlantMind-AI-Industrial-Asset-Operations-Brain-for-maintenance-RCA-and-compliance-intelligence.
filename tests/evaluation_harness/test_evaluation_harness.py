from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
while str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

import json

from evaluation.common import load_benchmark
from evaluation.run_evaluation import run


def test_benchmark_has_30_questions_and_five_categories() -> None:
    benchmark = load_benchmark()

    assert len(benchmark) == 30

    categories = {
        question["category"]
        for question in benchmark
    }

    assert categories == {
        "entity_extraction",
        "rag",
        "compliance",
        "rca",
        "latency",
    }


def test_run_evaluation_generates_json_csv_and_markdown() -> None:
    results = run()

    assert results["benchmark_question_count"] == 30

    json_path = Path("evaluation/reports/evaluation_results.json")
    csv_path = Path("evaluation/reports/evaluation_results.csv")
    markdown_path = Path("evaluation/reports/evaluation_report.md")

    assert json_path.exists()
    assert csv_path.exists()
    assert markdown_path.exists()

    payload = json.loads(
        json_path.read_text(
            encoding="utf-8",
        )
    )

    assert payload["benchmark_question_count"] == 30
    assert "entity_extraction" in payload["groups"]
    assert "rag" in payload["groups"]
    assert "compliance" in payload["groups"]
    assert "rca" in payload["groups"]
    assert "citations" in payload["groups"]

    markdown = markdown_path.read_text(
        encoding="utf-8",
    )

    assert "PlantMind Evaluation Report" in markdown
    assert "Precision" in markdown
    assert "Recall@K" in markdown
    assert "Unsupported-claim rate" in markdown
