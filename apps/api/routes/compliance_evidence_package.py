from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.auth.dependencies import require_permission
from apps.api.compliance_evidence_package.schemas import (
    ComplianceAuditPackage,
)
from apps.api.compliance_evidence_package.service import (
    ComplianceAuditPackageService,
)


router = APIRouter(
    prefix="/compliance",
    tags=["compliance-evidence-package"],
)

compliance_audit_package_service = ComplianceAuditPackageService()


@router.get(
    "/audit-packages/assets/{asset_id}",
    response_model=ComplianceAuditPackage,
)
def get_asset_compliance_audit_package(
    asset_id: str,
    user=Depends(require_permission("document.read")),
) -> ComplianceAuditPackage:
    return compliance_audit_package_service.build_asset_audit_package(
        asset_id
    )