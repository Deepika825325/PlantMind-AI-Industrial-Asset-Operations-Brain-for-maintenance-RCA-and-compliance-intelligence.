from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from apps.api.services.data_loader import (
    get_assets,
    get_compliance_matrix,
)
from apps.api.services.maintenance_service import (
    get_all_work_orders,
)
from apps.api.services.rca_service import (
    load_rca_data,
)


CLOSED_STATUSES = {
    "cancelled",
    "closed",
    "completed",
    "resolved",
    "verified",
}

AT_RISK_LEVELS = {
    "critical",
    "high",
    "medium",
}

CRITICAL_SEVERITIES = {
    "critical",
    "high",
}

URGENT_PRIORITIES = {
    "critical",
    "high",
    "immediate",
    "urgent",
}

ACTION_PRIORITY_RANK = {
    "immediate": 0,
    "critical": 1,
    "high": 2,
    "medium": 3,
    "preventive": 4,
    "low": 5,
}

WORK_ORDER_PRIORITY_RANK = {
    "critical": 0,
    "immediate": 1,
    "urgent": 2,
    "high": 3,
    "medium": 4,
    "low": 5,
}


def _generated_at() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _normalize(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip().lower()


def _number(
    value: Any,
) -> float:
    try:
        return float(
            value or 0
        )
    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _extract_records(
    payload: Any,
    key: str,
) -> list[dict[str, Any]]:
    if isinstance(
        payload,
        list,
    ):
        records = payload
    elif isinstance(
        payload,
        dict,
    ):
        records = payload.get(
            key,
            [],
        )
    else:
        records = []

    return [
        record
        for record in records
        if isinstance(
            record,
            dict,
        )
    ]


def _is_open(
    status: Any,
) -> bool:
    return (
        _normalize(status)
        not in CLOSED_STATUSES
    )


def _readiness_label(
    score: int,
) -> str:
    if score >= 90:
        return "Ready"

    if score >= 70:
        return "Moderate"

    if score >= 40:
        return "Low"

    return "Critical"


def _build_assets_at_risk(
    assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    filtered_assets = [
        asset
        for asset in assets
        if _normalize(
            asset.get(
                "risk_level"
            )
        )
        in AT_RISK_LEVELS
    ]

    filtered_assets.sort(
        key=lambda asset: (
            -_number(
                asset.get(
                    "risk_score"
                )
            ),
            str(
                asset.get(
                    "asset_id",
                    "",
                )
            ),
        )
    )

    return [
        {
            "asset_id": asset.get(
                "asset_id"
            ),
            "asset_name": asset.get(
                "asset_name"
            ),
            "asset_type": asset.get(
                "asset_type"
            ),
            "risk_level": asset.get(
                "risk_level"
            ),
            "risk_score": asset.get(
                "risk_score"
            ),
            "health_score": asset.get(
                "health_score"
            ),
            "sensor_status": asset.get(
                "sensor_status"
            ),
            "compliance_status": asset.get(
                "compliance_status"
            ),
        }
        for asset in filtered_assets
    ]


def _build_open_compliance_gaps(
    gaps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    open_gaps = [
        gap
        for gap in gaps
        if _is_open(
            gap.get(
                "current_status"
            )
        )
    ]

    severity_rank = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    open_gaps.sort(
        key=lambda gap: (
            severity_rank.get(
                _normalize(
                    gap.get(
                        "gap_severity"
                    )
                ),
                99,
            ),
            str(
                gap.get(
                    "gap_id",
                    "",
                )
            ),
        )
    )

    return [
        {
            "gap_id": gap.get(
                "gap_id"
            ),
            "asset_id": gap.get(
                "asset_id"
            ),
            "requirement": gap.get(
                "requirement"
            ),
            "current_status": gap.get(
                "current_status"
            ),
            "gap_severity": gap.get(
                "gap_severity"
            ),
            "expected_evidence": gap.get(
                "expected_evidence"
            ),
            "evidence_file": (
                gap.get(
                    "evidence_file"
                )
                or None
            ),
            "evidence_available": bool(
                str(
                    gap.get(
                        "evidence_file",
                        "",
                    )
                ).strip()
            ),
            "recommended_action": gap.get(
                "recommended_action"
            ),
            "source_document": gap.get(
                "source_document"
            ),
        }
        for gap in open_gaps
    ]


def _build_urgent_work_orders(
    work_orders: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    urgent_work_orders = [
        work_order
        for work_order in work_orders
        if (
            _is_open(
                work_order.get(
                    "status"
                )
            )
            and (
                _normalize(
                    work_order.get(
                        "priority"
                    )
                )
                in URGENT_PRIORITIES
                or _number(
                    work_order.get(
                        "risk_score"
                    )
                )
                >= 80
            )
        )
    ]

    urgent_work_orders.sort(
        key=lambda work_order: (
            WORK_ORDER_PRIORITY_RANK.get(
                _normalize(
                    work_order.get(
                        "priority"
                    )
                ),
                99,
            ),
            -_number(
                work_order.get(
                    "risk_score"
                )
            ),
            str(
                work_order.get(
                    "due_at",
                    "",
                )
            ),
        )
    )

    return [
        {
            "work_order_id": work_order.get(
                "work_order_id"
            ),
            "asset_id": work_order.get(
                "asset_id"
            ),
            "title": work_order.get(
                "title"
            ),
            "maintenance_type": work_order.get(
                "maintenance_type"
            ),
            "priority": work_order.get(
                "priority"
            ),
            "status": work_order.get(
                "status"
            ),
            "risk_score": work_order.get(
                "risk_score"
            ),
            "confidence": work_order.get(
                "confidence"
            ),
            "due_at": work_order.get(
                "due_at"
            ),
            "owner_role": work_order.get(
                "owner_role"
            ),
            "linked_rca_case_id": work_order.get(
                "linked_rca_case_id"
            ),
            "verification_metric": work_order.get(
                "verification_metric"
            ),
        }
        for work_order in urgent_work_orders
    ]


def _build_critical_rca_cases(
    cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    critical_cases = [
        case
        for case in cases
        if (
            _normalize(
                case.get(
                    "severity"
                )
            )
            in CRITICAL_SEVERITIES
            and _is_open(
                case.get(
                    "incident_status"
                )
            )
        )
    ]

    severity_rank = {
        "critical": 0,
        "high": 1,
    }

    critical_cases.sort(
        key=lambda case: (
            severity_rank.get(
                _normalize(
                    case.get(
                        "severity"
                    )
                ),
                99,
            ),
            -_number(
                case.get(
                    "overall_confidence"
                )
            ),
        )
    )

    return [
        {
            "case_id": case.get(
                "case_id"
            ),
            "title": case.get(
                "title"
            ),
            "asset_id": case.get(
                "asset_id"
            ),
            "asset_name": case.get(
                "asset_name"
            ),
            "severity": case.get(
                "severity"
            ),
            "incident_status": case.get(
                "incident_status"
            ),
            "detected_at": case.get(
                "detected_at"
            ),
            "overall_confidence": case.get(
                "overall_confidence"
            ),
            "recommendation_summary": case.get(
                "recommendation_summary"
            ),
        }
        for case in critical_cases
    ]


def _build_audit_readiness(
    open_gaps: list[dict[str, Any]],
) -> dict[str, Any]:
    total_gap_count = len(
        open_gaps
    )

    evidence_ready_count = sum(
        1
        for gap in open_gaps
        if gap.get(
            "evidence_available"
        )
    )

    missing_evidence_count = (
        total_gap_count
        - evidence_ready_count
    )

    score = (
        round(
            (
                evidence_ready_count
                / total_gap_count
            )
            * 100
        )
        if total_gap_count
        else 100
    )

    return {
        "score": score,
        "label": _readiness_label(
            score
        ),
        "total_open_gap_count": (
            total_gap_count
        ),
        "evidence_ready_gap_count": (
            evidence_ready_count
        ),
        "missing_evidence_gap_count": (
            missing_evidence_count
        ),
        "method": (
            "Percentage of open compliance "
            "gaps with linked evidence"
        ),
    }


def _build_top_recommended_action(
    cases: list[dict[str, Any]],
    urgent_work_orders: list[dict[str, Any]],
) -> dict[str, Any] | None:
    action_candidates: list[
        dict[str, Any]
    ] = []

    for case in cases:
        if not _is_open(
            case.get(
                "incident_status"
            )
        ):
            continue

        for action in case.get(
            "corrective_actions",
            [],
        ):
            if not isinstance(
                action,
                dict,
            ):
                continue

            action_candidates.append(
                {
                    "action_id": action.get(
                        "action_id"
                    ),
                    "title": action.get(
                        "title"
                    ),
                    "description": action.get(
                        "description"
                    ),
                    "priority": action.get(
                        "priority"
                    ),
                    "status": action.get(
                        "status"
                    ),
                    "owner_role": action.get(
                        "owner_role"
                    ),
                    "due_in_hours": action.get(
                        "due_in_hours"
                    ),
                    "verification_metric": (
                        action.get(
                            "verification_metric"
                        )
                    ),
                    "asset_id": case.get(
                        "asset_id"
                    ),
                    "source_type": "RCA",
                    "source_id": case.get(
                        "case_id"
                    ),
                    "confidence": case.get(
                        "overall_confidence"
                    ),
                }
            )

    if action_candidates:
        action_candidates.sort(
            key=lambda action: (
                ACTION_PRIORITY_RANK.get(
                    _normalize(
                        action.get(
                            "priority"
                        )
                    ),
                    99,
                ),
                _number(
                    action.get(
                        "due_in_hours"
                    )
                ),
                -_number(
                    action.get(
                        "confidence"
                    )
                ),
            )
        )

        return action_candidates[0]

    if urgent_work_orders:
        work_order = urgent_work_orders[0]

        return {
            "action_id": work_order.get(
                "work_order_id"
            ),
            "title": work_order.get(
                "title"
            ),
            "description": None,
            "priority": work_order.get(
                "priority"
            ),
            "status": work_order.get(
                "status"
            ),
            "owner_role": work_order.get(
                "owner_role"
            ),
            "due_in_hours": None,
            "verification_metric": (
                work_order.get(
                    "verification_metric"
                )
            ),
            "asset_id": work_order.get(
                "asset_id"
            ),
            "source_type": "Work Order",
            "source_id": work_order.get(
                "work_order_id"
            ),
            "confidence": work_order.get(
                "confidence"
            ),
        }

    return None


def get_operations_summary() -> dict[str, Any]:
    assets = _extract_records(
        get_assets(),
        "assets",
    )

    compliance_gaps = _extract_records(
        get_compliance_matrix(),
        "gaps",
    )

    work_orders = _extract_records(
        get_all_work_orders(),
        "work_orders",
    )

    rca_cases = _extract_records(
        load_rca_data(),
        "cases",
    )

    assets_at_risk = (
        _build_assets_at_risk(
            assets
        )
    )

    open_compliance_gaps = (
        _build_open_compliance_gaps(
            compliance_gaps
        )
    )

    urgent_work_orders = (
        _build_urgent_work_orders(
            work_orders
        )
    )

    critical_rca_cases = (
        _build_critical_rca_cases(
            rca_cases
        )
    )

    audit_readiness = (
        _build_audit_readiness(
            open_compliance_gaps
        )
    )

    top_recommended_action = (
        _build_top_recommended_action(
            rca_cases,
            urgent_work_orders,
        )
    )

    return {
        "generated_at": _generated_at(),
        "assets_at_risk": {
            "count": len(
                assets_at_risk
            ),
            "items": assets_at_risk,
        },
        "critical_rca_cases": {
            "count": len(
                critical_rca_cases
            ),
            "items": critical_rca_cases,
        },
        "open_compliance_gaps": {
            "count": len(
                open_compliance_gaps
            ),
            "items": open_compliance_gaps,
        },
        "urgent_work_orders": {
            "count": len(
                urgent_work_orders
            ),
            "items": urgent_work_orders,
        },
        "audit_readiness": (
            audit_readiness
        ),
        "top_recommended_action": (
            top_recommended_action
        ),
    }
