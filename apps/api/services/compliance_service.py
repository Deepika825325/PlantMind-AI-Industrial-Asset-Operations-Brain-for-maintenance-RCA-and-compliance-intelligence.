from datetime import datetime, timezone
from functools import lru_cache
import re
from typing import Any

from apps.api.repositories.registry import (
    get_repository_registry,
)


ACTIVE_STATUSES = {
    "open",
    "planned",
    "in progress",
    "delayed",
    "recommended",
}

COMPLETED_STATUSES = {
    "completed",
    "closed",
}

CANCELLED_STATUSES = {
    "cancelled",
    "canceled",
}

INSPECTION_WORDS = {
    "inspect",
    "inspection",
    "check",
    "test",
    "verify",
    "verification",
    "assessment",
}

SEVERITY_PENALTY_KEYS = {
    "critical": "critical_gap_penalty",
    "high": "high_gap_penalty",
    "medium": "medium_gap_penalty",
}


def _generated_at() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    normalized = value.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _is_completed(status: str | None) -> bool:
    return _normalize(status) in COMPLETED_STATUSES


def _is_cancelled(status: str | None) -> bool:
    return _normalize(status) in CANCELLED_STATUSES


def _is_active(status: str | None) -> bool:
    normalized = _normalize(status)

    return (
        normalized in ACTIVE_STATUSES
        or (
            normalized
            and normalized not in COMPLETED_STATUSES
            and normalized not in CANCELLED_STATUSES
        )
    )


def _load_assets() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.assets.list_assets()


def _load_documents() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.documents.list_documents()


def _load_rule_data() -> dict[str, Any]:
    repositories = get_repository_registry()
    return repositories.compliance.get_rules()


def _load_work_orders() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.work_orders.list_work_orders()


def _load_rca_cases() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.rca.list_cases()


def _get_asset(asset_id: str) -> dict[str, Any] | None:
    normalized_asset_id = asset_id.upper()

    for asset in _load_assets():
        if asset.get("asset_id") == normalized_asset_id:
            return asset

    return None


def _get_asset_documents(asset_id: str) -> list[dict[str, Any]]:
    normalized_asset_id = asset_id.upper()
    results = []

    for document in _load_documents():
        asset_ids = {
            str(item).upper()
            for item in document.get("asset_ids", [])
        }

        tags = {
            str(item).upper()
            for item in document.get("tags", [])
        }

        if normalized_asset_id in asset_ids or normalized_asset_id in tags:
            results.append(document)

    return results


def _get_asset_work_orders(asset_id: str) -> list[dict[str, Any]]:
    normalized_asset_id = asset_id.upper()

    return [
        work_order
        for work_order in _load_work_orders()
        if work_order.get("asset_id") == normalized_asset_id
    ]


def _get_asset_rca_cases(asset_id: str) -> list[dict[str, Any]]:
    normalized_asset_id = asset_id.upper()

    return [
        case
        for case in _load_rca_cases()
        if case.get("asset_id") == normalized_asset_id
    ]


@lru_cache(maxsize=128)
def _read_document_text(document_id: str) -> str:
    repositories = get_repository_registry()

    return repositories.documents.read_document_text(
        document_id
    )


def _get_requirement_document_ids(
    documents: list[dict[str, Any]],
) -> list[str]:
    return sorted(
        {
            str(document.get("document_id"))
            for document in documents
            if document.get("document_id")
            and (
                document.get("source_group") == "manuals_sops"
                or document.get("document_type")
                in {
                    "SOP",
                    "SOP / Manual",
                    "Compliance Checklist",
                }
            )
        }
    )


def _get_rca_document_ids(
    rca_cases: list[dict[str, Any]],
) -> list[str]:
    document_ids = set()

    for case in rca_cases:
        for evidence in case.get("evidence", []):
            document_id = evidence.get("document_id")

            if document_id:
                document_ids.add(str(document_id))

    return sorted(document_ids)


def _get_linked_rca_ids(
    rca_cases: list[dict[str, Any]],
) -> list[str]:
    return sorted(
        {
            str(case.get("case_id"))
            for case in rca_cases
            if case.get("case_id")
        }
    )


def _is_inspection_work_order(
    work_order: dict[str, Any],
) -> bool:
    maintenance_type = _normalize(
        work_order.get("maintenance_type")
    )

    title_words = set(
        re.findall(
            r"[a-z]+",
            _normalize(work_order.get("title")),
        )
    )

    return (
        maintenance_type
        in {
            "condition-based",
            "verification",
            "predictive",
        }
        or bool(title_words.intersection(INSPECTION_WORDS))
    )


def _work_order_requires_permit(
    work_order: dict[str, Any],
) -> bool:
    safety_text = " ".join(
        str(item)
        for item in work_order.get(
            "safety_requirements",
            [],
        )
    ).lower()

    return (
        "work permit" in safety_text
        or "isolation" in safety_text
        or "zero rotational energy" in safety_text
        or "zero-energy" in safety_text
    )


def _work_order_requires_loto(
    work_order: dict[str, Any],
) -> bool:
    safety_text = " ".join(
        str(item)
        for item in work_order.get(
            "safety_requirements",
            [],
        )
    ).lower()

    return (
        "lockout" in safety_text
        or "tagout" in safety_text
        or "loto" in safety_text
    )


def _build_rule_result(
    rule: dict[str, Any],
    status: str,
    description: str,
    available_evidence: list[str],
    missing_evidence: list[str],
    linked_document_ids: list[str],
    linked_work_order_ids: list[str],
    linked_rca_case_ids: list[str],
    confidence: float,
) -> dict[str, Any]:
    return {
        "rule_id": rule["rule_id"],
        "rule_name": rule["rule_name"],
        "severity": rule["default_severity"],
        "status": status,
        "description": description,
        "required_evidence": rule.get(
            "required_evidence",
            [],
        ),
        "available_evidence": sorted(
            set(available_evidence)
        ),
        "missing_evidence": sorted(
            set(missing_evidence)
        ),
        "linked_document_ids": sorted(
            set(linked_document_ids)
        ),
        "linked_work_order_ids": sorted(
            set(linked_work_order_ids)
        ),
        "linked_rca_case_ids": sorted(
            set(linked_rca_case_ids)
        ),
        "recommendation": rule["recommendation"],
        "confidence": confidence,
    }


def _evaluate_c001(
    rule: dict[str, Any],
    asset_id: str,
    documents: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    rca_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    vibration_documents = [
        document
        for document in documents
        if "vibration" in _normalize(
            document.get("title")
        )
        and "inspection" in _normalize(
            document.get("document_type")
        )
    ]

    matching_documents = []

    for document in vibration_documents:
        document_id = str(document.get("document_id"))
        text = _read_document_text(document_id)

        if re.search(
            r"\b\d+(?:\.\d+)?\s*mm/s\b",
            text,
            re.IGNORECASE,
        ):
            matching_documents.append(document)

    linked_document_ids = [
        str(document.get("document_id"))
        for document in matching_documents
        if document.get("document_id")
    ]

    if matching_documents:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"{asset_id} has a documented numeric "
                "vibration measurement."
            ),
            available_evidence=[
                f"Numeric vibration reading in {document_id}"
                for document_id in linked_document_ids
            ],
            missing_evidence=[],
            linked_document_ids=linked_document_ids,
            linked_work_order_ids=[],
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.99,
        )

    return _build_rule_result(
        rule=rule,
        status="Failed",
        description=(
            f"No numeric vibration reading was found "
            f"for {asset_id}."
        ),
        available_evidence=[],
        missing_evidence=rule["required_evidence"],
        linked_document_ids=[
            str(document.get("document_id"))
            for document in vibration_documents
            if document.get("document_id")
        ],
        linked_work_order_ids=[
            str(work_order.get("work_order_id"))
            for work_order in work_orders
            if _is_inspection_work_order(work_order)
        ],
        linked_rca_case_ids=_get_linked_rca_ids(
            rca_cases
        ),
        confidence=0.96,
    )


def _evaluate_c002(
    rule: dict[str, Any],
    asset_id: str,
    documents: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    rca_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    verification_orders = [
        work_order
        for work_order in work_orders
        if (
            _normalize(
                work_order.get("maintenance_type")
            )
            == "verification"
            or "post-maintenance"
            in _normalize(work_order.get("title"))
        )
    ]

    completed_orders = [
        work_order
        for work_order in verification_orders
        if _is_completed(work_order.get("status"))
        and work_order.get("completion_notes")
    ]

    linked_work_order_ids = [
        str(work_order.get("work_order_id"))
        for work_order in verification_orders
        if work_order.get("work_order_id")
    ]

    if verification_orders and completed_orders:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"{asset_id} has completed "
                "post-maintenance verification."
            ),
            available_evidence=[
                f"Completed verification work order "
                f"{work_order['work_order_id']}"
                for work_order in completed_orders
            ],
            missing_evidence=[],
            linked_document_ids=[],
            linked_work_order_ids=linked_work_order_ids,
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.98,
        )

    available_evidence = [
        f"Verification work order "
        f"{work_order['work_order_id']} exists with "
        f"status {work_order.get('status')}"
        for work_order in verification_orders
    ]

    return _build_rule_result(
        rule=rule,
        status="Failed",
        description=(
            f"{asset_id} does not have a completed "
            "post-maintenance inspection with recorded results."
        ),
        available_evidence=available_evidence,
        missing_evidence=[
            "Completed verification work order",
            "Post-maintenance inspection result",
            "Recorded executed verification value",
        ],
        linked_document_ids=[],
        linked_work_order_ids=linked_work_order_ids,
        linked_rca_case_ids=_get_linked_rca_ids(
            rca_cases
        ),
        confidence=0.98,
    )


def _evaluate_c003(
    rule: dict[str, Any],
    asset_id: str,
    documents: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    rca_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    controlled_orders = [
        work_order
        for work_order in work_orders
        if _work_order_requires_permit(work_order)
    ]

    evidence_documents = [
        document
        for document in documents
        if document.get("source_group")
        not in {
            "manuals_sops",
            "compliance",
        }
        and "supervisor" in _normalize(
            _read_document_text(
                str(document.get("document_id"))
            )
        )
        and re.search(
            r"approved|approval|signed|sign-off",
            _read_document_text(
                str(document.get("document_id"))
            ),
            re.IGNORECASE,
        )
    ]

    linked_work_order_ids = [
        str(work_order.get("work_order_id"))
        for work_order in controlled_orders
        if work_order.get("work_order_id")
    ]

    linked_document_ids = [
        str(document.get("document_id"))
        for document in evidence_documents
        if document.get("document_id")
    ]

    if not controlled_orders:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"No permit-controlled maintenance was "
                f"identified for {asset_id}."
            ),
            available_evidence=[],
            missing_evidence=[],
            linked_document_ids=[],
            linked_work_order_ids=[],
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.95,
        )

    if evidence_documents:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"Supervisor approval evidence is available "
                f"for {asset_id}."
            ),
            available_evidence=[
                f"Supervisor approval in {document_id}"
                for document_id in linked_document_ids
            ],
            missing_evidence=[],
            linked_document_ids=linked_document_ids,
            linked_work_order_ids=linked_work_order_ids,
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.94,
        )

    requirement_documents = [
        document_id
        for document_id in _get_requirement_document_ids(
            documents
        )
        if "SOP-GEN-001" in document_id
    ]

    return _build_rule_result(
        rule=rule,
        status="Failed",
        description=(
            f"{asset_id} has permit-controlled work orders, "
            "but no supervisor approval record with a "
            "name and timestamp is attached."
        ),
        available_evidence=[
            "Supervisor sign-off is required by SOP-GEN-001"
        ],
        missing_evidence=rule["required_evidence"],
        linked_document_ids=requirement_documents,
        linked_work_order_ids=linked_work_order_ids,
        linked_rca_case_ids=_get_linked_rca_ids(
            rca_cases
        ),
        confidence=0.93,
    )


def _evaluate_c004(
    rule: dict[str, Any],
    asset_id: str,
    documents: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    rca_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    loto_orders = [
        work_order
        for work_order in work_orders
        if _work_order_requires_loto(work_order)
    ]

    loto_evidence_documents = [
        document
        for document in documents
        if document.get("source_group")
        not in {
            "manuals_sops",
            "compliance",
        }
        and (
            "loto" in _normalize(
                document.get("document_id")
            )
            or "lockout" in _normalize(
                document.get("title")
            )
        )
    ]

    linked_work_order_ids = [
        str(work_order.get("work_order_id"))
        for work_order in loto_orders
        if work_order.get("work_order_id")
    ]

    linked_document_ids = [
        str(document.get("document_id"))
        for document in loto_evidence_documents
        if document.get("document_id")
    ]

    if not loto_orders:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"No LOTO-controlled maintenance was "
                f"identified for {asset_id}."
            ),
            available_evidence=[],
            missing_evidence=[],
            linked_document_ids=[],
            linked_work_order_ids=[],
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.96,
        )

    if loto_evidence_documents:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"A LOTO evidence record is available "
                f"for {asset_id}."
            ),
            available_evidence=[
                f"LOTO evidence document {document_id}"
                for document_id in linked_document_ids
            ],
            missing_evidence=[],
            linked_document_ids=linked_document_ids,
            linked_work_order_ids=linked_work_order_ids,
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.96,
        )

    requirement_documents = [
        document_id
        for document_id in _get_requirement_document_ids(
            documents
        )
        if "SOP-GEN-001" in document_id
    ]

    return _build_rule_result(
        rule=rule,
        status="Failed",
        description=(
            f"{asset_id} requires lockout and tagout, "
            "but no completed LOTO checklist is attached."
        ),
        available_evidence=[
            "LOTO is required by SOP-GEN-001"
        ],
        missing_evidence=rule["required_evidence"],
        linked_document_ids=requirement_documents,
        linked_work_order_ids=linked_work_order_ids,
        linked_rca_case_ids=_get_linked_rca_ids(
            rca_cases
        ),
        confidence=0.97,
    )


def _evaluate_c005(
    rule: dict[str, Any],
    asset_id: str,
    documents: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    rca_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    current_time = datetime.now(timezone.utc)

    overdue_orders = []

    for work_order in work_orders:
        due_at = _parse_datetime(
            work_order.get("due_at")
        )

        if (
            due_at
            and due_at < current_time
            and _is_active(work_order.get("status"))
            and _is_inspection_work_order(work_order)
        ):
            overdue_orders.append(work_order)

    linked_work_order_ids = [
        str(work_order.get("work_order_id"))
        for work_order in overdue_orders
        if work_order.get("work_order_id")
    ]

    if not overdue_orders:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"No overdue inspection or verification "
                f"work orders were found for {asset_id}."
            ),
            available_evidence=[],
            missing_evidence=[],
            linked_document_ids=[],
            linked_work_order_ids=[],
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.99,
        )

    return _build_rule_result(
        rule=rule,
        status="Failed",
        description=(
            f"{asset_id} has {len(overdue_orders)} overdue "
            "inspection or verification work order(s)."
        ),
        available_evidence=[
            f"{work_order['work_order_id']} was due "
            f"{work_order.get('due_at')}"
            for work_order in overdue_orders
        ],
        missing_evidence=[
            "Completed inspection result",
            "Inspection completion timestamp",
        ],
        linked_document_ids=[],
        linked_work_order_ids=linked_work_order_ids,
        linked_rca_case_ids=_get_linked_rca_ids(
            rca_cases
        ),
        confidence=0.99,
    )


def _evaluate_c006(
    rule: dict[str, Any],
    asset_id: str,
    documents: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    rca_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    closed_orders = [
        work_order
        for work_order in work_orders
        if _is_completed(work_order.get("status"))
    ]

    unverified_orders = [
        work_order
        for work_order in closed_orders
        if not work_order.get("completion_notes")
    ]

    linked_work_order_ids = [
        str(work_order.get("work_order_id"))
        for work_order in closed_orders
        if work_order.get("work_order_id")
    ]

    if not unverified_orders:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"No closed work order without verification "
                f"was found for {asset_id}."
            ),
            available_evidence=[
                f"Closed work order {work_order['work_order_id']} "
                "contains completion notes"
                for work_order in closed_orders
            ],
            missing_evidence=[],
            linked_document_ids=[],
            linked_work_order_ids=linked_work_order_ids,
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.98,
        )

    return _build_rule_result(
        rule=rule,
        status="Failed",
        description=(
            f"{asset_id} has closed work orders without "
            "recorded verification evidence."
        ),
        available_evidence=[],
        missing_evidence=rule["required_evidence"],
        linked_document_ids=[],
        linked_work_order_ids=[
            str(work_order.get("work_order_id"))
            for work_order in unverified_orders
            if work_order.get("work_order_id")
        ],
        linked_rca_case_ids=_get_linked_rca_ids(
            rca_cases
        ),
        confidence=0.98,
    )


def _evaluate_c007(
    rule: dict[str, Any],
    asset_id: str,
    documents: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    rca_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    available_document_ids = {
        str(document.get("document_id"))
        for document in _load_documents()
        if document.get("document_id")
    }

    missing_procedure_orders = [
        work_order
        for work_order in work_orders
        if (
            not work_order.get("required_procedure")
            or str(
                work_order.get("required_procedure")
            )
            not in available_document_ids
        )
    ]

    linked_document_ids = [
        str(work_order.get("required_procedure"))
        for work_order in work_orders
        if work_order.get("required_procedure")
        and str(
            work_order.get("required_procedure")
        )
        in available_document_ids
    ]

    linked_work_order_ids = [
        str(work_order.get("work_order_id"))
        for work_order in work_orders
        if work_order.get("work_order_id")
    ]

    if not missing_procedure_orders:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"All controlled maintenance work orders "
                f"for {asset_id} reference available SOPs."
            ),
            available_evidence=[
                f"Linked procedure {document_id}"
                for document_id in linked_document_ids
            ],
            missing_evidence=[],
            linked_document_ids=linked_document_ids,
            linked_work_order_ids=linked_work_order_ids,
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.99,
        )

    return _build_rule_result(
        rule=rule,
        status="Failed",
        description=(
            f"{asset_id} has work orders with missing "
            "or unavailable required procedures."
        ),
        available_evidence=[
            f"Linked procedure {document_id}"
            for document_id in linked_document_ids
        ],
        missing_evidence=[
            "Available applicable SOP",
            "Valid required procedure reference",
        ],
        linked_document_ids=linked_document_ids,
        linked_work_order_ids=[
            str(work_order.get("work_order_id"))
            for work_order in missing_procedure_orders
            if work_order.get("work_order_id")
        ],
        linked_rca_case_ids=_get_linked_rca_ids(
            rca_cases
        ),
        confidence=0.99,
    )


def _evaluate_c008(
    rule: dict[str, Any],
    asset_id: str,
    documents: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    rca_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    incomplete_orders = [
        work_order
        for work_order in work_orders
        if (
            _is_active(work_order.get("status"))
            and not work_order.get("completion_notes")
        )
    ]

    linked_work_order_ids = [
        str(work_order.get("work_order_id"))
        for work_order in incomplete_orders
        if work_order.get("work_order_id")
    ]

    linked_document_ids = sorted(
        set(
            _get_requirement_document_ids(documents)
            + _get_rca_document_ids(rca_cases)
        )
    )

    available_evidence = []

    for work_order in incomplete_orders:
        for evidence_id in work_order.get(
            "linked_evidence_ids",
            [],
        ):
            available_evidence.append(
                f"Linked diagnostic evidence {evidence_id}"
            )

        if work_order.get("required_procedure"):
            available_evidence.append(
                f"Required procedure "
                f"{work_order['required_procedure']}"
            )

    if not incomplete_orders:
        return _build_rule_result(
            rule=rule,
            status="Passed",
            description=(
                f"Maintenance evidence is complete for "
                f"{asset_id}."
            ),
            available_evidence=available_evidence,
            missing_evidence=[],
            linked_document_ids=linked_document_ids,
            linked_work_order_ids=[],
            linked_rca_case_ids=_get_linked_rca_ids(
                rca_cases
            ),
            confidence=0.95,
        )

    return _build_rule_result(
        rule=rule,
        status="Failed",
        description=(
            f"{asset_id} has {len(incomplete_orders)} active "
            "work order(s) without completion evidence."
        ),
        available_evidence=available_evidence,
        missing_evidence=[
            "Completion notes",
            "Executed verification result",
            "Completion timestamp",
            "Required safety evidence",
        ],
        linked_document_ids=linked_document_ids,
        linked_work_order_ids=linked_work_order_ids,
        linked_rca_case_ids=_get_linked_rca_ids(
            rca_cases
        ),
        confidence=0.96,
    )


RULE_EVALUATORS = {
    "C001": _evaluate_c001,
    "C002": _evaluate_c002,
    "C003": _evaluate_c003,
    "C004": _evaluate_c004,
    "C005": _evaluate_c005,
    "C006": _evaluate_c006,
    "C007": _evaluate_c007,
    "C008": _evaluate_c008,
}


def evaluate_asset_rules(
    asset_id: str,
) -> list[dict[str, Any]]:
    normalized_asset_id = asset_id.upper()
    documents = _get_asset_documents(normalized_asset_id)
    work_orders = _get_asset_work_orders(
        normalized_asset_id
    )
    rca_cases = _get_asset_rca_cases(
        normalized_asset_id
    )

    results = []

    for rule in _load_rule_data().get("rules", []):
        applicable_asset_ids = {
            str(item).upper()
            for item in rule.get(
                "applicable_asset_ids",
                [],
            )
        }

        if (
            applicable_asset_ids
            and normalized_asset_id
            not in applicable_asset_ids
        ):
            continue

        evaluator = RULE_EVALUATORS.get(
            rule.get("rule_id")
        )

        if not evaluator:
            continue

        results.append(
            evaluator(
                rule,
                normalized_asset_id,
                documents,
                work_orders,
                rca_cases,
            )
        )

    return results


def _build_gap(
    asset_id: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "gap_id": (
            f"GAP-{asset_id.replace('-', '')}-"
            f"{result['rule_id']}"
        ),
        "asset_id": asset_id,
        "rule_id": result["rule_id"],
        "rule_name": result["rule_name"],
        "severity": result["severity"],
        "status": "Open",
        "description": result["description"],
        "required_evidence": result[
            "required_evidence"
        ],
        "available_evidence": result[
            "available_evidence"
        ],
        "missing_evidence": result[
            "missing_evidence"
        ],
        "linked_document_ids": result[
            "linked_document_ids"
        ],
        "linked_work_order_ids": result[
            "linked_work_order_ids"
        ],
        "linked_rca_case_ids": result[
            "linked_rca_case_ids"
        ],
        "recommendation": result[
            "recommendation"
        ],
        "confidence": result["confidence"],
    }


def _calculate_score(
    gaps: list[dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    scoring = _load_rule_data().get(
        "scoring",
        {},
    )

    severity_counts = {
        severity: sum(
            1
            for gap in gaps
            if _normalize(gap.get("severity"))
            == severity
        )
        for severity in [
            "critical",
            "high",
            "medium",
        ]
    }

    critical_value = int(
        scoring.get("critical_gap_penalty", 0)
    )

    high_value = int(
        scoring.get("high_gap_penalty", 0)
    )

    medium_value = int(
        scoring.get("medium_gap_penalty", 0)
    )

    penalty_caps = scoring.get(
        "severity_penalty_caps",
        {},
    )

    raw_critical_penalty = (
        severity_counts["critical"]
        * critical_value
    )

    raw_high_penalty = (
        severity_counts["high"]
        * high_value
    )

    raw_medium_penalty = (
        severity_counts["medium"]
        * medium_value
    )

    critical_penalty = min(
        raw_critical_penalty,
        int(
            penalty_caps.get(
                "critical",
                raw_critical_penalty,
            )
        ),
    )

    high_penalty = min(
        raw_high_penalty,
        int(
            penalty_caps.get(
                "high",
                raw_high_penalty,
            )
        ),
    )

    medium_penalty = min(
        raw_medium_penalty,
        int(
            penalty_caps.get(
                "medium",
                raw_medium_penalty,
            )
        ),
    )

    severity_penalty = (
        critical_penalty
        + high_penalty
        + medium_penalty
    )

    missing_evidence_gap_count = sum(
        1
        for gap in gaps
        if gap.get("missing_evidence")
    )

    missing_evidence_penalty = (
        int(
            scoring.get(
                "missing_evidence_penalty",
                0,
            )
        )
        if missing_evidence_gap_count
        else 0
    )

    overdue_work_order_ids = {
        work_order_id
        for gap in gaps
        if gap.get("rule_id") == "C005"
        for work_order_id in gap.get(
            "linked_work_order_ids",
            [],
        )
    }

    overdue_action_penalty = (
        int(
            scoring.get(
                "overdue_action_penalty",
                0,
            )
        )
        if overdue_work_order_ids
        else 0
    )

    total_penalty = (
        severity_penalty
        + missing_evidence_penalty
        + overdue_action_penalty
    )

    maximum_score = int(
        scoring.get("maximum_score", 100)
    )

    minimum_score = int(
        scoring.get("minimum_score", 0)
    )

    score = max(
        minimum_score,
        min(
            maximum_score,
            maximum_score - total_penalty,
        ),
    )

    breakdown = {
        "maximum_score": maximum_score,
        "gap_counts": severity_counts,
        "raw_severity_penalties": {
            "critical": raw_critical_penalty,
            "high": raw_high_penalty,
            "medium": raw_medium_penalty,
        },
        "applied_severity_penalties": {
            "critical": critical_penalty,
            "high": high_penalty,
            "medium": medium_penalty,
        },
        "severity_penalty": severity_penalty,
        "missing_evidence_gap_count": (
            missing_evidence_gap_count
        ),
        "missing_evidence_penalty": (
            missing_evidence_penalty
        ),
        "overdue_action_count": len(
            overdue_work_order_ids
        ),
        "overdue_action_penalty": (
            overdue_action_penalty
        ),
        "total_penalty": total_penalty,
        "final_score": score,
        "formula": scoring.get("formula"),
        "penalty_values": {
            "critical_gap": critical_value,
            "high_gap": high_value,
            "medium_gap": medium_value,
            "missing_evidence": scoring.get(
                "missing_evidence_penalty"
            ),
            "overdue_action": scoring.get(
                "overdue_action_penalty"
            ),
        },
        "penalty_caps": penalty_caps,
    }

    return score, breakdown

def get_asset_audit_package(
    asset_id: str,
) -> dict[str, Any] | None:
    normalized_asset_id = asset_id.upper()
    asset = _get_asset(normalized_asset_id)

    if not asset:
        return None

    rule_results = evaluate_asset_rules(
        normalized_asset_id
    )

    passed_rules = [
        result
        for result in rule_results
        if result.get("status") == "Passed"
    ]

    failed_rules = [
        result
        for result in rule_results
        if result.get("status") == "Failed"
    ]

    open_gaps = [
        _build_gap(normalized_asset_id, result)
        for result in failed_rules
    ]

    score, scoring_breakdown = _calculate_score(
        open_gaps
    )

    documents = _get_asset_documents(
        normalized_asset_id
    )

    related_inspections = [
        document
        for document in documents
        if "inspection" in _normalize(
            document.get("document_type")
        )
    ]

    related_work_orders = _get_asset_work_orders(
        normalized_asset_id
    )

    related_rca_cases = _get_asset_rca_cases(
        normalized_asset_id
    )

    return {
        "asset": asset,
        "audit_readiness_score": score,
        "scoring_breakdown": scoring_breakdown,
        "applicable_rules": rule_results,
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
        "open_gaps": open_gaps,
        "evidence_documents": documents,
        "related_inspections": related_inspections,
        "related_work_orders": related_work_orders,
        "related_rca_cases": related_rca_cases,
        "recommended_actions": sorted(
            {
                gap["recommendation"]
                for gap in open_gaps
            }
        ),
        "generated_at": _generated_at(),
    }


def get_compliance_gaps(
    asset_id: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    rule_id: str | None = None,
    evidence_availability: str | None = None,
) -> dict[str, Any]:
    asset_ids = [
        asset_id.upper()
    ] if asset_id else [
        str(asset.get("asset_id"))
        for asset in _load_assets()
        if asset.get("asset_id")
    ]

    gaps = []

    for current_asset_id in asset_ids:
        package = get_asset_audit_package(
            current_asset_id
        )

        if package:
            gaps.extend(package["open_gaps"])

    if severity:
        gaps = [
            gap
            for gap in gaps
            if _normalize(gap.get("severity"))
            == _normalize(severity)
        ]

    if status:
        gaps = [
            gap
            for gap in gaps
            if _normalize(gap.get("status"))
            == _normalize(status)
        ]

    if rule_id:
        gaps = [
            gap
            for gap in gaps
            if _normalize(gap.get("rule_id"))
            == _normalize(rule_id)
        ]

    if evidence_availability:
        normalized_filter = _normalize(
            evidence_availability
        )

        if normalized_filter == "missing":
            gaps = [
                gap
                for gap in gaps
                if not gap.get("available_evidence")
            ]

        elif normalized_filter == "partial":
            gaps = [
                gap
                for gap in gaps
                if gap.get("available_evidence")
                and gap.get("missing_evidence")
            ]

    return {
        "total": len(gaps),
        "gaps": gaps,
        "filters": {
            "asset_id": asset_id,
            "severity": severity,
            "status": status,
            "rule_id": rule_id,
            "evidence_availability": (
                evidence_availability
            ),
        },
    }


def get_compliance_overview() -> dict[str, Any]:
    asset_summaries = []
    all_gaps = []

    for asset in _load_assets():
        asset_id = asset.get("asset_id")

        if not asset_id:
            continue

        package = get_asset_audit_package(
            str(asset_id)
        )

        if not package:
            continue

        gaps = package["open_gaps"]
        all_gaps.extend(gaps)

        asset_summaries.append(
            {
                "asset_id": asset_id,
                "asset_name": asset.get("asset_name"),
                "audit_readiness_score": package[
                    "audit_readiness_score"
                ],
                "total_rules": len(
                    package["applicable_rules"]
                ),
                "passed_rules": len(
                    package["passed_rules"]
                ),
                "failed_rules": len(
                    package["failed_rules"]
                ),
                "open_gaps": len(gaps),
                "critical_gaps": sum(
                    1
                    for gap in gaps
                    if gap.get("severity")
                    == "Critical"
                ),
                "high_gaps": sum(
                    1
                    for gap in gaps
                    if gap.get("severity")
                    == "High"
                ),
                "medium_gaps": sum(
                    1
                    for gap in gaps
                    if gap.get("severity")
                    == "Medium"
                ),
            }
        )

    scores = [
        summary["audit_readiness_score"]
        for summary in asset_summaries
    ]

    severity_distribution = {
        severity: sum(
            1
            for gap in all_gaps
            if gap.get("severity") == severity
        )
        for severity in [
            "Critical",
            "High",
            "Medium",
            "Low",
        ]
    }

    return {
        "artifact": "compliance_intelligence",
        "generated_at": _generated_at(),
        "audit_readiness_formula": (
            _load_rule_data()
            .get("scoring", {})
            .get("formula")
        ),
        "average_audit_readiness_score": (
            round(sum(scores) / len(scores), 2)
            if scores
            else 0
        ),
        "total_assets": len(asset_summaries),
        "total_open_gaps": len(all_gaps),
        "missing_evidence_gaps": sum(
            1
            for gap in all_gaps
            if gap.get("missing_evidence")
        ),
        "severity_distribution": (
            severity_distribution
        ),
        "asset_compliance_summary": (
            asset_summaries
        ),
        "gaps": all_gaps,
    }


def get_compliance_rules() -> dict[str, Any]:
    return _load_rule_data()