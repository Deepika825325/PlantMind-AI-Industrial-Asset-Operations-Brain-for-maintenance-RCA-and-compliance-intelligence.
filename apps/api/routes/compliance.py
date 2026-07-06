from fastapi import APIRouter, HTTPException, Query

from apps.api.services.compliance_service import (
    get_asset_audit_package,
    get_compliance_gaps,
    get_compliance_overview,
    get_compliance_rules,
)


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
    package = get_asset_audit_package(asset_id)

    if not package:
        raise HTTPException(
            status_code=404,
            detail=(
                "Compliance audit package not found "
                f"for asset: {asset_id.upper()}"
            ),
        )

    return package


@router.get("/assets/{asset_id}")
def get_asset_compliance(asset_id: str):
    package = get_asset_audit_package(asset_id)

    if not package:
        raise HTTPException(
            status_code=404,
            detail=(
                "Compliance information not found "
                f"for asset: {asset_id.upper()}"
            ),
        )

    return {
        "asset": package["asset"],
        "audit_readiness_score": package[
            "audit_readiness_score"
        ],
        "scoring_breakdown": package[
            "scoring_breakdown"
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
        "open_gaps": package["open_gaps"],
        "recommended_actions": package[
            "recommended_actions"
        ],
        "generated_at": package["generated_at"],
    }