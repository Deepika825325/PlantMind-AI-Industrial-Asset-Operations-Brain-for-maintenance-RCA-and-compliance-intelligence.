from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from common import CHARTS_DIR


def _save(fig: Any, filename: str) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / filename, dpi=160, bbox_inches="tight")
    plt.close(fig)


def generate_charts(metrics: dict[str, Any], rag_results: list[dict[str, Any]]) -> list[str]:
    generated: list[str] = []

    module_scores = {
        "Entity F1": metrics.get("entity_extraction", {}).get("f1", 0),
        "RAG correctness": metrics.get("rag", {}).get("answer_correctness", 0),
        "Compliance F1": metrics.get("compliance", {}).get("gap_detection_f1", 0),
        "Graph links": metrics.get("knowledge_graph", {}).get("graph_link_completeness", 0),
        "RCA top-1": metrics.get("rca", {}).get("root_cause_top_1_accuracy", 0),
    }
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(list(module_scores.keys()), list(module_scores.values()))
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Accuracy by Module")
    ax.tick_params(axis="x", rotation=20)
    _save(fig, "accuracy_by_module.png")
    generated.append("charts/accuracy_by_module.png")

    citation_scores = {
        "Precision": metrics.get("rag", {}).get("citation_precision", 0),
        "Recall": metrics.get("rag", {}).get("citation_recall", 0),
        "Coverage": metrics.get("rag", {}).get("citation_coverage", 0),
    }
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(list(citation_scores.keys()), list(citation_scores.values()))
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Citation Performance")
    _save(fig, "citation_performance.png")
    generated.append("charts/citation_performance.png")

    by_category: dict[str, list[float]] = defaultdict(list)
    for row in rag_results:
        by_category[row["category"]].append(float(row.get("latency_seconds", 0)))
    categories = list(by_category.keys())
    category_latency = [
        sum(by_category[category]) / len(by_category[category])
        for category in categories
    ]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(categories, category_latency)
    ax.set_ylabel("Average latency (seconds)")
    ax.set_title("Latency Comparison by Benchmark Category")
    ax.tick_params(axis="x", rotation=20)
    _save(fig, "latency_comparison.png")
    generated.append("charts/latency_comparison.png")

    manual_values = [
        float(row["manual_retrieval_seconds"])
        for row in rag_results
        if row.get("manual_retrieval_seconds") is not None
    ]
    plantmind_values = [float(row.get("latency_seconds", 0)) for row in rag_results]
    fig, ax = plt.subplots(figsize=(8, 5))
    if manual_values:
        manual_average = sum(manual_values) / len(manual_values)
        plantmind_average = sum(plantmind_values) / max(len(plantmind_values), 1)
        ax.bar(["Manual retrieval", "PlantMind"], [manual_average, plantmind_average])
        ax.set_ylabel("Average seconds")
    else:
        plantmind_average = sum(plantmind_values) / max(len(plantmind_values), 1)
        ax.bar(["PlantMind"], [plantmind_average])
        ax.set_ylabel("Average seconds")
        ax.text(
            0.5,
            0.82,
            "Manual timings were not recorded.\nFill manual_retrieval_seconds in benchmark_questions.json.",
            transform=ax.transAxes,
            ha="center",
            va="center",
        )
    ax.set_title("Manual versus PlantMind Retrieval Time")
    _save(fig, "manual_vs_plantmind_retrieval_time.png")
    generated.append("charts/manual_vs_plantmind_retrieval_time.png")

    compliance_scores = {
        "Precision": metrics.get("compliance", {}).get("gap_detection_precision", 0),
        "Recall": metrics.get("compliance", {}).get("gap_detection_recall", 0),
        "Severity": metrics.get("compliance", {}).get("severity_accuracy", 0),
        "Evidence links": metrics.get("compliance", {}).get("evidence_link_accuracy", 0),
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(list(compliance_scores.keys()), list(compliance_scores.values()))
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Compliance Detection Performance")
    _save(fig, "compliance_detection_performance.png")
    generated.append("charts/compliance_detection_performance.png")

    return generated
