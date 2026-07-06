from __future__ import annotations

from typing import Any
import sys

from common import EVALUATION_DIR, PROJECT_ROOT, load_json, round_metrics, set_metrics

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def evaluate_compliance() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from apps.api.services.data_loader import clear_data_cache
    from apps.api.services.compliance_service import get_asset_audit_package

    clear_data_cache()
    ground_truth = load_json(EVALUATION_DIR / "ground_truth_compliance.json")
    expected_pairs: list[str] = []
    actual_pairs: list[str] = []
    severity_matches = 0
    severity_total = 0
    expected_links_total = 0
    matched_links_total = 0
    score_matches = 0
    score_total = 0
    rows: list[dict[str, Any]] = []

    for asset in ground_truth.get("assets", []):
        asset_id = asset["asset_id"]
        package = get_asset_audit_package(asset_id)
        if not package:
            rows.append(
                {
                    "module": "compliance",
                    "item_id": asset_id,
                    "category": "audit_package",
                    "metric": "package_exists",
                    "expected": "available",
                    "actual": "missing",
                    "pass": False,
                    "notes": "",
                }
            )
            continue

        actual_gaps = {gap["rule_id"]: gap for gap in package.get("open_gaps", [])}
        expected_failed = asset.get("expected_failed_rules", [])
        expected_pairs.extend(f"{asset_id}:{rule_id}" for rule_id in expected_failed)
        actual_pairs.extend(f"{asset_id}:{rule_id}" for rule_id in actual_gaps)

        for rule_id in expected_failed:
            actual_gap = actual_gaps.get(rule_id)
            expected_severity = asset.get("expected_severity", {}).get(rule_id)
            actual_severity = actual_gap.get("severity") if actual_gap else None
            if expected_severity:
                severity_total += 1
                if expected_severity == actual_severity:
                    severity_matches += 1

            expected_links = asset.get("expected_links", {}).get(rule_id, [])
            if expected_links:
                actual_links = set()
                if actual_gap:
                    actual_links.update(actual_gap.get("linked_document_ids", []))
                    actual_links.update(actual_gap.get("linked_work_order_ids", []))
                    actual_links.update(actual_gap.get("linked_rca_case_ids", []))
                expected_links_total += len(expected_links)
                matched_links_total += len(set(expected_links) & actual_links)

            rows.append(
                {
                    "module": "compliance",
                    "item_id": f"{asset_id}:{rule_id}",
                    "category": "gap_detection",
                    "metric": "expected_failed_rule",
                    "expected": rule_id,
                    "actual": rule_id if actual_gap else "not detected",
                    "pass": bool(actual_gap),
                    "notes": f"expected_severity={expected_severity}; actual_severity={actual_severity}",
                }
            )

        expected_score = asset.get("expected_audit_readiness_score")
        if expected_score is not None:
            score_total += 1
            actual_score = package.get("audit_readiness_score")
            if actual_score == expected_score:
                score_matches += 1
            rows.append(
                {
                    "module": "compliance",
                    "item_id": asset_id,
                    "category": "audit_score",
                    "metric": "exact_score",
                    "expected": expected_score,
                    "actual": actual_score,
                    "pass": actual_score == expected_score,
                    "notes": "",
                }
            )

    detection = set_metrics(expected_pairs, actual_pairs)
    metrics = {
        "gap_detection_precision": detection["precision"],
        "gap_detection_recall": detection["recall"],
        "gap_detection_f1": detection["f1"],
        "severity_accuracy": severity_matches / severity_total if severity_total else 1.0,
        "evidence_link_accuracy": (
            matched_links_total / expected_links_total if expected_links_total else 1.0
        ),
        "audit_score_accuracy": score_matches / score_total if score_total else 1.0,
        "expected_gap_count": len(expected_pairs),
        "detected_gap_count": len(actual_pairs),
    }
    return round_metrics(metrics), rows


if __name__ == "__main__":
    metrics, _ = evaluate_compliance()
    print(metrics)
