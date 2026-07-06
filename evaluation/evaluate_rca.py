from __future__ import annotations

from typing import Any

from common import EVALUATION_DIR, PROJECT_ROOT, load_json, round_metrics, safe_divide


def evaluate_rca() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    truth = load_json(EVALUATION_DIR / "ground_truth_rca.json")
    data = load_json(PROJECT_ROOT / "data" / "demo" / "rca_cases.json")
    actual_cases = {
        case.get("case_id"): case
        for case in data.get("cases", [])
        if isinstance(case, dict) and case.get("case_id")
    }

    rows: list[dict[str, Any]] = []
    top1_matches = 0
    case_count = 0
    expected_evidence_total = 0
    matched_evidence_total = 0
    counter_evidence_matches = 0
    counter_evidence_total = 0
    expected_actions_total = 0
    matched_actions_total = 0

    for expected_case in truth.get("cases", []):
        case_id = expected_case["case_id"]
        actual_case = actual_cases.get(case_id)
        case_count += 1
        if not actual_case:
            rows.append(
                {
                    "module": "rca",
                    "item_id": case_id,
                    "category": "case",
                    "metric": "exists",
                    "expected": "present",
                    "actual": "missing",
                    "pass": False,
                    "notes": "",
                }
            )
            continue

        root_causes = sorted(actual_case.get("root_causes", []), key=lambda item: item.get("rank", 999))
        actual_top_id = root_causes[0].get("cause_id") if root_causes else None
        expected_top_id = expected_case.get("expected_top_root_cause_id")
        if actual_top_id == expected_top_id:
            top1_matches += 1

        actual_top = root_causes[0] if root_causes else {}
        expected_evidence = set(expected_case.get("expected_evidence_ids", []))
        actual_evidence = set(actual_top.get("evidence_ids", []))
        expected_evidence_total += len(expected_evidence)
        matched_evidence_total += len(expected_evidence & actual_evidence)

        if expected_case.get("requires_counter_evidence"):
            counter_evidence_total += 1
            if actual_top.get("counter_evidence"):
                counter_evidence_matches += 1

        expected_actions = set(expected_case.get("expected_corrective_action_ids", []))
        actual_actions = {
            item.get("action_id")
            for item in actual_case.get("corrective_actions", [])
            if item.get("action_id")
        }
        expected_actions_total += len(expected_actions)
        matched_actions_total += len(expected_actions & actual_actions)

        rows.extend(
            [
                {
                    "module": "rca",
                    "item_id": case_id,
                    "category": "root_cause",
                    "metric": "top_1_accuracy",
                    "expected": expected_top_id,
                    "actual": actual_top_id,
                    "pass": actual_top_id == expected_top_id,
                    "notes": "",
                },
                {
                    "module": "rca",
                    "item_id": case_id,
                    "category": "evidence",
                    "metric": "coverage",
                    "expected": "; ".join(sorted(expected_evidence)),
                    "actual": "; ".join(sorted(actual_evidence)),
                    "pass": expected_evidence.issubset(actual_evidence),
                    "notes": "",
                },
                {
                    "module": "rca",
                    "item_id": case_id,
                    "category": "actions",
                    "metric": "relevance",
                    "expected": "; ".join(sorted(expected_actions)),
                    "actual": "; ".join(sorted(actual_actions)),
                    "pass": expected_actions.issubset(actual_actions),
                    "notes": "",
                },
            ]
        )

    metrics = {
        "root_cause_top_1_accuracy": safe_divide(top1_matches, case_count),
        "evidence_coverage": safe_divide(matched_evidence_total, expected_evidence_total),
        "counter_evidence_coverage": safe_divide(counter_evidence_matches, counter_evidence_total),
        "action_relevance": safe_divide(matched_actions_total, expected_actions_total),
        "case_count": case_count,
    }
    return round_metrics(metrics), rows


if __name__ == "__main__":
    metrics, _ = evaluate_rca()
    print(metrics)
