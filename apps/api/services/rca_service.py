from __future__ import annotations

from typing import Any

from apps.api.repositories.registry import (
    get_repository_registry,
)


def load_rca_data() -> dict[str, Any]:
    repositories = get_repository_registry()
    return repositories.rca.get_dataset()


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""

    return value.strip().lower()


def build_case_summary(case: dict[str, Any]) -> dict[str, Any]:
    root_causes = case.get("root_causes", [])
    top_root_cause = root_causes[0] if root_causes else None

    return {
        "case_id": case.get("case_id"),
        "title": case.get("title"),
        "asset_id": case.get("asset_id"),
        "asset_name": case.get("asset_name"),
        "asset_type": case.get("asset_type"),
        "incident_status": case.get("incident_status"),
        "severity": case.get("severity"),
        "detected_at": case.get("detected_at"),
        "problem_statement": case.get("problem_statement"),
        "summary": case.get("summary"),
        "overall_confidence": case.get(
            "overall_confidence",
            0
        ),
        "top_root_cause": (
            {
                "cause_id": top_root_cause.get("cause_id"),
                "title": top_root_cause.get("title"),
                "category": top_root_cause.get("category"),
                "confidence": top_root_cause.get(
                    "confidence",
                    0
                ),
            }
            if top_root_cause
            else None
        ),
        "timeline_event_count": len(
            case.get("timeline", [])
        ),
        "causal_chain_step_count": len(
            case.get("causal_chain", [])
        ),
        "root_cause_count": len(
            case.get("root_causes", [])
        ),
        "corrective_action_count": len(
            case.get("corrective_actions", [])
        ),
        "evidence_count": len(
            case.get("evidence", [])
        ),
    }


def list_rca_cases(
    asset_id: str | None = None,
    severity: str | None = None,
    incident_status: str | None = None,
) -> dict[str, Any]:
    data = load_rca_data()
    cases = data["cases"]

    normalized_asset_id = normalize_text(asset_id)
    normalized_severity = normalize_text(severity)
    normalized_status = normalize_text(incident_status)

    filtered_cases: list[dict[str, Any]] = []

    for case in cases:
        if (
            normalized_asset_id
            and normalize_text(case.get("asset_id"))
            != normalized_asset_id
        ):
            continue

        if (
            normalized_severity
            and normalize_text(case.get("severity"))
            != normalized_severity
        ):
            continue

        if (
            normalized_status
            and normalize_text(
                case.get("incident_status")
            )
            != normalized_status
        ):
            continue

        filtered_cases.append(build_case_summary(case))

    filtered_cases.sort(
        key=lambda item: item.get("detected_at", ""),
        reverse=True,
    )

    return {
        "artifact": data.get("artifact"),
        "generated_at": data.get("generated_at"),
        "total_count": len(cases),
        "filtered_count": len(filtered_cases),
        "filters": {
            "asset_id": asset_id,
            "severity": severity,
            "incident_status": incident_status,
        },
        "cases": filtered_cases,
    }


def get_rca_case(case_id: str) -> dict[str, Any] | None:
    normalized_case_id = normalize_text(case_id)
    data = load_rca_data()

    for case in data["cases"]:
        if (
            normalize_text(case.get("case_id"))
            == normalized_case_id
        ):
            return case

    return None


def get_rca_cases_for_asset(
    asset_id: str,
) -> list[dict[str, Any]]:
    normalized_asset_id = normalize_text(asset_id)
    data = load_rca_data()

    matching_cases = [
        case
        for case in data["cases"]
        if normalize_text(case.get("asset_id"))
        == normalized_asset_id
    ]

    matching_cases.sort(
        key=lambda item: item.get("detected_at", ""),
        reverse=True,
    )

    return matching_cases


def get_rca_evidence(
    case_id: str,
    evidence_id: str,
) -> dict[str, Any] | None:
    case = get_rca_case(case_id)

    if case is None:
        return None

    normalized_evidence_id = normalize_text(evidence_id)

    for evidence in case.get("evidence", []):
        if (
            normalize_text(evidence.get("evidence_id"))
            == normalized_evidence_id
        ):
            return evidence

    return None


def get_rca_statistics() -> dict[str, Any]:
    data = load_rca_data()
    cases = data["cases"]

    severity_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    asset_counts: dict[str, int] = {}

    total_confidence = 0.0
    total_root_causes = 0
    total_actions = 0
    total_evidence = 0

    for case in cases:
        severity = case.get("severity", "Unknown")
        status = case.get(
            "incident_status",
            "Unknown"
        )
        asset_id = case.get("asset_id", "Unknown")

        severity_counts[severity] = (
            severity_counts.get(severity, 0) + 1
        )

        status_counts[status] = (
            status_counts.get(status, 0) + 1
        )

        asset_counts[asset_id] = (
            asset_counts.get(asset_id, 0) + 1
        )

        total_confidence += float(
            case.get("overall_confidence", 0)
        )

        total_root_causes += len(
            case.get("root_causes", [])
        )

        total_actions += len(
            case.get("corrective_actions", [])
        )

        total_evidence += len(
            case.get("evidence", [])
        )

    average_confidence = (
        total_confidence / len(cases)
        if cases
        else 0
    )

    return {
        "total_cases": len(cases),
        "average_confidence": round(
            average_confidence,
            2
        ),
        "total_root_causes": total_root_causes,
        "total_corrective_actions": total_actions,
        "total_evidence_items": total_evidence,
        "severity_counts": severity_counts,
        "status_counts": status_counts,
        "asset_counts": asset_counts,
    }