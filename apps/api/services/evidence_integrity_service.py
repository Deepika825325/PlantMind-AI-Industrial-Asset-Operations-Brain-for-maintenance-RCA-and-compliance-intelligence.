from __future__ import annotations

from pathlib import Path
from typing import Any
import re

from apps.api.services.compliance_service import (
    get_asset_audit_package,
)
from apps.api.services.data_loader import (
    get_document_chunks,
    get_documents,
)
from apps.api.services.maintenance_service import (
    get_work_order,
)
from apps.api.services.rca_service import (
    get_rca_case,
    get_rca_cases_for_asset,
    list_rca_cases,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

UNSUPPORTED_ANSWER = (
    "PlantMind could not find sufficient evidence "
    "to support a reliable conclusion."
)

ASSET_PATTERN = re.compile(
    r"\b(?:P|C|HX)-\d{3}\b",
    re.IGNORECASE,
)

VALIDATION_STATUSES = {
    "verified": "Verified",
    "partial": "Partially verified",
    "unavailable": "Unavailable",
}


def normalize_text(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )
    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def extract_asset_ids(value: Any) -> list[str]:
    if isinstance(value, list):
        text = " ".join(
            str(item)
            for item in value
        )
    else:
        text = str(value or "")

    return list(
        dict.fromkeys(
            match.group(0).upper()
            for match in ASSET_PATTERN.finditer(
                text
            )
        )
    )


def get_source_quality(
    source_type: str | None,
    source_kind: str | None = None,
) -> dict[str, str]:
    normalized_type = normalize_text(
        source_type
    )

    normalized_kind = normalize_text(
        source_kind
    )

    if (
        "sop" in normalized_type
        or "procedure" in normalized_type
        or "safety procedure" in normalized_type
    ):
        return {
            "label": "Official SOP",
            "rating": "High",
        }

    if (
        "inspection" in normalized_type
        or "compliance checklist"
        in normalized_type
        or "audit" in normalized_type
    ):
        return {
            "label": "Inspection report",
            "rating": "High",
        }

    if (
        "maintenance" in normalized_type
        or "work order" in normalized_type
        or normalized_kind == "work order"
    ):
        return {
            "label": "Maintenance record",
            "rating": "High",
        }

    if "incident" in normalized_type:
        return {
            "label": "Incident report",
            "rating": "Medium-High",
        }

    if (
        "sensor" in normalized_type
        or normalized_kind == "sensor evidence"
    ):
        return {
            "label": "Sensor extract",
            "rating": "Medium-High",
        }

    if "operator" in normalized_type:
        return {
            "label": "Operator note",
            "rating": "Medium",
        }

    if (
        "root cause" in normalized_type
        or "recommendation" in normalized_type
        or "corrective action" in normalized_type
        or "compliance gap" in normalized_type
        or normalized_kind in {
            "rca case",
            "compliance gap",
        }
    ):
        return {
            "label": "Generated recommendation",
            "rating": "Derived",
        }

    return {
        "label": "Generated recommendation",
        "rating": "Derived",
    }


def get_document_lookup() -> dict[str, dict[str, Any]]:
    return {
        str(document["document_id"]): document
        for document in get_documents()
        if document.get("document_id")
    }


def get_chunk_lookup() -> dict[str, list[dict[str, Any]]]:
    lookup: dict[
        str,
        list[dict[str, Any]]
    ] = {}

    for chunk in get_document_chunks():
        document_id = str(
            chunk.get("document_id")
            or ""
        )

        if not document_id:
            continue

        lookup.setdefault(
            document_id,
            [],
        ).append(chunk)

    return lookup


def match_document(
    identifier: str,
) -> dict[str, Any] | None:
    document_lookup = get_document_lookup()

    if identifier in document_lookup:
        return document_lookup[identifier]

    matches = [
        document
        for document_id, document
        in document_lookup.items()
        if (
            document_id.startswith(
                f"{identifier}_"
            )
            or identifier.startswith(
                f"{document_id}_"
            )
        )
    ]

    if len(matches) == 1:
        return matches[0]

    return None


def iter_rca_cases(
    asset_id: str | None,
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    if asset_id:
        candidates = get_rca_cases_for_asset(
            asset_id
        )
    else:
        response = list_rca_cases()

        if isinstance(response, dict):
            candidates = (
                response.get("cases")
                or response.get("items")
                or response.get("results")
                or []
            )
        else:
            candidates = response or []

    for candidate in candidates:
        case_id = candidate.get("case_id")

        if not case_id:
            continue

        full_case = get_rca_case(
            str(case_id)
        )

        if full_case:
            cases.append(full_case)

    return cases


def find_rca_evidence(
    identifier: str,
    asset_id: str | None,
) -> tuple[
    dict[str, Any] | None,
    dict[str, Any] | None,
]:
    for case in iter_rca_cases(
        asset_id
    ):
        for evidence in case.get(
            "evidence",
            [],
        ):
            if identifier in {
                str(
                    evidence.get(
                        "evidence_id"
                        or ""
                    )
                ),
                str(
                    evidence.get(
                        "document_id"
                        or ""
                    )
                ),
            }:
                return evidence, case

    return None, None


def find_compliance_gap(
    identifier: str,
    asset_id: str | None,
) -> dict[str, Any] | None:
    if not asset_id:
        return None

    package = get_asset_audit_package(
        asset_id
    )

    if not package:
        return None

    for gap in package.get(
        "open_gaps",
        [],
    ):
        if identifier in {
            str(gap.get("gap_id") or ""),
            str(gap.get("rule_id") or ""),
        }:
            return gap

    return None


def resolve_reference(
    identifier: str,
    asset_id: str | None,
) -> dict[str, Any]:
    document = match_document(
        identifier
    )

    if document:
        document_id = str(
            document.get("document_id")
        )

        chunks = get_chunk_lookup().get(
            document_id,
            [],
        )

        return {
            "exists": True,
            "kind": "document",
            "record": document,
            "asset_ids": [
                str(value).upper()
                for value in document.get(
                    "asset_ids",
                    [],
                )
            ],
            "section_titles": [
                str(
                    chunk.get(
                        "section_title"
                        or ""
                    )
                )
                for chunk in chunks
                if chunk.get(
                    "section_title"
                )
            ],
            "source_type": str(
                document.get(
                    "document_type"
                    or ""
                )
            ),
            "relative_path": (
                document.get(
                    "relative_path"
                )
            ),
        }

    if identifier.startswith("RCA-"):
        case = get_rca_case(
            identifier
        )

        if case:
            return {
                "exists": True,
                "kind": "rca case",
                "record": case,
                "asset_ids": [
                    str(
                        case.get(
                            "asset_id"
                            or ""
                        )
                    ).upper()
                ],
                "section_titles": [
                    str(
                        case.get(
                            "title"
                            or ""
                        )
                    )
                ],
                "source_type": (
                    "Root Cause Analysis"
                ),
                "relative_path": None,
            }

    work_order = get_work_order(
        identifier
    )

    if work_order:
        return {
            "exists": True,
            "kind": "work order",
            "record": work_order,
            "asset_ids": [
                str(
                    work_order.get(
                        "asset_id"
                        or ""
                    )
                ).upper()
            ],
            "section_titles": [
                str(
                    work_order.get(
                        "title"
                        or ""
                    )
                )
            ],
            "source_type": (
                "Maintenance Work Order"
            ),
            "relative_path": None,
        }

    gap = find_compliance_gap(
        identifier,
        asset_id,
    )

    if gap:
        return {
            "exists": True,
            "kind": "compliance gap",
            "record": gap,
            "asset_ids": [
                str(
                    gap.get(
                        "asset_id"
                        or ""
                    )
                ).upper()
            ],
            "section_titles": [
                str(
                    gap.get(
                        "rule_name"
                        or ""
                    )
                ),
                (
                    f"{gap.get('rule_id', '')}: "
                    f"{gap.get('rule_name', '')}"
                ).strip(": "),
            ],
            "source_type": "Compliance Gap",
            "relative_path": None,
        }

    evidence, case = find_rca_evidence(
        identifier,
        asset_id,
    )

    if evidence and case:
        source_type = str(
            evidence.get(
                "document_type"
                or "RCA Evidence"
            )
        )

        source_kind = (
            "sensor evidence"
            if "sensor"
            in normalize_text(source_type)
            else "rca evidence"
        )

        return {
            "exists": True,
            "kind": source_kind,
            "record": evidence,
            "asset_ids": [
                str(
                    case.get(
                        "asset_id"
                        or ""
                    )
                ).upper()
            ],
            "section_titles": [
                str(
                    evidence.get(
                        "section_title"
                        or ""
                    )
                )
            ],
            "source_type": source_type,
            "relative_path": (
                evidence.get(
                    "relative_path"
                )
            ),
        }

    return {
        "exists": False,
        "kind": "unknown",
        "record": None,
        "asset_ids": [],
        "section_titles": [],
        "source_type": "",
        "relative_path": None,
    }


def section_exists(
    section_title: str | None,
    reference: dict[str, Any],
    citation_title: str | None,
    evidence_excerpt: str | None = None,
) -> bool:
    if not reference.get("exists"):
        return False

    normalized_section = normalize_text(
        section_title
    )

    if not normalized_section:
        return False

    available_sections = {
        normalize_text(value)
        for value in reference.get(
            "section_titles",
            [],
        )
        if value
    }

    if normalized_section in available_sections:
        return True

    normalized_title = normalize_text(
        citation_title
    )

    if (
        normalized_section
        == normalized_title
        and reference.get(
            "kind"
        ) != "document"
    ):
        return True

    record = reference.get(
        "record"
    ) or {}

    record_title = normalize_text(
        record.get("title")
        or record.get("document_title")
        or record.get("rule_name")
    )

    if normalized_section == record_title:
        return True

    section_stop_words = {
        "inspection",
        "report",
        "record",
        "document",
        "section",
        "verification",
        "result",
        "results",
    }

    requested_tokens = {
        token
        for token in normalized_section.split()
        if (
            token not in section_stop_words
            and not token.isdigit()
        )
    }

    for available_section in available_sections:
        available_tokens = {
            token
            for token in available_section.split()
            if (
                token not in section_stop_words
                and not token.isdigit()
            )
        }

        if (
            requested_tokens
            and available_tokens
            and (
                requested_tokens
                <= available_tokens
                or available_tokens
                <= requested_tokens
            )
        ):
            return True

    if reference.get("kind") != "document":
        return False

    excerpt = normalize_text(
        evidence_excerpt
    )

    if not excerpt:
        return False

    document_id = str(
        record.get("document_id")
        or ""
    )

    if not document_id:
        return False

    excerpt_stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "for",
        "to",
        "in",
        "on",
        "at",
        "by",
        "with",
        "was",
        "were",
        "is",
        "are",
        "be",
        "been",
        "during",
        "currently",
        "available",
        "not",
        "no",
        "this",
        "that",
    }

    excerpt_tokens = {
        token
        for token in excerpt.split()
        if (
            len(token) >= 4
            and token not in excerpt_stop_words
        )
    }

    if not excerpt_tokens:
        return False

    chunks = get_chunk_lookup().get(
        document_id,
        [],
    )

    for chunk in chunks:
        chunk_text = normalize_text(
            chunk.get("chunk_text")
        )

        chunk_tokens = {
            token
            for token in chunk_text.split()
            if (
                len(token) >= 4
                and token not in excerpt_stop_words
            )
        }

        overlap = (
            excerpt_tokens
            & chunk_tokens
        )

        overlap_ratio = (
            len(overlap)
            / len(excerpt_tokens)
        )

        if (
            len(overlap) >= 2
            and overlap_ratio >= 0.3
        ):
            return True

    return False


def physical_file_exists(
    relative_path: str | None,
    reference_kind: str,
) -> bool | None:
    if reference_kind != "document":
        return None

    if not relative_path:
        return False

    relative = Path(relative_path)

    candidates = [
        PROJECT_ROOT / relative,
        PROJECT_ROOT / "data" / relative,
        PROJECT_ROOT / "data" / "demo" / relative,
        PROJECT_ROOT / "data" / "raw" / relative,
    ]

    return any(
        candidate.exists()
        for candidate in candidates
    )


def validate_citation(
    citation: dict[str, Any],
    asset_id: str | None = None,
) -> dict[str, Any]:
    validated = dict(citation)

    document_id = str(
        citation.get("document_id")
        or citation.get("source_id")
        or citation.get("citation_id")
        or ""
    )

    citation_id = str(
        citation.get("citation_id")
        or document_id
    )

    reference = resolve_reference(
        document_id,
        asset_id,
    )

    excerpt = str(
        citation.get(
            "evidence_excerpt"
        )
        or citation.get("excerpt")
        or citation.get("chunk_text")
        or ""
    ).strip()

    section_title = str(
        citation.get(
            "section_title"
        )
        or ""
    ).strip()

    citation_title = str(
        citation.get(
            "document_title"
        )
        or citation.get("title")
        or ""
    ).strip()

    source_assets = [
        str(value).upper()
        for value in reference.get(
            "asset_ids",
            [],
        )
        if value
    ]

    if asset_id:
        normalized_asset = asset_id.upper()

        asset_matches = (
            normalized_asset
            in source_assets
            or normalized_asset
            in extract_asset_ids(
                " ".join(
                    [
                        document_id,
                        citation_title,
                        excerpt,
                    ]
                )
            )
        )
    else:
        asset_matches = True

    reference_exists = bool(
        reference.get("exists")
    )

    referenced_section_exists = (
        section_exists(
            section_title,
            reference,
            citation_title,
            excerpt,
        )
    )

    excerpt_not_empty = bool(
        excerpt
    )

    file_exists = physical_file_exists(
        reference.get(
            "relative_path"
        ),
        str(
            reference.get(
                "kind"
                or ""
            )
        ),
    )

    evidence_id_exists = (
        reference_exists
        and bool(citation_id)
    )

    physical_reference_valid = (
        file_exists is not False
    )

    required_checks = [
        reference_exists,
        evidence_id_exists,
        referenced_section_exists,
        excerpt_not_empty,
        asset_matches,
        physical_reference_valid,
    ]

    if all(required_checks):
        status = VALIDATION_STATUSES[
            "verified"
        ]
    elif (
        not reference_exists
        or not evidence_id_exists
    ):
        status = VALIDATION_STATUSES[
            "unavailable"
        ]
    else:
        status = VALIDATION_STATUSES[
            "partial"
        ]

    source_type = str(
        citation.get("document_type")
        or reference.get("source_type")
        or ""
    )

    source_quality = get_source_quality(
        source_type,
        str(
            reference.get(
                "kind"
                or ""
            )
        ),
    )

    validated.update(
        {
            "validation_status": status,
            "source_quality": source_quality,
            "validation_details": {
                "reference_exists": (
                    reference_exists
                ),
                "evidence_id_exists": (
                    evidence_id_exists
                ),
                "referenced_section_exists": (
                    referenced_section_exists
                ),
                "excerpt_not_empty": (
                    excerpt_not_empty
                ),
                "asset_matches": (
                    asset_matches
                ),
                "physical_file_exists": (
                    file_exists
                ),
            },
            "resolved_reference_type": (
                reference.get("kind")
            ),
            "resolved_asset_ids": (
                source_assets
            ),
        }
    )

    return validated


def validate_citations(
    citations: list[dict[str, Any]],
    asset_id: str | None = None,
) -> list[dict[str, Any]]:
    return [
        validate_citation(
            citation,
            asset_id,
        )
        for citation in citations
    ]


def get_evidence_not_found(
    validated_citations: list[
        dict[str, Any]
    ],
    explicit_missing_evidence: list[
        str
    ] | None = None,
) -> list[str]:
    missing = list(
        explicit_missing_evidence
        or []
    )

    for citation in validated_citations:
        if (
            citation.get(
                "validation_status"
            )
            == VALIDATION_STATUSES[
                "unavailable"
            ]
        ):
            identifier = str(
                citation.get(
                    "document_id"
                )
                or citation.get(
                    "citation_id"
                )
                or "Unknown evidence"
            )

            missing.append(
                identifier
            )

    return list(
        dict.fromkeys(
            item
            for item in missing
            if item
        )
    )


def build_confidence_explanation(
    confidence: float,
    validated_citations: list[
        dict[str, Any]
    ],
    conflicting_evidence: list[
        str
    ] | None = None,
    evidence_not_found: list[
        str
    ] | None = None,
) -> dict[str, Any]:
    score = max(
        0.0,
        min(
            float(confidence),
            1.0,
        ),
    )

    verified = [
        citation
        for citation in validated_citations
        if citation.get(
            "validation_status"
        )
        == VALIDATION_STATUSES[
            "verified"
        ]
    ]

    partial = [
        citation
        for citation in validated_citations
        if citation.get(
            "validation_status"
        )
        == VALIDATION_STATUSES[
            "partial"
        ]
    ]

    source_ids = {
        str(
            citation.get(
                "document_id"
            )
            or citation.get(
                "citation_id"
            )
        )
        for citation in validated_citations
        if citation.get(
            "validation_status"
        )
        != VALIDATION_STATUSES[
            "unavailable"
        ]
    }

    conflicts = list(
        conflicting_evidence
        or []
    )

    missing = list(
        evidence_not_found
        or []
    )

    why: list[str] = []

    if len(source_ids) >= 3:
        why.append(
            "Strong support from three or more "
            "independent evidence sources"
        )
    elif len(source_ids) == 2:
        why.append(
            "Support from two independent "
            "evidence sources"
        )
    elif len(source_ids) == 1:
        why.append(
            "Support from one evidence source"
        )
    else:
        why.append(
            "No validated evidence source "
            "was available"
        )

    if verified:
        why.append(
            f"{len(verified)} citation"
            f"{'' if len(verified) == 1 else 's'} "
            "passed integrity validation"
        )

    if partial:
        why.append(
            f"{len(partial)} citation"
            f"{'' if len(partial) == 1 else 's'} "
            "was only partially verified"
        )

    if conflicts:
        why.append(
            f"{len(conflicts)} conflicting "
            "evidence item was identified"
            if len(conflicts) == 1
            else (
                f"{len(conflicts)} conflicting "
                "evidence items were identified"
            )
        )
    else:
        why.append(
            "No material conflicting evidence "
            "was identified"
        )

    if missing:
        why.append(
            f"{len(missing)} required evidence "
            "item remains unavailable"
            if len(missing) == 1
            else (
                f"{len(missing)} required evidence "
                "items remain unavailable"
            )
        )

    if score >= 0.85:
        label = "High"
    elif score >= 0.65:
        label = "Medium"
    else:
        label = "Low"

    return {
        "score": round(
            score,
            4,
        ),
        "percentage": round(
            score * 100,
            1,
        ),
        "label": label,
        "why": why,
        "verified_source_count": len(
            verified
        ),
        "partial_source_count": len(
            partial
        ),
        "independent_source_count": len(
            source_ids
        ),
        "conflict_count": len(
            conflicts
        ),
        "missing_evidence_count": len(
            missing
        ),
    }


def build_decision_trace(
    answer: str,
    confidence: float,
    citations: list[dict[str, Any]],
    asset_id: str | None = None,
    reasoning_summary: list[str] | None = None,
    rules_applied: list[str] | None = None,
    conflicting_evidence: list[str] | None = None,
    recommended_action: str | None = None,
    verification_method: str | None = None,
    explicit_missing_evidence: list[
        str
    ] | None = None,
) -> dict[str, Any]:
    validated_citations = (
        validate_citations(
            citations,
            asset_id,
        )
    )

    evidence_not_found = (
        get_evidence_not_found(
            validated_citations,
            explicit_missing_evidence,
        )
    )

    usable_evidence = [
        citation
        for citation in validated_citations
        if citation.get(
            "validation_status"
        )
        in {
            VALIDATION_STATUSES[
                "verified"
            ],
            VALIDATION_STATUSES[
                "partial"
            ],
        }
    ]

    supported = bool(
        usable_evidence
    )

    final_answer = (
        answer
        if supported
        else UNSUPPORTED_ANSWER
    )

    confidence_value = (
        float(confidence)
        if supported
        else 0.0
    )

    confidence_explanation = (
        build_confidence_explanation(
            confidence_value,
            validated_citations,
            conflicting_evidence,
            evidence_not_found,
        )
    )

    return {
        "answer": final_answer,
        "confidence": round(
            confidence_value,
            4,
        ),
        "confidence_explanation": (
            confidence_explanation
        ),
        "evidence_used": (
            validated_citations
        ),
        "evidence_not_found": (
            evidence_not_found
        ),
        "reasoning_summary": list(
            reasoning_summary
            or []
        ),
        "rules_applied": list(
            rules_applied
            or []
        ),
        "conflicting_evidence": list(
            conflicting_evidence
            or []
        ),
        "recommended_action": (
            recommended_action
        ),
        "verification_method": (
            verification_method
        ),
        "supported": supported,
    }


def build_unsupported_decision_trace(
    asset_id: str | None = None,
    evidence_not_found: list[str] | None = None,
    reasoning_summary: list[str] | None = None,
) -> dict[str, Any]:
    return build_decision_trace(
        answer=UNSUPPORTED_ANSWER,
        confidence=0.0,
        citations=[],
        asset_id=asset_id,
        reasoning_summary=(
            reasoning_summary
            or [
                "No validated evidence was available "
                "for a reliable conclusion"
            ]
        ),
        rules_applied=[],
        conflicting_evidence=[],
        recommended_action=(
            "Collect the missing evidence and "
            "repeat the assessment."
        ),
        verification_method=(
            "Provide at least one valid source "
            "with an identifiable section and "
            "non-empty evidence excerpt."
        ),
        explicit_missing_evidence=(
            evidence_not_found
            or [
                "Validated supporting evidence"
            ]
        ),
    )

def unique_strings(
    values: list[Any],
) -> list[str]:
    result: list[str] = []

    for value in values:
        if isinstance(value, list):
            candidates = value
        else:
            candidates = [value]

        for candidate in candidates:
            text = str(
                candidate or ""
            ).strip()

            if text and text not in result:
                result.append(text)

    return result


def iter_nested_records(
    value: Any,
):
    if isinstance(value, dict):
        yield value

        for nested_value in value.values():
            yield from iter_nested_records(
                nested_value
            )

    elif isinstance(value, list):
        for item in value:
            yield from iter_nested_records(
                item
            )


def build_ask_reasoning_summary(
    response: dict[str, Any],
) -> list[str]:
    context = response.get(
        "structured_context"
    ) or {}

    selected_root_cause = context.get(
        "root_cause"
    )

    reasoning: list[str] = []

    if isinstance(
        selected_root_cause,
        dict,
    ):
        title = str(
            selected_root_cause.get(
                "title"
            )
            or selected_root_cause.get(
                "cause_id"
            )
            or "Selected root cause"
        ).strip()

        cause_reasoning = str(
            selected_root_cause.get(
                "reasoning"
            )
            or ""
        ).strip()

        if cause_reasoning:
            reasoning.append(
                f"{title}: {cause_reasoning}"
            )
        else:
            reasoning.append(title)

        evidence_ids = {
            str(value)
            for value in selected_root_cause.get(
                "evidence_ids",
                [],
            )
            if value
        }

        case = context.get("case")

        if isinstance(case, dict):
            for evidence in case.get(
                "evidence",
                [],
            ):
                evidence_id = str(
                    evidence.get(
                        "evidence_id"
                    )
                    or ""
                )

                if (
                    evidence_ids
                    and evidence_id
                    not in evidence_ids
                ):
                    continue

                section_title = str(
                    evidence.get(
                        "section_title"
                    )
                    or ""
                ).strip()

                excerpt = str(
                    evidence.get("excerpt")
                    or ""
                ).strip()

                if not excerpt:
                    continue

                if section_title:
                    reasoning.append(
                        f"{section_title}: "
                        f"{excerpt}"
                    )
                else:
                    reasoning.append(
                        excerpt
                    )

        return unique_strings(
            reasoning
        )[:4]

    for record in iter_nested_records(
        context
    ):
        gap_id = record.get(
            "gap_id"
        )

        work_order_id = record.get(
            "work_order_id"
        )

        cause_id = record.get(
            "cause_id"
        )

        if cause_id:
            title = str(
                record.get("title")
                or cause_id
            ).strip()

            cause_reasoning = str(
                record.get("reasoning")
                or ""
            ).strip()

            if cause_reasoning:
                reasoning.append(
                    f"{title}: "
                    f"{cause_reasoning}"
                )
            else:
                reasoning.append(title)

        elif gap_id:
            rule_name = str(
                record.get("rule_name")
                or record.get("rule_id")
                or gap_id
            ).strip()

            description = str(
                record.get("description")
                or ""
            ).strip()

            if description:
                reasoning.append(
                    f"{rule_name}: "
                    f"{description}"
                )
            else:
                reasoning.append(
                    rule_name
                )

        elif work_order_id:
            title = str(
                record.get("title")
                or work_order_id
            ).strip()

            status = str(
                record.get("status")
                or ""
            ).strip()

            priority = str(
                record.get("priority")
                or ""
            ).strip()

            details = [
                value
                for value in [
                    (
                        f"priority {priority}"
                        if priority
                        else ""
                    ),
                    (
                        f"status {status}"
                        if status
                        else ""
                    ),
                ]
                if value
            ]

            if details:
                reasoning.append(
                    f"{title} has "
                    + " and ".join(details)
                )
            else:
                reasoning.append(title)

    if not reasoning:
        retrieved_context = response.get(
            "retrieved_context"
        ) or []

        for chunk in retrieved_context[:3]:
            section_title = str(
                chunk.get("section_title")
                or ""
            ).strip()

            excerpt = str(
                chunk.get("chunk_text")
                or ""
            ).strip()

            if section_title:
                reasoning.append(
                    "Evidence was retrieved from "
                    f"{section_title}"
                )
            elif excerpt:
                reasoning.append(
                    excerpt[:240]
                )

    if not reasoning:
        reasoning.append(
            "The answer is based on the "
            "validated evidence listed below"
        )

    return unique_strings(
        reasoning
    )[:4]


def build_ask_rules_applied(
    response: dict[str, Any],
) -> list[str]:
    context = response.get(
        "structured_context"
    ) or {}

    rules: list[str] = []

    for record in iter_nested_records(
        context
    ):
        rule_id = str(
            record.get("rule_id")
            or ""
        ).strip()

        rule_name = str(
            record.get("rule_name")
            or ""
        ).strip()

        if rule_id or rule_name:
            if rule_id and rule_name:
                rules.append(
                    f"{rule_id}: {rule_name}"
                )
            else:
                rules.append(
                    rule_id or rule_name
                )

    if not rules:
        rules = [
            "Supporting evidence must exist",
            "Referenced evidence sections must exist",
            "Evidence excerpts must not be empty",
            "Evidence must match the requested asset",
        ]

    return unique_strings(rules)


def build_ask_conflicting_evidence(
    response: dict[str, Any],
) -> list[str]:
    context = response.get(
        "structured_context"
    ) or {}

    selected_root_cause = context.get(
        "root_cause"
    )

    candidates: list[Any] = []

    if isinstance(
        selected_root_cause,
        dict,
    ):
        counter_evidence = (
            selected_root_cause.get(
                "counter_evidence"
            )
            or []
        )

        candidates.append(
            counter_evidence
        )
    else:
        for record in iter_nested_records(
            context
        ):
            explicit_conflicts = record.get(
                "conflicting_evidence"
            )

            if explicit_conflicts:
                candidates.append(
                    explicit_conflicts
                )

            counter_evidence = record.get(
                "counter_evidence"
            )

            if counter_evidence:
                candidates.append(
                    counter_evidence
                )

    values = unique_strings(
        candidates
    )

    return [
        value
        for value in values
        if not is_missing_evidence_statement(
            value
        )
    ]


def build_ask_missing_evidence(
    response: dict[str, Any],
) -> list[str]:
    context = response.get(
        "structured_context"
    ) or {}

    selected_root_cause = context.get(
        "root_cause"
    )

    if isinstance(
        selected_root_cause,
        dict,
    ):
        records = [
            selected_root_cause
        ]
    else:
        records = list(
            iter_nested_records(
                context
            )
        )

    missing: list[Any] = []

    for record in records:
        explicit_missing = record.get(
            "missing_evidence"
        )

        if explicit_missing:
            missing.append(
                explicit_missing
            )

        counter_evidence = record.get(
            "counter_evidence"
        )

        if isinstance(
            counter_evidence,
            list,
        ):
            for item in counter_evidence:
                if (
                    is_missing_evidence_statement(
                        item
                    )
                ):
                    missing.append(item)

        elif (
            counter_evidence
            and is_missing_evidence_statement(
                counter_evidence
            )
        ):
            missing.append(
                counter_evidence
            )

    return unique_strings(
        missing
    )


def get_ask_recommended_action(
    response: dict[str, Any],
) -> str | None:
    context = response.get(
        "structured_context"
    ) or {}

    for record in iter_nested_records(
        context
    ):
        recommendation_summary = str(
            record.get(
                "recommendation_summary"
            )
            or ""
        ).strip()

        if recommendation_summary:
            return recommendation_summary

        recommendation = str(
            record.get("recommendation")
            or ""
        ).strip()

        if recommendation:
            return recommendation

        recommended_actions = record.get(
            "recommended_actions"
        )

        if (
            isinstance(
                recommended_actions,
                list,
            )
            and recommended_actions
        ):
            first_action = (
                recommended_actions[0]
            )

            if isinstance(
                first_action,
                str,
            ):
                return first_action.strip()

            if isinstance(
                first_action,
                dict,
            ):
                title = str(
                    first_action.get("title")
                    or ""
                ).strip()

                description = str(
                    first_action.get(
                        "description"
                    )
                    or ""
                ).strip()

                return (
                    description
                    or title
                    or None
                )

        if record.get("action_id"):
            description = str(
                record.get("description")
                or ""
            ).strip()

            title = str(
                record.get("title")
                or ""
            ).strip()

            return (
                description
                or title
                or None
            )

    return None


def get_ask_verification_method(
    response: dict[str, Any],
) -> str:
    context = response.get(
        "structured_context"
    ) or {}

    for record in iter_nested_records(
        context
    ):
        verification_metric = str(
            record.get(
                "verification_metric"
            )
            or ""
        ).strip()

        if verification_metric:
            return verification_metric

    answer_type = normalize_text(
        response.get("answer_type")
    )

    if "compliance" in answer_type:
        return (
            "Complete the required remediation, "
            "attach the missing evidence and "
            "regenerate the asset audit package."
        )

    if "rca" in answer_type:
        return (
            "Complete the recommended inspection "
            "and compare post-maintenance vibration "
            "and temperature readings with approved limits."
        )

    if "maintenance" in answer_type:
        return (
            "Complete the work order verification "
            "metric and attach the executed result."
        )

    return (
        "Review the cited evidence and confirm "
        "the conclusion against the applicable "
        "approved procedure or inspection record."
    )


def build_ask_decision_trace(
    response: dict[str, Any],
    asset_id: str | None = None,
) -> dict[str, Any]:
    detected_assets = [
        str(value).upper()
        for value in response.get(
            "detected_assets",
            [],
        )
        if value
    ]

    validation_asset = (
        asset_id.upper()
        if asset_id
        else (
            detected_assets[0]
            if len(detected_assets) == 1
            else None
        )
    )

    return build_decision_trace(
        answer=str(
            response.get("answer")
            or ""
        ),
        confidence=float(
            response.get(
                "confidence_score"
            )
            or 0.0
        ),
        citations=list(
            response.get(
                "citations"
            )
            or []
        ),
        asset_id=validation_asset,
        reasoning_summary=(
            build_ask_reasoning_summary(
                response
            )
        ),
        rules_applied=(
            build_ask_rules_applied(
                response
            )
        ),
        conflicting_evidence=(
            build_ask_conflicting_evidence(
                response
            )
        ),
        recommended_action=(
            get_ask_recommended_action(
                response
            )
        ),
        verification_method=(
            get_ask_verification_method(
                response
            )
        ),
        explicit_missing_evidence=(
            build_ask_missing_evidence(
                response
            )
        ),
    )


def enrich_ask_response(
    response: dict[str, Any],
    asset_id: str | None = None,
) -> dict[str, Any]:
    enriched = dict(response)

    trace = build_ask_decision_trace(
        enriched,
        asset_id,
    )

    enriched.update(
        {
            "answer": trace["answer"],
            "confidence_score": (
                trace["confidence"]
            ),
            "confidence": (
                trace["confidence"]
            ),
            "confidence_explanation": (
                trace[
                    "confidence_explanation"
                ]
            ),
            "citations": (
                trace["evidence_used"]
            ),
            "evidence_used": (
                trace["evidence_used"]
            ),
            "evidence_not_found": (
                trace[
                    "evidence_not_found"
                ]
            ),
            "reasoning_summary": (
                trace[
                    "reasoning_summary"
                ]
            ),
            "rules_applied": (
                trace["rules_applied"]
            ),
            "conflicting_evidence": (
                trace[
                    "conflicting_evidence"
                ]
            ),
            "recommended_action": (
                trace[
                    "recommended_action"
                ]
            ),
            "verification_method": (
                trace[
                    "verification_method"
                ]
            ),
            "supported": trace[
                "supported"
            ],
            "decision_trace": trace,
        }
    )

    return enriched

def is_missing_evidence_statement(
    value: Any,
) -> bool:
    normalized = normalize_text(
        value
    )

    if not normalized:
        return False

    missing_patterns = [
        "not available",
        "currently available",
        "unavailable",
        "not recorded",
        "not yet recorded",
        "have not been recorded",
        "has not been recorded",
        "not completed",
        "not yet completed",
        "could not be found",
        "was not found",
        "missing",
    ]

    if normalized.startswith("no "):
        return True

    return any(
        pattern in normalized
        for pattern in missing_patterns
    )

def build_rca_citations(
    case: dict[str, Any],
    root_cause: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence_ids = {
        str(value)
        for value in root_cause.get(
            "evidence_ids",
            [],
        )
        if value
    }

    citations: list[dict[str, Any]] = []

    for evidence in case.get(
        "evidence",
        [],
    ):
        evidence_id = str(
            evidence.get(
                "evidence_id"
            )
            or ""
        )

        if (
            evidence_ids
            and evidence_id
            not in evidence_ids
        ):
            continue

        document_id = str(
            evidence.get(
                "document_id"
            )
            or evidence_id
        )

        citations.append(
            {
                "citation_id": (
                    evidence_id
                    or document_id
                ),
                "document_id": document_id,
                "document_title": (
                    evidence.get(
                        "document_title"
                    )
                    or document_id
                ),
                "document_type": (
                    evidence.get(
                        "document_type"
                    )
                    or "RCA Evidence"
                ),
                "section_title": (
                    evidence.get(
                        "section_title"
                    )
                    or evidence.get(
                        "document_title"
                    )
                    or "Evidence"
                ),
                "relative_path": (
                    evidence.get(
                        "relative_path"
                    )
                ),
                "evidence_excerpt": (
                    evidence.get(
                        "excerpt"
                    )
                    or ""
                ),
            }
        )

    return citations


def build_rca_reasoning_summary(
    case: dict[str, Any],
    root_cause: dict[str, Any],
) -> list[str]:
    result: list[str] = []

    title = str(
        root_cause.get("title")
        or root_cause.get("cause_id")
        or "Selected root cause"
    ).strip()

    reasoning = str(
        root_cause.get("reasoning")
        or ""
    ).strip()

    if reasoning:
        result.append(
            f"{title}: {reasoning}"
        )
    else:
        result.append(title)

    evidence_ids = {
        str(value)
        for value in root_cause.get(
            "evidence_ids",
            [],
        )
        if value
    }

    for evidence in case.get(
        "evidence",
        [],
    ):
        evidence_id = str(
            evidence.get(
                "evidence_id"
            )
            or ""
        )

        if (
            evidence_ids
            and evidence_id
            not in evidence_ids
        ):
            continue

        section = str(
            evidence.get(
                "section_title"
            )
            or ""
        ).strip()

        excerpt = str(
            evidence.get("excerpt")
            or ""
        ).strip()

        if not excerpt:
            continue

        if section:
            result.append(
                f"{section}: {excerpt}"
            )
        else:
            result.append(excerpt)

    return unique_strings(
        result
    )[:4]


def build_rca_missing_evidence(
    root_cause: dict[str, Any],
) -> list[str]:
    result: list[str] = []

    for value in root_cause.get(
        "counter_evidence",
        [],
    ):
        if is_missing_evidence_statement(
            value
        ):
            result.append(
                str(value)
            )

    return unique_strings(result)


def build_rca_conflicting_evidence(
    root_cause: dict[str, Any],
) -> list[str]:
    result: list[str] = []

    for value in root_cause.get(
        "counter_evidence",
        [],
    ):
        if not is_missing_evidence_statement(
            value
        ):
            result.append(
                str(value)
            )

    return unique_strings(result)


def get_rca_recommended_action(
    case: dict[str, Any],
    root_cause: dict[str, Any],
) -> str | None:
    recommendation = str(
        case.get(
            "recommendation_summary"
        )
        or ""
    ).strip()

    if recommendation:
        return recommendation

    cause_id = str(
        root_cause.get("cause_id")
        or ""
    )

    corrective_actions = case.get(
        "corrective_actions",
        [],
    )

    linked_actions = [
        action
        for action in corrective_actions
        if (
            not cause_id
            or cause_id
            in [
                str(value)
                for value in action.get(
                    "linked_cause_ids",
                    [],
                )
            ]
        )
    ]

    candidates = (
        linked_actions
        or corrective_actions
    )

    if not candidates:
        return None

    action = candidates[0]

    return (
        str(
            action.get("description")
            or action.get("title")
            or ""
        ).strip()
        or None
    )


def get_rca_verification_method(
    case: dict[str, Any],
    root_cause: dict[str, Any],
) -> str:
    cause_id = str(
        root_cause.get("cause_id")
        or ""
    )

    corrective_actions = case.get(
        "corrective_actions",
        [],
    )

    for action in corrective_actions:
        linked_cause_ids = [
            str(value)
            for value in action.get(
                "linked_cause_ids",
                [],
            )
        ]

        if (
            cause_id
            and cause_id
            not in linked_cause_ids
        ):
            continue

        metric = str(
            action.get(
                "verification_metric"
            )
            or ""
        ).strip()

        if metric:
            return metric

    for action in corrective_actions:
        metric = str(
            action.get(
                "verification_metric"
            )
            or ""
        ).strip()

        if metric:
            return metric

    return (
        "Complete the recommended corrective "
        "action and record the post-maintenance "
        "inspection result."
    )


def enrich_rca_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    enriched = dict(case)

    root_causes = sorted(
        case.get(
            "root_causes",
            [],
        ),
        key=lambda item: (
            int(
                item.get(
                    "rank",
                    999,
                )
            ),
            -float(
                item.get(
                    "confidence",
                    0.0,
                )
            ),
        ),
    )

    if not root_causes:
        trace = build_unsupported_decision_trace(
            asset_id=case.get(
                "asset_id"
            ),
            evidence_not_found=[
                "Ranked root-cause evidence"
            ],
            reasoning_summary=[
                "No ranked root cause was available"
            ],
        )

        enriched["decision_trace"] = trace
        enriched["confidence"] = trace[
            "confidence"
        ]
        enriched[
            "confidence_explanation"
        ] = trace[
            "confidence_explanation"
        ]
        enriched["evidence_used"] = trace[
            "evidence_used"
        ]
        enriched[
            "evidence_not_found"
        ] = trace[
            "evidence_not_found"
        ]
        enriched[
            "reasoning_summary"
        ] = trace[
            "reasoning_summary"
        ]
        enriched["rules_applied"] = trace[
            "rules_applied"
        ]
        enriched[
            "conflicting_evidence"
        ] = trace[
            "conflicting_evidence"
        ]
        enriched[
            "recommended_action"
        ] = trace[
            "recommended_action"
        ]
        enriched[
            "verification_method"
        ] = trace[
            "verification_method"
        ]
        enriched["supported"] = False

        return enriched

    root_cause = root_causes[0]

    citations = build_rca_citations(
        case,
        root_cause,
    )

    confidence = float(
        root_cause.get(
            "confidence"
        )
        or case.get(
            "overall_confidence"
        )
        or 0.0
    )

    trace = build_decision_trace(
        answer=(
            str(
                case.get("summary")
                or root_cause.get(
                    "reasoning"
                )
                or ""
            )
        ),
        confidence=confidence,
        citations=citations,
        asset_id=case.get(
            "asset_id"
        ),
        reasoning_summary=(
            build_rca_reasoning_summary(
                case,
                root_cause,
            )
        ),
        rules_applied=[
            "Select the highest-ranked root cause",
            "Require linked supporting evidence",
            "Validate evidence references and excerpts",
            "Separate missing evidence from conflicting evidence",
        ],
        conflicting_evidence=(
            build_rca_conflicting_evidence(
                root_cause
            )
        ),
        recommended_action=(
            get_rca_recommended_action(
                case,
                root_cause,
            )
        ),
        verification_method=(
            get_rca_verification_method(
                case,
                root_cause,
            )
        ),
        explicit_missing_evidence=(
            build_rca_missing_evidence(
                root_cause
            )
        ),
    )

    enriched["selected_root_cause"] = (
        root_cause
    )
    enriched["decision_trace"] = trace
    enriched["confidence"] = trace[
        "confidence"
    ]
    enriched[
        "confidence_explanation"
    ] = trace[
        "confidence_explanation"
    ]
    enriched["evidence_used"] = trace[
        "evidence_used"
    ]
    enriched[
        "evidence_not_found"
    ] = trace[
        "evidence_not_found"
    ]
    enriched[
        "reasoning_summary"
    ] = trace[
        "reasoning_summary"
    ]
    enriched["rules_applied"] = trace[
        "rules_applied"
    ]
    enriched[
        "conflicting_evidence"
    ] = trace[
        "conflicting_evidence"
    ]
    enriched[
        "recommended_action"
    ] = trace[
        "recommended_action"
    ]
    enriched[
        "verification_method"
    ] = trace[
        "verification_method"
    ]
    enriched["supported"] = trace[
        "supported"
    ]

    return enriched

def build_compliance_citations(
    package: dict[str, Any],
) -> list[dict[str, Any]]:
    asset = package.get(
        "asset"
    ) or {}

    asset_id = str(
        asset.get("asset_id")
        or ""
    ).upper()

    asset_token = asset_id.replace(
        "-",
        "",
    )

    linked_document_ids: set[str] = set()
    linked_work_order_ids: set[str] = set()

    for gap in package.get(
        "open_gaps",
        [],
    ):
        linked_document_ids.update(
            str(value)
            for value in gap.get(
                "linked_document_ids",
                [],
            )
            if value
        )

        linked_work_order_ids.update(
            str(value)
            for value in gap.get(
                "linked_work_order_ids",
                [],
            )
            if value
        )

    related_inspection_ids = {
        str(
            inspection.get(
                "document_id"
            )
        )
        for inspection in package.get(
            "related_inspections",
            [],
        )
        if inspection.get(
            "document_id"
        )
    }

    required_procedure_ids = {
        str(
            work_order.get(
                "required_procedure"
            )
        )
        for work_order in package.get(
            "related_work_orders",
            [],
        )
        if work_order.get(
            "required_procedure"
        )
    }

    candidate_document_ids = (
        linked_document_ids
        | related_inspection_ids
        | required_procedure_ids
    )

    for document in package.get(
        "evidence_documents",
        [],
    ):
        document_id = str(
            document.get(
                "document_id"
            )
            or ""
        )

        document_type = normalize_text(
            document.get(
                "document_type"
            )
        )

        if (
            document_id
            and "compliance checklist"
            in document_type
        ):
            candidate_document_ids.add(
                document_id
            )

    excluded_prefixes = {
        "README",
        "PID-",
    }

    other_asset_tokens = {
        "P101",
        "C201",
        "HX301",
    } - {
        asset_token
    }

    documents_by_id = {
        str(
            document.get(
                "document_id"
            )
        ): document
        for document in package.get(
            "evidence_documents",
            [],
        )
        if document.get(
            "document_id"
        )
    }

    citations: list[dict[str, Any]] = []

    for document_id in sorted(
        candidate_document_ids
    ):
        if any(
            document_id.upper().startswith(
                prefix
            )
            for prefix in excluded_prefixes
        ):
            continue

        normalized_document_id = (
            document_id
            .upper()
            .replace(
                "-",
                "",
            )
            .replace(
                "_",
                "",
            )
        )

        belongs_to_other_asset = any(
            token
            in normalized_document_id
            for token in other_asset_tokens
        )

        is_generic_source = (
            normalized_document_id.startswith(
                "SOPGEN"
            )
            or normalized_document_id.startswith(
                "IRGEN"
            )
            or normalized_document_id.startswith(
                "COMP"
            )
        )

        if (
            belongs_to_other_asset
            and not is_generic_source
        ):
            continue

        document = documents_by_id.get(
            document_id
        )

        if not document:
            continue

        title = str(
            document.get("title")
            or document_id
        ).strip()

        excerpt = str(
            document.get("summary")
            or ""
        ).strip()

        if not excerpt:
            continue

        citations.append(
            {
                "citation_id": document_id,
                "document_id": document_id,
                "document_title": title,
                "document_type": (
                    document.get(
                        "document_type"
                    )
                    or "Compliance Evidence"
                ),
                "section_title": title,
                "relative_path": (
                    document.get(
                        "relative_path"
                    )
                ),
                "evidence_excerpt": excerpt,
            }
        )

    work_orders_by_id = {
        str(
            work_order.get(
                "work_order_id"
            )
        ): work_order
        for work_order in package.get(
            "related_work_orders",
            [],
        )
        if work_order.get(
            "work_order_id"
        )
    }

    for work_order_id in sorted(
        linked_work_order_ids
    ):
        work_order = work_orders_by_id.get(
            work_order_id
        )

        if not work_order:
            continue

        title = str(
            work_order.get("title")
            or work_order_id
        ).strip()

        description = str(
            work_order.get(
                "description"
            )
            or ""
        ).strip()

        status = str(
            work_order.get("status")
            or ""
        ).strip()

        due_at = str(
            work_order.get("due_at")
            or ""
        ).strip()

        verification_metric = str(
            work_order.get(
                "verification_metric"
            )
            or ""
        ).strip()

        excerpt_parts = [
            description,
            (
                f"Status: {status}"
                if status
                else ""
            ),
            (
                f"Due at: {due_at}"
                if due_at
                else ""
            ),
            (
                "Verification metric: "
                f"{verification_metric}"
                if verification_metric
                else ""
            ),
        ]

        excerpt = " ".join(
            value
            for value in excerpt_parts
            if value
        )

        if not excerpt:
            continue

        citations.append(
            {
                "citation_id": work_order_id,
                "document_id": work_order_id,
                "document_title": title,
                "document_type": (
                    "Maintenance Work Order"
                ),
                "section_title": title,
                "relative_path": None,
                "evidence_excerpt": excerpt,
            }
        )

    deduplicated: list[
        dict[str, Any]
    ] = []

    seen_ids: set[str] = set()

    for citation in citations:
        citation_id = str(
            citation.get(
                "citation_id"
            )
            or ""
        )

        if (
            not citation_id
            or citation_id in seen_ids
        ):
            continue

        seen_ids.add(citation_id)
        deduplicated.append(citation)

    return deduplicated


def build_compliance_reasoning_summary(
    package: dict[str, Any],
) -> list[str]:
    score = package.get(
        "audit_readiness_score"
    )

    gaps = package.get(
        "open_gaps",
        [],
    )

    reasoning: list[str] = [
        (
            f"Audit readiness score is "
            f"{score}/100"
        )
    ]

    for gap in gaps:
        rule_name = str(
            gap.get("rule_name")
            or gap.get("rule_id")
            or gap.get("gap_id")
            or "Compliance gap"
        ).strip()

        description = str(
            gap.get("description")
            or ""
        ).strip()

        if description:
            reasoning.append(
                f"{rule_name}: {description}"
            )
        else:
            reasoning.append(
                rule_name
            )

    return unique_strings(
        reasoning
    )[:4]


def build_compliance_rules_applied(
    package: dict[str, Any],
) -> list[str]:
    rules: list[str] = []

    for gap in package.get(
        "open_gaps",
        [],
    ):
        rule_id = str(
            gap.get("rule_id")
            or ""
        ).strip()

        rule_name = str(
            gap.get("rule_name")
            or ""
        ).strip()

        if rule_id and rule_name:
            rules.append(
                f"{rule_id}: {rule_name}"
            )
        elif rule_id or rule_name:
            rules.append(
                rule_id or rule_name
            )

    return unique_strings(rules)


def build_compliance_missing_evidence(
    package: dict[str, Any],
) -> list[str]:
    missing: list[Any] = []

    for gap in package.get(
        "open_gaps",
        [],
    ):
        values = gap.get(
            "missing_evidence"
        )

        if values:
            missing.append(values)

    return unique_strings(missing)


def get_compliance_recommended_action(
    package: dict[str, Any],
) -> str | None:
    actions = package.get(
        "recommended_actions",
        [],
    )

    if not actions:
        return None

    first_action = actions[0]

    if isinstance(first_action, str):
        return (
            first_action.strip()
            or None
        )

    if isinstance(first_action, dict):
        return (
            str(
                first_action.get(
                    "description"
                )
                or first_action.get(
                    "title"
                )
                or ""
            ).strip()
            or None
        )

    return None


def get_compliance_confidence(
    package: dict[str, Any],
) -> float:
    gap_confidences = [
        float(
            gap.get(
                "confidence",
                0.0,
            )
        )
        for gap in package.get(
            "open_gaps",
            [],
        )
        if gap.get("confidence") is not None
    ]

    if gap_confidences:
        return sum(
            gap_confidences
        ) / len(
            gap_confidences
        )

    applicable_rules = package.get(
        "applicable_rules",
        [],
    )

    if applicable_rules:
        return 0.95

    return 0.0


def build_compliance_answer(
    package: dict[str, Any],
) -> str:
    asset = package.get(
        "asset"
    ) or {}

    asset_id = str(
        asset.get("asset_id")
        or "Asset"
    )

    score = int(
        package.get(
            "audit_readiness_score",
            0,
        )
    )

    open_gap_count = len(
        package.get(
            "open_gaps",
            [],
        )
    )

    if open_gap_count:
        return (
            f"{asset_id} is not fully audit-ready. "
            f"Its audit readiness score is "
            f"{score}/100 with "
            f"{open_gap_count} open compliance "
            f"{'gap' if open_gap_count == 1 else 'gaps'}."
        )

    return (
        f"{asset_id} is audit-ready with an "
        f"audit readiness score of {score}/100."
    )


def enrich_compliance_package(
    package: dict[str, Any],
) -> dict[str, Any]:
    enriched = dict(package)

    asset = package.get(
        "asset"
    ) or {}

    asset_id = str(
        asset.get("asset_id")
        or ""
    )

    citations = build_compliance_citations(
        package
    )

    trace = build_decision_trace(
        answer=build_compliance_answer(
            package
        ),
        confidence=(
            get_compliance_confidence(
                package
            )
        ),
        citations=citations,
        asset_id=(
            asset_id
            or None
        ),
        reasoning_summary=(
            build_compliance_reasoning_summary(
                package
            )
        ),
        rules_applied=(
            build_compliance_rules_applied(
                package
            )
        ),
        conflicting_evidence=[],
        recommended_action=(
            get_compliance_recommended_action(
                package
            )
        ),
        verification_method=(
            "Complete the linked remediation work, "
            "attach the missing evidence, repeat "
            "required inspections and regenerate "
            "the asset audit package."
        ),
        explicit_missing_evidence=(
            build_compliance_missing_evidence(
                package
            )
        ),
    )

    enriched["answer"] = trace[
        "answer"
    ]
    enriched["confidence"] = trace[
        "confidence"
    ]
    enriched[
        "confidence_explanation"
    ] = trace[
        "confidence_explanation"
    ]
    enriched["evidence_used"] = trace[
        "evidence_used"
    ]
    enriched[
        "evidence_not_found"
    ] = trace[
        "evidence_not_found"
    ]
    enriched[
        "reasoning_summary"
    ] = trace[
        "reasoning_summary"
    ]
    enriched["rules_applied"] = trace[
        "rules_applied"
    ]
    enriched[
        "conflicting_evidence"
    ] = trace[
        "conflicting_evidence"
    ]
    enriched[
        "recommended_action"
    ] = trace[
        "recommended_action"
    ]
    enriched[
        "verification_method"
    ] = trace[
        "verification_method"
    ]
    enriched["supported"] = trace[
        "supported"
    ]
    enriched["decision_trace"] = trace

    return enriched

def build_maintenance_citations(
    work_order: dict[str, Any],
) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []

    work_order_id = str(
        work_order.get(
            "work_order_id"
        )
        or ""
    )

    title = str(
        work_order.get("title")
        or work_order_id
    ).strip()

    description = str(
        work_order.get("description")
        or ""
    ).strip()

    status = str(
        work_order.get("status")
        or ""
    ).strip()

    priority = str(
        work_order.get("priority")
        or ""
    ).strip()

    due_at = str(
        work_order.get("due_at")
        or ""
    ).strip()

    work_order_excerpt = " ".join(
        value
        for value in [
            description,
            (
                f"Priority: {priority}"
                if priority
                else ""
            ),
            (
                f"Status: {status}"
                if status
                else ""
            ),
            (
                f"Due at: {due_at}"
                if due_at
                else ""
            ),
        ]
        if value
    )

    if (
        work_order_id
        and work_order_excerpt
    ):
        citations.append(
            {
                "citation_id": work_order_id,
                "document_id": work_order_id,
                "document_title": title,
                "document_type": (
                    "Maintenance Work Order"
                ),
                "section_title": title,
                "relative_path": None,
                "evidence_excerpt": (
                    work_order_excerpt
                ),
            }
        )

    required_procedure = str(
        work_order.get(
            "required_procedure"
        )
        or ""
    )

    if required_procedure:
        procedure = match_document(
            required_procedure
        )

        if procedure:
            procedure_title = str(
                procedure.get("title")
                or required_procedure
            ).strip()

            procedure_excerpt = str(
                procedure.get("summary")
                or ""
            ).strip()

            if procedure_excerpt:
                citations.append(
                    {
                        "citation_id": (
                            required_procedure
                        ),
                        "document_id": (
                            required_procedure
                        ),
                        "document_title": (
                            procedure_title
                        ),
                        "document_type": (
                            procedure.get(
                                "document_type"
                            )
                            or "SOP / Manual"
                        ),
                        "section_title": (
                            procedure_title
                        ),
                        "relative_path": (
                            procedure.get(
                                "relative_path"
                            )
                        ),
                        "evidence_excerpt": (
                            procedure_excerpt
                        ),
                    }
                )

    asset_id = str(
        work_order.get("asset_id")
        or ""
    )

    for evidence_id in work_order.get(
        "linked_evidence_ids",
        [],
    ):
        evidence, case = find_rca_evidence(
            str(evidence_id),
            asset_id or None,
        )

        if not evidence:
            continue

        document_id = str(
            evidence.get(
                "document_id"
            )
            or evidence_id
        )

        excerpt = str(
            evidence.get("excerpt")
            or ""
        ).strip()

        if not excerpt:
            continue

        citations.append(
            {
                "citation_id": str(
                    evidence.get(
                        "evidence_id"
                    )
                    or evidence_id
                ),
                "document_id": document_id,
                "document_title": (
                    evidence.get(
                        "document_title"
                    )
                    or document_id
                ),
                "document_type": (
                    evidence.get(
                        "document_type"
                    )
                    or "Maintenance Evidence"
                ),
                "section_title": (
                    evidence.get(
                        "section_title"
                    )
                    or evidence.get(
                        "document_title"
                    )
                    or "Evidence"
                ),
                "relative_path": (
                    evidence.get(
                        "relative_path"
                    )
                ),
                "evidence_excerpt": excerpt,
            }
        )

    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for citation in citations:
        citation_id = str(
            citation.get(
                "citation_id"
            )
            or ""
        )

        if (
            not citation_id
            or citation_id in seen_ids
        ):
            continue

        seen_ids.add(citation_id)
        result.append(citation)

    return result


def build_maintenance_reasoning_summary(
    work_order: dict[str, Any],
) -> list[str]:
    reasoning: list[str] = []

    priority = str(
        work_order.get("priority")
        or ""
    ).strip()

    status = str(
        work_order.get("status")
        or ""
    ).strip()

    risk_score = work_order.get(
        "risk_score"
    )

    source_type = str(
        work_order.get("source_type")
        or ""
    ).strip()

    source_id = str(
        work_order.get("source_id")
        or ""
    ).strip()

    linked_rca_case_id = str(
        work_order.get(
            "linked_rca_case_id"
        )
        or ""
    ).strip()

    if priority or status:
        reasoning.append(
            "The work order is "
            + " and ".join(
                value
                for value in [
                    (
                        f"{priority} priority"
                        if priority
                        else ""
                    ),
                    (
                        f"currently {status}"
                        if status
                        else ""
                    ),
                ]
                if value
            )
        )

    if risk_score is not None:
        reasoning.append(
            f"The recorded maintenance risk "
            f"score is {risk_score}"
        )

    if source_type or source_id:
        reasoning.append(
            "The work order was generated from "
            + " ".join(
                value
                for value in [
                    source_type,
                    source_id,
                ]
                if value
            )
        )

    if linked_rca_case_id:
        reasoning.append(
            f"The work order is linked to "
            f"{linked_rca_case_id}"
        )

    return unique_strings(
        reasoning
    )[:4]


def build_maintenance_missing_evidence(
    work_order: dict[str, Any],
) -> list[str]:
    missing: list[str] = []

    status = normalize_text(
        work_order.get("status")
    )

    completion_notes = str(
        work_order.get(
            "completion_notes"
        )
        or ""
    ).strip()

    if (
        status not in {
            "completed",
            "closed",
            "verified",
        }
        and not completion_notes
    ):
        missing.append(
            "Completion notes"
        )

    verification_metric = str(
        work_order.get(
            "verification_metric"
        )
        or ""
    ).strip()

    if (
        verification_metric
        and status not in {
            "completed",
            "closed",
            "verified",
        }
    ):
        missing.append(
            "Executed verification result"
        )

    return unique_strings(
        missing
    )


def build_maintenance_answer(
    work_order: dict[str, Any],
) -> str:
    work_order_id = str(
        work_order.get(
            "work_order_id"
        )
        or "Work order"
    )

    title = str(
        work_order.get("title")
        or "maintenance action"
    )

    priority = str(
        work_order.get("priority")
        or "Unspecified"
    )

    status = str(
        work_order.get("status")
        or "Unknown"
    )

    return (
        f"{work_order_id} requires {title}. "
        f"It is {priority} priority and "
        f"currently {status}."
    )


def enrich_maintenance_work_order(
    work_order: dict[str, Any],
) -> dict[str, Any]:
    enriched = dict(work_order)

    citations = build_maintenance_citations(
        work_order
    )

    confidence = float(
        work_order.get(
            "confidence"
        )
        or 0.0
    )

    verification_metric = str(
        work_order.get(
            "verification_metric"
        )
        or ""
    ).strip()

    trace = build_decision_trace(
        answer=build_maintenance_answer(
            work_order
        ),
        confidence=confidence,
        citations=citations,
        asset_id=work_order.get(
            "asset_id"
        ),
        reasoning_summary=(
            build_maintenance_reasoning_summary(
                work_order
            )
        ),
        rules_applied=[
            "The maintenance action must be linked to an asset",
            "The required procedure must be identifiable",
            "Linked evidence must pass integrity validation",
            "The work order must define a verification method",
        ],
        conflicting_evidence=[],
        recommended_action=(
            str(
                work_order.get(
                    "description"
                )
                or work_order.get(
                    "title"
                )
                or ""
            ).strip()
            or None
        ),
        verification_method=(
            verification_metric
            or (
                "Complete the maintenance action "
                "and record the executed result."
            )
        ),
        explicit_missing_evidence=(
            build_maintenance_missing_evidence(
                work_order
            )
        ),
    )

    enriched["answer"] = trace[
        "answer"
    ]
    enriched["confidence"] = trace[
        "confidence"
    ]
    enriched[
        "confidence_explanation"
    ] = trace[
        "confidence_explanation"
    ]
    enriched["evidence_used"] = trace[
        "evidence_used"
    ]
    enriched[
        "evidence_not_found"
    ] = trace[
        "evidence_not_found"
    ]
    enriched[
        "reasoning_summary"
    ] = trace[
        "reasoning_summary"
    ]
    enriched["rules_applied"] = trace[
        "rules_applied"
    ]
    enriched[
        "conflicting_evidence"
    ] = trace[
        "conflicting_evidence"
    ]
    enriched[
        "recommended_action"
    ] = trace[
        "recommended_action"
    ]
    enriched[
        "verification_method"
    ] = trace[
        "verification_method"
    ]
    enriched["supported"] = trace[
        "supported"
    ]
    enriched["decision_trace"] = trace

    return enriched
