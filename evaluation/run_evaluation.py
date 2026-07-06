from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any
import csv
import sys
import traceback

EVALUATION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVALUATION_DIR.parent
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from charts import generate_charts
from common import ensure_output_directories, round_metrics, utc_now, write_json
from evaluate_compliance import evaluate_compliance
from evaluate_entities import evaluate_entities
from evaluate_graph import evaluate_graph
from evaluate_rag import evaluate_rag
from evaluate_rca import evaluate_rca


TARGETS = {
    "entity_extraction_f1": {
        "module": "entity_extraction",
        "metric": "f1",
        "operator": ">=",
        "target": 0.90,
    },
    "citation_precision": {
        "module": "rag",
        "metric": "citation_precision",
        "operator": ">=",
        "target": 0.85,
    },
    "citation_coverage": {
        "module": "rag",
        "metric": "citation_coverage",
        "operator": ">=",
        "target": 0.90,
    },
    "compliance_gap_recall": {
        "module": "compliance",
        "metric": "gap_detection_recall",
        "operator": ">=",
        "target": 0.80,
    },
    "graph_link_completeness": {
        "module": "knowledge_graph",
        "metric": "graph_link_completeness",
        "operator": ">=",
        "target": 0.90,
    },
    "unsupported_claim_rate": {
        "module": "rag",
        "metric": "unsupported_claim_rate",
        "operator": "<",
        "target": 0.10,
    },
    "average_answer_latency_seconds": {
        "module": "rag",
        "metric": "average_answer_latency_seconds",
        "operator": "<",
        "target": 5.0,
    },
}


def _target_result(actual: float, operator: str, target: float) -> bool:
    if operator == ">=":
        return actual >= target
    if operator == "<":
        return actual < target
    raise ValueError(f"Unsupported target operator: {operator}")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "module",
        "item_id",
        "category",
        "metric",
        "expected",
        "actual",
        "pass",
        "notes",
        "latency_seconds",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value) * 100:.1f}%"
    return "N/A"


def _build_report(
    metrics: dict[str, Any],
    target_results: dict[str, Any],
    rag_results: list[dict[str, Any]],
    generated_charts: list[str],
    errors: list[str],
) -> str:
    lines = [
        "# PlantMind Evaluation Report",
        "",
        f"Generated at: `{metrics['generated_at']}`",
        "",
        "## Execution Summary",
        "",
        f"- Benchmark questions: **{metrics.get('rag', {}).get('question_count', 0)}**",
        f"- API answers: **{metrics.get('rag', {}).get('api_answer_count', 0)}**",
        f"- Offline fallback answers: **{metrics.get('rag', {}).get('offline_fallback_count', 0)}**",
        f"- Technical evaluation errors: **{len(errors)}**",
        "",
        "Results are calculated from the current repository state. No metric is manually substituted or fabricated.",
        "",
        "## Target Metrics",
        "",
        "| Target | Actual | Requirement | Status |",
        "|---|---:|---:|---|",
    ]
    for name, result in target_results.items():
        actual = result["actual"]
        target = result["target"]
        display_actual = f"{actual:.3f}" if isinstance(actual, (int, float)) else str(actual)
        lines.append(
            f"| {name} | {display_actual} | {result['operator']} {target} | "
            f"{'PASS' if result['pass'] else 'NEEDS IMPROVEMENT'} |"
        )

    lines.extend(
        [
            "",
            "## Entity Extraction",
            "",
            f"- Precision: **{_percent(metrics.get('entity_extraction', {}).get('precision'))}**",
            f"- Recall: **{_percent(metrics.get('entity_extraction', {}).get('recall'))}**",
            f"- F1: **{_percent(metrics.get('entity_extraction', {}).get('f1'))}**",
            f"- Equipment-tag accuracy: **{_percent(metrics.get('entity_extraction', {}).get('equipment_tag_accuracy'))}**",
            f"- Failure-mode accuracy: **{_percent(metrics.get('entity_extraction', {}).get('failure_mode_accuracy'))}**",
            f"- Work-order ID accuracy: **{_percent(metrics.get('entity_extraction', {}).get('work_order_id_accuracy'))}**",
            "",
            "## RAG",
            "",
            f"- Answer correctness: **{_percent(metrics.get('rag', {}).get('answer_correctness'))}**",
            f"- Citation precision: **{_percent(metrics.get('rag', {}).get('citation_precision'))}**",
            f"- Citation recall: **{_percent(metrics.get('rag', {}).get('citation_recall'))}**",
            f"- Citation coverage: **{_percent(metrics.get('rag', {}).get('citation_coverage'))}**",
            f"- Unsupported-claim rate: **{_percent(metrics.get('rag', {}).get('unsupported_claim_rate'))}**",
            f"- Average answer latency: **{metrics.get('rag', {}).get('average_answer_latency_seconds', 0):.3f} seconds**",
            "",
            "The unsupported-claim metric is a lexical support estimate against returned or retrieved evidence. It is not an LLM-based factuality judge.",
            "",
            "## Compliance",
            "",
            f"- Gap-detection precision: **{_percent(metrics.get('compliance', {}).get('gap_detection_precision'))}**",
            f"- Gap-detection recall: **{_percent(metrics.get('compliance', {}).get('gap_detection_recall'))}**",
            f"- Gap-detection F1: **{_percent(metrics.get('compliance', {}).get('gap_detection_f1'))}**",
            f"- Severity accuracy: **{_percent(metrics.get('compliance', {}).get('severity_accuracy'))}**",
            f"- Evidence-link accuracy: **{_percent(metrics.get('compliance', {}).get('evidence_link_accuracy'))}**",
            "",
            "## Knowledge Graph",
            "",
            f"- Node coverage: **{_percent(metrics.get('knowledge_graph', {}).get('node_coverage'))}**",
            f"- Edge coverage: **{_percent(metrics.get('knowledge_graph', {}).get('edge_coverage'))}**",
            f"- Asset-document linkage accuracy: **{_percent(metrics.get('knowledge_graph', {}).get('asset_document_linkage_accuracy'))}**",
            f"- Broken-link count: **{metrics.get('knowledge_graph', {}).get('broken_link_count', 0)}**",
            "",
            "## RCA",
            "",
            f"- Root-cause top-1 accuracy: **{_percent(metrics.get('rca', {}).get('root_cause_top_1_accuracy'))}**",
            f"- Evidence coverage: **{_percent(metrics.get('rca', {}).get('evidence_coverage'))}**",
            f"- Counter-evidence coverage: **{_percent(metrics.get('rca', {}).get('counter_evidence_coverage'))}**",
            f"- Action relevance: **{_percent(metrics.get('rca', {}).get('action_relevance'))}**",
            "",
            "## Charts",
            "",
        ]
    )
    for chart in generated_charts:
        lines.append(f"- `{chart}`")

    lines.extend(["", "## Manual Retrieval Timing", ""])
    manual_count = sum(
        1 for row in rag_results if row.get("manual_retrieval_seconds") is not None
    )
    if manual_count:
        lines.append(f"Manual timing was recorded for **{manual_count}** benchmark questions.")
    else:
        lines.append(
            "Manual retrieval time has not been measured. Fill `manual_retrieval_seconds` "
            "in `benchmark_questions.json` and rerun the evaluation to produce a true comparison."
        )

    if errors:
        lines.extend(["", "## Technical Errors", ""])
        for error in errors:
            lines.append(f"- {error}")

    lines.extend(
        [
            "",
            "## Generated Outputs",
            "",
            "- `metrics.json`",
            "- `benchmark_results.csv`",
            "- `evaluation_report.md`",
            "- `rag_results.json`",
            "- `charts/accuracy_by_module.png`",
            "- `charts/citation_performance.png`",
            "- `charts/latency_comparison.png`",
            "- `charts/manual_vs_plantmind_retrieval_time.png`",
            "- `charts/compliance_detection_performance.png`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = ArgumentParser(description="Run the PlantMind benchmark evaluation.")
    parser.add_argument(
        "--api-base",
        default="http://127.0.0.1:8000",
        help="PlantMind API base URL.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip API calls and use the local extractive retrieval fallback.",
    )
    args = parser.parse_args()

    ensure_output_directories()
    module_metrics: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    rag_results: list[dict[str, Any]] = []

    evaluators = [
        ("entity_extraction", lambda: evaluate_entities()),
        ("rag", lambda: evaluate_rag(api_base=args.api_base, offline=args.offline)),
        ("compliance", lambda: evaluate_compliance()),
        ("knowledge_graph", lambda: evaluate_graph()),
        ("rca", lambda: evaluate_rca()),
    ]

    for module_name, evaluator in evaluators:
        try:
            result = evaluator()
            if module_name == "rag":
                metrics, module_rows, rag_results = result
            else:
                metrics, module_rows = result
            module_metrics[module_name] = metrics
            rows.extend(module_rows)
            print(f"{module_name}: PASS")
        except Exception as error:
            module_metrics[module_name] = {"error": str(error)}
            errors.append(f"{module_name}: {error}")
            print(f"{module_name}: ERROR")
            traceback.print_exc()

    target_results: dict[str, Any] = {}
    for target_name, definition in TARGETS.items():
        actual = (
            module_metrics.get(definition["module"], {})
            .get(definition["metric"], 0.0)
        )
        actual_value = float(actual) if isinstance(actual, (int, float)) else 0.0
        target_results[target_name] = {
            **definition,
            "actual": actual_value,
            "pass": _target_result(actual_value, definition["operator"], definition["target"]),
        }

    metrics_payload = round_metrics(
        {
            "artifact": "plantmind_evaluation_metrics",
            "generated_at": utc_now(),
            **module_metrics,
            "targets": target_results,
            "technical_errors": errors,
        }
    )

    write_json(EVALUATION_DIR / "metrics.json", metrics_payload)
    write_json(EVALUATION_DIR / "rag_results.json", rag_results)
    _write_csv(EVALUATION_DIR / "benchmark_results.csv", rows)

    generated_charts: list[str] = []
    try:
        generated_charts = generate_charts(metrics_payload, rag_results)
    except Exception as error:
        errors.append(f"charts: {error}")
        print(f"charts: ERROR ({error})")

    report = _build_report(
        metrics_payload,
        target_results,
        rag_results,
        generated_charts,
        errors,
    )
    (EVALUATION_DIR / "evaluation_report.md").write_text(
        report,
        encoding="utf-8",
        newline="\n",
    )

    print("")
    print("PlantMind evaluation complete.")
    print(f"Metrics: {EVALUATION_DIR / 'metrics.json'}")
    print(f"Results: {EVALUATION_DIR / 'benchmark_results.csv'}")
    print(f"Report: {EVALUATION_DIR / 'evaluation_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
