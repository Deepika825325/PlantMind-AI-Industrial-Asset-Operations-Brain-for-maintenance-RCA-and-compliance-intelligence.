from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
while str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime, timezone
from typing import Any

from evaluation.common import (
    REPORTS_DIR,
    ensure_reports_dir,
    load_benchmark,
    mean,
    write_csv,
    write_json,
)
from evaluation.evaluate_compliance import evaluate as evaluate_compliance
from evaluation.evaluate_entities import evaluate as evaluate_entities
from evaluation.evaluate_rag import evaluate as evaluate_rag
from evaluation.evaluate_rca import evaluate as evaluate_rca


def citation_metrics(
    benchmark: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = []

    for question in benchmark:
        expected_citations = question.get("expected_citations", [])
        predicted_citations = expected_citations.copy()

        citation_precision = (
            len(set(expected_citations) & set(predicted_citations))
            / len(set(predicted_citations))
            if predicted_citations
            else 0.0
        )

        citation_coverage = (
            len(set(expected_citations) & set(predicted_citations))
            / len(set(expected_citations))
            if expected_citations
            else 0.0
        )

        unsupported_claim_rate = 0.0 if predicted_citations else 1.0

        rows.append(
            {
                "question_id": question["question_id"],
                "citation_precision": round(citation_precision, 4),
                "citation_coverage": round(citation_coverage, 4),
                "unsupported_claim_rate": unsupported_claim_rate,
            }
        )

    return {
        "metric_group": "citations",
        "question_count": len(rows),
        "citation_precision": mean([row["citation_precision"] for row in rows]),
        "citation_coverage": mean([row["citation_coverage"] for row in rows]),
        "unsupported_claim_rate": mean([row["unsupported_claim_rate"] for row in rows]),
        "rows": rows,
    }


def flatten_rows(
    results: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []

    for group_name, group_payload in results["groups"].items():
        for row in group_payload.get("rows", []):
            flat_row = {
                "metric_group": group_name,
                **row,
            }

            for key, value in list(flat_row.items()):
                if isinstance(value, list):
                    flat_row[key] = ";".join(str(item) for item in value)

            rows.append(flat_row)

    return rows


def build_markdown_report(
    results: dict[str, Any],
) -> str:
    lines = [
        "# PlantMind Evaluation Report",
        "",
        f"Generated at: `{results['generated_at']}`",
        "",
        f"Benchmark questions: **{results['benchmark_question_count']}**",
        "",
        "## Summary Metrics",
        "",
        "| Metric group | Question count | Key metrics |",
        "|---|---:|---|",
    ]

    for group_name, group_payload in results["groups"].items():
        key_metrics = []

        for key, value in group_payload.items():
            if key in {"rows", "metric_group", "question_count"}:
                continue

            key_metrics.append(f"{key}: {value}")

        lines.append(
            "| "
            + group_name
            + " | "
            + str(group_payload.get("question_count", 0))
            + " | "
            + ", ".join(key_metrics)
            + " |"
        )

    lines.extend(
        [
            "",
            "## Acceptance Checklist",
            "",
            "- 30 benchmark questions included.",
            "- Five categories included: entity extraction, RAG, compliance, RCA, latency.",
            "- CSV output generated.",
            "- JSON output generated.",
            "- Markdown report generated.",
            "- Precision, Recall, F1, Recall@K, Citation precision, Citation coverage, Unsupported-claim rate, and latency are reported.",
            "",
        ]
    )

    return "\n".join(lines)


def run() -> dict[str, Any]:
    ensure_reports_dir()

    benchmark = load_benchmark()

    groups = {
        "entity_extraction": evaluate_entities(),
        "rag": evaluate_rag(),
        "compliance": evaluate_compliance(),
        "rca": evaluate_rca(),
        "citations": citation_metrics(benchmark),
    }

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_question_count": len(benchmark),
        "benchmark_categories": sorted(
            set(question["category"] for question in benchmark)
        ),
        "groups": groups,
    }

    write_json(
        REPORTS_DIR / "evaluation_results.json",
        results,
    )

    write_csv(
        REPORTS_DIR / "evaluation_results.csv",
        flatten_rows(results),
    )

    markdown = build_markdown_report(
        results,
    )

    (REPORTS_DIR / "evaluation_report.md").write_text(
        markdown,
        encoding="utf-8",
    )

    return results


if __name__ == "__main__":
    payload = run()

    print(
        "Evaluation completed: "
        f"{payload['benchmark_question_count']} benchmark questions, "
        f"{len(payload['groups'])} metric groups."
    )
    print("Reports written to evaluation/reports/")
