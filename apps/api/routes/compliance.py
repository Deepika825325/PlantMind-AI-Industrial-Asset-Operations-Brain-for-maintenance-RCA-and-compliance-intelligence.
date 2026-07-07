from fastapi import APIRouter, HTTPException, Query

from apps.api.services.compliance_service import (
    get_asset_audit_package,
    get_compliance_gaps,
    get_compliance_overview,
    get_compliance_rules,
)
from apps.api.services.evidence_integrity_service import enrich_compliance_package


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"],
)


@router.get("")
def get_compliance():
    return get_compliance_overview()


@router.get("/overview")
def get_compliance_intelligence_overview():
    return get_compliance_overview()


@router.get("/rules")
def list_compliance_rules():
    return get_compliance_rules()


@router.get("/gaps")
def list_compliance_gaps(
    asset_id: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    rule_id: str | None = Query(default=None),
    evidence_availability: str | None = Query(
        default=None
    ),
):
    return get_compliance_gaps(
        asset_id=asset_id,
        severity=severity,
        status=status,
        rule_id=rule_id,
        evidence_availability=evidence_availability,
    )


@router.get("/assets/{asset_id}/audit-package")
def get_asset_compliance_audit_package(
    asset_id: str,
):
    package = get_asset_audit_package(
        asset_id
    )

    if not package:
        raise HTTPException(
            status_code=404,
            detail=(
                "Compliance audit package not found "
                f"for asset: {asset_id.upper()}"
            ),
        )

    return enrich_compliance_package(
        package
    )


@router.get("/assets/{asset_id}")
def get_asset_compliance(asset_id: str):
    package = get_asset_audit_package(
        asset_id
    )

    if not package:
        raise HTTPException(
            status_code=404,
            detail=(
                "Compliance information not found "
                f"for asset: {asset_id.upper()}"
            ),
        )

    enriched = enrich_compliance_package(
        package
    )

    return {
        "asset": enriched["asset"],
        "audit_readiness_score": enriched[
            "audit_readiness_score"
        ],
        "scoring_breakdown": enriched[
            "scoring_breakdown"
        ],
        "total_rules": len(
            enriched["applicable_rules"]
        ),
        "passed_rules": len(
            enriched["passed_rules"]
        ),
        "failed_rules": len(
            enriched["failed_rules"]
        ),
        "open_gaps": enriched[
            "open_gaps"
        ],
        "recommended_actions": enriched[
            "recommended_actions"
        ],
        "generated_at": enriched[
            "generated_at"
        ],
        "answer": enriched["answer"],
        "confidence": enriched[
            "confidence"
        ],
        "confidence_explanation": enriched[
            "confidence_explanation"
        ],
        "evidence_used": enriched[
            "evidence_used"
        ],
        "evidence_not_found": enriched[
            "evidence_not_found"
        ],
        "reasoning_summary": enriched[
            "reasoning_summary"
        ],
        "rules_applied": enriched[
            "rules_applied"
        ],
        "conflicting_evidence": enriched[
            "conflicting_evidence"
        ],
        "recommended_action": enriched[
            "recommended_action"
        ],
        "verification_method": enriched[
            "verification_method"
        ],
        "supported": enriched[
            "supported"
        ],
        "decision_trace": enriched[
            "decision_trace"
        ],
    }
