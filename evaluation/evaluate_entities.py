from __future__ import annotations

from typing import Any

from common import (
    EVALUATION_DIR,
    extract_entities,
    jaccard_score,
    known_document_ids,
    load_json,
    round_metrics,
    set_metrics,
)


ENTITY_FIELDS = [
    "asset_ids",
    "work_order_ids",
    "rca_case_ids",
    "root_cause_ids",
    "corrective_action_ids",
    "evidence_ids",
    "document_ids",
    "failure_modes",
]


def evaluate_entities() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = load_json(EVALUATION_DIR / "ground_truth_entities.json")
    document_ids = known_document_ids()
    rows: list[dict[str, Any]] = []
    all_expected: list[str] = []
    all_predicted: list[str] = []
    field_scores: dict[str, list[float]] = {field: [] for field in ENTITY_FIELDS}

    for sample in data.get("samples", []):
        predicted = extract_entities(sample.get("text", ""), document_ids)
        expected = sample.get("expected", {})
        for field in ENTITY_FIELDS:
            expected_values = expected.get(field, [])
            predicted_values = predicted.get(field, [])
            field_scores[field].append(jaccard_score(expected_values, predicted_values))
            all_expected.extend(f"{field}:{value}" for value in expected_values)
            all_predicted.extend(f"{field}:{value}" for value in predicted_values)
            rows.append(
                {
                    "module": "entity_extraction",
                    "item_id": sample.get("sample_id"),
                    "category": field,
                    "metric": "set_match",
                    "expected": "; ".join(expected_values),
                    "actual": "; ".join(predicted_values),
                    "pass": set(map(str.lower, expected_values)) == set(map(str.lower, predicted_values)),
                    "notes": sample.get("text", ""),
                }
            )

    micro = set_metrics(all_expected, all_predicted)
    metrics = {
        "precision": micro["precision"],
        "recall": micro["recall"],
        "f1": micro["f1"],
        "equipment_tag_accuracy": sum(field_scores["asset_ids"]) / max(len(field_scores["asset_ids"]), 1),
        "failure_mode_accuracy": sum(field_scores["failure_modes"]) / max(len(field_scores["failure_modes"]), 1),
        "work_order_id_accuracy": sum(field_scores["work_order_ids"]) / max(len(field_scores["work_order_ids"]), 1),
        "sample_count": len(data.get("samples", [])),
        "mode": "deterministic PlantMind benchmark extractor",
    }
    return round_metrics(metrics), rows


if __name__ == "__main__":
    metrics, _ = evaluate_entities()
    print(metrics)
