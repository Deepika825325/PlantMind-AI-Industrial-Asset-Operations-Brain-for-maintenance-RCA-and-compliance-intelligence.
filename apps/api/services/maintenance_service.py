import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATA_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "demo"
    / "maintenance_work_orders.json"
)

PRIORITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}

STATUS_ORDER = {
    "Open": 3,
    "Delayed": 3,
    "In Progress": 2,
    "Planned": 1,
    "Completed": 0,
    "Cancelled": 0
}


def _load_data() -> dict[str, Any]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Maintenance work-order data not found: {DATA_PATH}"
        )

    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    normalized_value = value.replace("Z", "+00:00")

    try:
        parsed_value = datetime.fromisoformat(normalized_value)
    except ValueError:
        return None

    if parsed_value.tzinfo is None:
        parsed_value = parsed_value.replace(tzinfo=timezone.utc)

    return parsed_value


def _matches_text(value: str | None, expected: str | None) -> bool:
    if expected is None:
        return True

    return (value or "").lower() == expected.lower()


def _sort_work_orders(
    work_orders: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return sorted(
        work_orders,
        key=lambda item: (
            -PRIORITY_ORDER.get(item.get("priority", ""), 0),
            -item.get("risk_score", 0),
            _parse_datetime(item.get("due_at"))
            or datetime.max.replace(tzinfo=timezone.utc)
        )
    )


def get_all_work_orders() -> list[dict[str, Any]]:
    data = _load_data()
    return _sort_work_orders(data.get("work_orders", []))


def filter_work_orders(
    asset_id: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    maintenance_type: str | None = None,
    rca_case_id: str | None = None,
    due_date: str | None = None,
    due_before: str | None = None,
    due_after: str | None = None
) -> list[dict[str, Any]]:
    work_orders = get_all_work_orders()

    normalized_asset_id = asset_id.upper() if asset_id else None
    normalized_rca_case_id = rca_case_id.upper() if rca_case_id else None
    parsed_due_date = _parse_datetime(due_date)
    parsed_due_before = _parse_datetime(due_before)
    parsed_due_after = _parse_datetime(due_after)

    filtered_work_orders: list[dict[str, Any]] = []

    for work_order in work_orders:
        if normalized_asset_id:
            if work_order.get("asset_id", "").upper() != normalized_asset_id:
                continue

        if not _matches_text(work_order.get("priority"), priority):
            continue

        if not _matches_text(work_order.get("status"), status):
            continue

        if not _matches_text(
            work_order.get("maintenance_type"),
            maintenance_type
        ):
            continue

        if normalized_rca_case_id:
            linked_rca_case_id = (
                work_order.get("linked_rca_case_id") or ""
            ).upper()

            if linked_rca_case_id != normalized_rca_case_id:
                continue

        work_order_due_at = _parse_datetime(work_order.get("due_at"))

        if parsed_due_date:
            if not work_order_due_at:
                continue

            if work_order_due_at.date() != parsed_due_date.date():
                continue

        if parsed_due_before:
            if not work_order_due_at:
                continue

            if work_order_due_at > parsed_due_before:
                continue

        if parsed_due_after:
            if not work_order_due_at:
                continue

            if work_order_due_at < parsed_due_after:
                continue

        filtered_work_orders.append(work_order)

    return _sort_work_orders(filtered_work_orders)


def get_work_order(
    work_order_id: str
) -> dict[str, Any] | None:
    normalized_work_order_id = work_order_id.upper()

    for work_order in get_all_work_orders():
        if (
            work_order.get("work_order_id", "").upper()
            == normalized_work_order_id
        ):
            return work_order

    return None


def get_asset_work_orders(
    asset_id: str
) -> list[dict[str, Any]]:
    return filter_work_orders(asset_id=asset_id)


def get_rca_work_orders(
    case_id: str
) -> list[dict[str, Any]]:
    return filter_work_orders(rca_case_id=case_id)


def get_work_order_statistics() -> dict[str, Any]:
    work_orders = get_all_work_orders()
    now = datetime.now(timezone.utc)

    status_counts = Counter(
        work_order.get("status", "Unknown")
        for work_order in work_orders
    )

    priority_counts = Counter(
        work_order.get("priority", "Unknown")
        for work_order in work_orders
    )

    maintenance_type_counts = Counter(
        work_order.get("maintenance_type", "Unknown")
        for work_order in work_orders
    )

    asset_counts = Counter(
        work_order.get("asset_id", "Unknown")
        for work_order in work_orders
    )

    overdue_work_orders = [
        work_order
        for work_order in work_orders
        if work_order.get("status") not in {"Completed", "Cancelled"}
        and (
            _parse_datetime(work_order.get("due_at"))
            and _parse_datetime(work_order.get("due_at")) < now
        )
    ]

    open_work_orders = [
        work_order
        for work_order in work_orders
        if work_order.get("status") in {
            "Open",
            "Delayed",
            "In Progress",
            "Planned"
        }
    ]

    high_risk_work_orders = [
        work_order
        for work_order in work_orders
        if work_order.get("risk_score", 0) >= 80
    ]

    average_risk_score = (
        round(
            sum(
                work_order.get("risk_score", 0)
                for work_order in work_orders
            )
            / len(work_orders),
            2
        )
        if work_orders
        else 0
    )

    average_confidence = (
        round(
            sum(
                work_order.get("confidence", 0)
                for work_order in work_orders
            )
            / len(work_orders),
            2
        )
        if work_orders
        else 0
    )

    return {
        "total_work_orders": len(work_orders),
        "open_work_orders": len(open_work_orders),
        "overdue_work_orders": len(overdue_work_orders),
        "high_risk_work_orders": len(high_risk_work_orders),
        "rca_linked_work_orders": sum(
            1
            for work_order in work_orders
            if work_order.get("linked_rca_case_id")
        ),
        "average_risk_score": average_risk_score,
        "average_confidence": average_confidence,
        "status_counts": dict(status_counts),
        "priority_counts": dict(priority_counts),
        "maintenance_type_counts": dict(maintenance_type_counts),
        "asset_counts": dict(asset_counts)
    }


def get_maintenance_recommendations(
    asset_id: str | None = None,
    limit: int = 5
) -> list[dict[str, Any]]:
    work_orders = filter_work_orders(asset_id=asset_id)

    eligible_work_orders = [
        work_order
        for work_order in work_orders
        if work_order.get("status") not in {
            "Completed",
            "Cancelled"
        }
    ]

    ranked_work_orders = sorted(
        eligible_work_orders,
        key=lambda item: (
            -STATUS_ORDER.get(item.get("status", ""), 0),
            -PRIORITY_ORDER.get(item.get("priority", ""), 0),
            -item.get("risk_score", 0),
            -item.get("confidence", 0),
            _parse_datetime(item.get("due_at"))
            or datetime.max.replace(tzinfo=timezone.utc)
        )
    )

    recommendations: list[dict[str, Any]] = []

    for position, work_order in enumerate(
        ranked_work_orders[:limit],
        start=1
    ):
        recommendations.append(
            {
                "rank": position,
                "work_order_id": work_order["work_order_id"],
                "asset_id": work_order["asset_id"],
                "title": work_order["title"],
                "priority": work_order["priority"],
                "status": work_order["status"],
                "risk_score": work_order["risk_score"],
                "confidence": work_order["confidence"],
                "due_at": work_order["due_at"],
                "owner_role": work_order["owner_role"],
                "linked_rca_case_id": work_order[
                    "linked_rca_case_id"
                ],
                "recommendation": (
                    f"Prioritize {work_order['title']} for "
                    f"{work_order['asset_id']} based on "
                    f"{work_order['priority'].lower()} priority, "
                    f"risk score {work_order['risk_score']} and "
                    f"confidence {work_order['confidence']}."
                )
            }
        )

    return recommendations