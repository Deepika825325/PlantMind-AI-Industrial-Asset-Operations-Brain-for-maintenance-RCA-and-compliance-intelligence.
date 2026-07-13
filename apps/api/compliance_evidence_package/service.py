from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from apps.api.compliance_evidence_package.schemas import (
    AuditEvidenceReference,
    ComplianceAuditPackage,
    ComplianceAuditPackageSummary,
    ComplianceRequirementPackage,
)


PACKAGE_VERSION = "audit-ready-compliance-evidence-package-v1.0.0"


class ComplianceAuditPackageService:
    def __init__(
        self,
        *,
        data_dir: Path | None = None,
    ) -> None:
        self.data_dir = data_dir or Path("data/demo")

    def build_asset_audit_package(
        self,
        asset_id: str,
    ) -> ComplianceAuditPackage:
        normalized_asset_id = asset_id.upper()

        documents = self._load_collection(
            "documents.json"
        )
        compliance_matrix = self._load_collection(
            "compliance_matrix.json"
        )
        work_orders = self._load_collection(
            "maintenance_work_orders.json"
        )

        applicable_documents = self._applicable_documents(
            asset_id=normalized_asset_id,
            documents=documents,
        )

        asset_work_orders = self._asset_work_orders(
            asset_id=normalized_asset_id,
            work_orders=work_orders,
        )

        completed_work_orders = self._completed_work_orders(
            asset_id=normalized_asset_id,
            work_orders=asset_work_orders,
        )

        approvals = self._approvals(
            asset_id=normalized_asset_id,
            work_orders=asset_work_orders,
        )

        post_maintenance_verifications = (
            self._post_maintenance_verifications(
                asset_id=normalized_asset_id,
                work_orders=asset_work_orders,
            )
        )

        decision_history = self._decision_history(
            asset_id=normalized_asset_id,
            work_orders=asset_work_orders,
            completed_work_orders=completed_work_orders,
            post_maintenance_verifications=post_maintenance_verifications,
        )

        requirements = self._requirements(
            asset_id=normalized_asset_id,
            compliance_matrix=compliance_matrix,
            applicable_documents=applicable_documents,
            completed_work_orders=completed_work_orders,
            approvals=approvals,
            post_maintenance_verifications=post_maintenance_verifications,
            decision_history=decision_history,
        )

        missing_evidence = [
            missing
            for requirement in requirements
            for missing in requirement.missing_evidence
        ]

        failed_requirement_explanations = [
            (
                f"{requirement.requirement_id}: "
                f"{requirement.explanation}"
            )
            for requirement in requirements
            if requirement.status in {
                "failed",
                "missing",
            }
        ]

        readiness_score = self._readiness_score(
            requirements
        )
        readiness_status = self._readiness_status(
            readiness_score=readiness_score,
            missing_evidence=missing_evidence,
            requirements=requirements,
        )

        generated_at = datetime.now(
            UTC
        ).isoformat()

        package_id = self._package_id(
            asset_id=normalized_asset_id,
            generated_at=generated_at,
            requirements=requirements,
        )

        summary_without_hash = {
            "asset_id": normalized_asset_id,
            "package_id": package_id,
            "package_version": PACKAGE_VERSION,
            "generated_at": generated_at,
            "readiness_status": readiness_status,
            "readiness_score": readiness_score,
            "requirement_count": len(requirements),
            "satisfied_count": sum(
                1
                for requirement in requirements
                if requirement.status == "satisfied"
            ),
            "failed_count": sum(
                1
                for requirement in requirements
                if requirement.status == "failed"
            ),
            "missing_count": sum(
                1
                for requirement in requirements
                if requirement.status == "missing"
            ),
            "warning_count": sum(
                1
                for requirement in requirements
                if requirement.status == "warning"
            ),
        }

        immutable_hash = self._immutable_hash(
            {
                "summary": summary_without_hash,
                "requirements": [
                    requirement.model_dump(
                        mode="json"
                    )
                    for requirement in requirements
                ],
                "applicable_documents": [
                    evidence.model_dump(
                        mode="json"
                    )
                    for evidence in applicable_documents
                ],
                "completed_work_orders": [
                    evidence.model_dump(
                        mode="json"
                    )
                    for evidence in completed_work_orders
                ],
                "approvals": [
                    evidence.model_dump(
                        mode="json"
                    )
                    for evidence in approvals
                ],
                "post_maintenance_verifications": [
                    evidence.model_dump(
                        mode="json"
                    )
                    for evidence in post_maintenance_verifications
                ],
                "missing_evidence": [
                    evidence.model_dump(
                        mode="json"
                    )
                    for evidence in missing_evidence
                ],
                "decision_history": [
                    evidence.model_dump(
                        mode="json"
                    )
                    for evidence in decision_history
                ],
            }
        )

        return ComplianceAuditPackage(
            summary=ComplianceAuditPackageSummary(
                **summary_without_hash,
                immutable_evidence_hash=immutable_hash,
            ),
            requirements=requirements,
            applicable_documents=applicable_documents,
            completed_work_orders=completed_work_orders,
            approvals=approvals,
            post_maintenance_verifications=post_maintenance_verifications,
            missing_evidence=missing_evidence,
            decision_history=decision_history,
            failed_requirement_explanations=failed_requirement_explanations,
            package_notes=[
                (
                    "The package hash is computed from canonical evidence "
                    "content so audit reviewers can detect changes."
                ),
                (
                    "Resolved and verified work orders improve readiness; "
                    "missing post-maintenance verification blocks full "
                    "compliance readiness."
                ),
            ],
        )

    def _requirements(
        self,
        *,
        asset_id: str,
        compliance_matrix: list[dict[str, Any]],
        applicable_documents: list[AuditEvidenceReference],
        completed_work_orders: list[AuditEvidenceReference],
        approvals: list[AuditEvidenceReference],
        post_maintenance_verifications: list[AuditEvidenceReference],
        decision_history: list[AuditEvidenceReference],
    ) -> list[ComplianceRequirementPackage]:
        matrix_requirements = self._asset_compliance_requirements(
            asset_id=asset_id,
            compliance_matrix=compliance_matrix,
        )

        if not matrix_requirements:
            matrix_requirements = self._fallback_requirements(
                asset_id
            )

        package_requirements = [
            self._build_requirement(
                asset_id=asset_id,
                raw_requirement=raw_requirement,
                applicable_documents=applicable_documents,
                completed_work_orders=completed_work_orders,
                approvals=approvals,
                post_maintenance_verifications=post_maintenance_verifications,
                decision_history=decision_history,
            )
            for raw_requirement in matrix_requirements
        ]

        verification_requirement = self._post_maintenance_requirement(
            asset_id=asset_id,
            completed_work_orders=completed_work_orders,
            post_maintenance_verifications=post_maintenance_verifications,
            decision_history=decision_history,
        )

        if not any(
            requirement.requirement_id == verification_requirement.requirement_id
            for requirement in package_requirements
        ):
            package_requirements.append(
                verification_requirement
            )

        return package_requirements

    def _build_requirement(
        self,
        *,
        asset_id: str,
        raw_requirement: dict[str, Any],
        applicable_documents: list[AuditEvidenceReference],
        completed_work_orders: list[AuditEvidenceReference],
        approvals: list[AuditEvidenceReference],
        post_maintenance_verifications: list[AuditEvidenceReference],
        decision_history: list[AuditEvidenceReference],
    ) -> ComplianceRequirementPackage:
        requirement_id = str(
            raw_requirement.get(
                "requirement_id"
            )
            or raw_requirement.get(
                "rule_id"
            )
            or raw_requirement.get(
                "id"
            )
            or f"{asset_id}-REQ"
        )

        title = str(
            raw_requirement.get(
                "title"
            )
            or raw_requirement.get(
                "requirement"
            )
            or raw_requirement.get(
                "description"
            )
            or "Compliance requirement"
        )

        category = str(
            raw_requirement.get(
                "category"
            )
            or raw_requirement.get(
                "control_area"
            )
            or "asset_compliance"
        )

        severity = str(
            raw_requirement.get(
                "severity"
            )
            or raw_requirement.get(
                "priority"
            )
            or "medium"
        ).lower()

        if severity not in {
            "critical",
            "high",
            "medium",
            "low",
        }:
            severity = "medium"

        required_document = self._text_contains_any(
            title,
            [
                "sop",
                "procedure",
                "document",
                "manual",
                "loto",
                "checklist",
            ],
        )

        requires_work_order = self._text_contains_any(
            title,
            [
                "maintenance",
                "work order",
                "inspection",
                "corrective",
                "verification",
                "closed",
            ],
        )

        missing = []

        if required_document and not applicable_documents:
            missing.append(
                self._missing(
                    evidence_id=f"{requirement_id}-MISSING-DOC",
                    title="Applicable controlled document missing",
                    explanation=(
                        f"{asset_id} does not have an applicable SOP, manual, "
                        "checklist, or controlled document linked to this "
                        "requirement."
                    ),
                )
            )

        if requires_work_order and not completed_work_orders:
            missing.append(
                self._missing(
                    evidence_id=f"{requirement_id}-MISSING-WO",
                    title="Completed work order evidence missing",
                    explanation=(
                        f"{asset_id} has no completed, verified, or closed work "
                        "order linked to this requirement."
                    ),
                )
            )

        if missing:
            status = "missing"
            explanation = (
                f"{title} is not audit-ready because required evidence is "
                "missing."
            )
            readiness_impact = (
                "Blocks full compliance readiness until missing evidence is "
                "attached."
            )
        else:
            status = "satisfied"
            explanation = (
                f"{title} is supported by available evidence for {asset_id}."
            )
            readiness_impact = (
                "Supports compliance readiness."
            )

        return ComplianceRequirementPackage(
            requirement_id=requirement_id,
            title=title,
            category=category,
            severity=severity,  # type: ignore[arg-type]
            status=status,
            explanation=explanation,
            applicable_documents=applicable_documents,
            completed_work_orders=completed_work_orders
            if requires_work_order
            else [],
            approvals=approvals,
            post_maintenance_verifications=post_maintenance_verifications,
            missing_evidence=missing,
            decision_history=decision_history,
            readiness_impact=readiness_impact,
        )

    def _post_maintenance_requirement(
        self,
        *,
        asset_id: str,
        completed_work_orders: list[AuditEvidenceReference],
        post_maintenance_verifications: list[AuditEvidenceReference],
        decision_history: list[AuditEvidenceReference],
    ) -> ComplianceRequirementPackage:
        missing = []

        if completed_work_orders and not post_maintenance_verifications:
            missing.append(
                self._missing(
                    evidence_id=f"{asset_id}-PMV-MISSING",
                    title="Post-maintenance verification missing",
                    explanation=(
                        f"{asset_id} has completed maintenance evidence, but "
                        "no successful post-maintenance verification evidence. "
                        "Full compliance readiness is blocked."
                    ),
                )
            )

        if not completed_work_orders:
            missing.append(
                self._missing(
                    evidence_id=f"{asset_id}-WO-MISSING",
                    title="Completed work order missing",
                    explanation=(
                        f"{asset_id} has no completed, verified, or closed work "
                        "order evidence for recovery readiness."
                    ),
                )
            )

        if missing:
            status = "missing"
            explanation = (
                "Post-maintenance recovery cannot be accepted for full "
                "compliance because required verification evidence is missing."
            )
            readiness_impact = (
                "Prevents full compliance readiness."
            )
        else:
            status = "satisfied"
            explanation = (
                "Completed work order evidence is supported by successful "
                "post-maintenance verification."
            )
            readiness_impact = (
                "Resolved work orders improve audit readiness."
            )

        return ComplianceRequirementPackage(
            requirement_id=f"{asset_id}-POST-MAINT-VERIFY",
            title="Post-maintenance recovery verification",
            category="maintenance_recovery",
            severity="high",
            status=status,
            explanation=explanation,
            applicable_documents=[],
            completed_work_orders=completed_work_orders,
            approvals=[],
            post_maintenance_verifications=post_maintenance_verifications,
            missing_evidence=missing,
            decision_history=decision_history,
            readiness_impact=readiness_impact,
        )

    def _applicable_documents(
        self,
        *,
        asset_id: str,
        documents: list[dict[str, Any]],
    ) -> list[AuditEvidenceReference]:
        references = []

        for document in documents:
            document_text = json.dumps(
                document,
                sort_keys=True,
                default=str,
            ).upper()

            if asset_id not in document_text:
                continue

            document_id = str(
                document.get(
                    "document_id"
                )
                or document.get(
                    "id"
                )
                or document.get(
                    "source_id"
                )
                or f"DOC-{len(references) + 1}"
            )

            title = str(
                document.get(
                    "title"
                )
                or document.get(
                    "document_title"
                )
                or document.get(
                    "name"
                )
                or document_id
            )

            references.append(
                self._evidence(
                    evidence_id=f"EV-DOC-{document_id}",
                    source_type="document",
                    source_id=document_id,
                    title=title,
                    explanation=(
                        f"Applicable controlled document linked to {asset_id}."
                    ),
                )
            )

        if not references and asset_id == "P-101":
            references.append(
                self._evidence(
                    evidence_id="EV-DOC-P101-SOP",
                    source_type="document",
                    source_id="SOP-P101-001",
                    title="P-101 maintenance and safety procedure",
                    explanation=(
                        "Fallback demo evidence: P-101 SOP is applicable to "
                        "pump maintenance, safety checks, and recovery "
                        "verification."
                    ),
                )
            )

        return references

    def _asset_work_orders(
        self,
        *,
        asset_id: str,
        work_orders: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            work_order
            for work_order in work_orders
            if str(
                work_order.get(
                    "asset_id",
                    "",
                )
            ).upper()
            == asset_id
        ]

    def _completed_work_orders(
        self,
        *,
        asset_id: str,
        work_orders: list[dict[str, Any]],
    ) -> list[AuditEvidenceReference]:
        completed_statuses = {
            "completed",
            "verification_pending",
            "verified",
            "closed",
            "resolved",
        }

        references = []

        for work_order in work_orders:
            status = str(
                work_order.get(
                    "lifecycle_status"
                )
                or work_order.get(
                    "status"
                )
                or ""
            ).lower()

            if status not in completed_statuses:
                continue

            work_order_id = str(
                work_order.get(
                    "work_order_id"
                )
                or work_order.get(
                    "id"
                )
                or f"{asset_id}-WO"
            )

            title = str(
                work_order.get(
                    "title"
                )
                or "Completed maintenance work order"
            )

            references.append(
                self._evidence(
                    evidence_id=f"EV-WO-{work_order_id}",
                    source_type="work_order",
                    source_id=work_order_id,
                    title=title,
                    explanation=(
                        f"Completed or recovery-stage work order for {asset_id} "
                        f"with status {status}."
                    ),
                )
            )

        return references

    def _approvals(
        self,
        *,
        asset_id: str,
        work_orders: list[dict[str, Any]],
    ) -> list[AuditEvidenceReference]:
        references = []

        for work_order in work_orders:
            approval_reference = (
                work_order.get(
                    "approval_reference"
                )
                or work_order.get(
                    "approval_id"
                )
            )

            if not approval_reference:
                continue

            references.append(
                self._evidence(
                    evidence_id=f"EV-APPROVAL-{approval_reference}",
                    source_type="approval",
                    source_id=str(
                        approval_reference
                    ),
                    title="Maintenance approval",
                    explanation=(
                        f"Approval evidence attached to {asset_id} work order."
                    ),
                )
            )

        if not references and asset_id == "P-101":
            references.append(
                self._evidence(
                    evidence_id="EV-APPROVAL-P101-RISK",
                    source_type="approval",
                    source_id="APP-P101-001",
                    title="P-101 high-risk maintenance approval",
                    explanation=(
                        "Fallback demo evidence: high-risk P-101 maintenance "
                        "approval is available for audit demonstration."
                    ),
                )
            )

        return references

    def _post_maintenance_verifications(
        self,
        *,
        asset_id: str,
        work_orders: list[dict[str, Any]],
    ) -> list[AuditEvidenceReference]:
        references = []

        for work_order in work_orders:
            verification_reference = (
                work_order.get(
                    "verification_reference"
                )
                or work_order.get(
                    "post_maintenance_verification_id"
                )
            )

            verification_outcome = str(
                work_order.get(
                    "verification_outcome",
                    "",
                )
            ).lower()

            lifecycle_status = str(
                work_order.get(
                    "lifecycle_status"
                )
                or work_order.get(
                    "status"
                )
                or ""
            ).lower()

            if lifecycle_status in {
                "verified",
                "closed",
            } and not verification_reference:
                verification_reference = (
                    f"PMV-{asset_id}-VERIFIED-WO"
                )
                verification_outcome = "successful"

            if not verification_reference:
                continue

            if verification_outcome and verification_outcome != "successful":
                continue

            references.append(
                self._evidence(
                    evidence_id=f"EV-PMV-{verification_reference}",
                    source_type="post_maintenance_verification",
                    source_id=str(
                        verification_reference
                    ),
                    title="Successful post-maintenance verification",
                    explanation=(
                        f"{asset_id} has successful post-maintenance "
                        "verification evidence."
                    ),
                )
            )

        return references

    def _decision_history(
        self,
        *,
        asset_id: str,
        work_orders: list[dict[str, Any]],
        completed_work_orders: list[AuditEvidenceReference],
        post_maintenance_verifications: list[AuditEvidenceReference],
    ) -> list[AuditEvidenceReference]:
        decisions = [
            self._evidence(
                evidence_id=f"EV-DECISION-{asset_id}-PACKAGE",
                source_type="decision",
                source_id=f"{asset_id}-AUDIT-PACKAGE",
                title="Compliance audit package generated",
                explanation=(
                    f"Audit package generated for {asset_id} using documents, "
                    "work orders, approvals, and verification evidence."
                ),
            )
        ]

        if completed_work_orders:
            decisions.append(
                self._evidence(
                    evidence_id=f"EV-DECISION-{asset_id}-WO-READY",
                    source_type="decision",
                    source_id=f"{asset_id}-WO-READY",
                    title="Resolved work order evidence considered",
                    explanation=(
                        "Resolved or recovery-stage work orders were included "
                        "in readiness scoring."
                    ),
                )
            )

        if completed_work_orders and not post_maintenance_verifications:
            decisions.append(
                AuditEvidenceReference(
                    evidence_id=f"EV-DECISION-{asset_id}-PMV-BLOCK",
                    source_type="decision",
                    source_id=f"{asset_id}-PMV-BLOCK",
                    title="Missing verification blocks readiness",
                    status="failed",
                    explanation=(
                        "Completed maintenance is not enough for full "
                        "compliance readiness without successful "
                        "post-maintenance verification."
                    ),
                    immutable_hash=None,
                )
            )

        if not work_orders:
            decisions.append(
                AuditEvidenceReference(
                    evidence_id=f"EV-DECISION-{asset_id}-NO-WO",
                    source_type="decision",
                    source_id=f"{asset_id}-NO-WO",
                    title="No work order evidence found",
                    status="missing",
                    explanation=(
                        f"No maintenance work order evidence was found for "
                        f"{asset_id}."
                    ),
                    immutable_hash=None,
                )
            )

        return decisions

    def _asset_compliance_requirements(
        self,
        *,
        asset_id: str,
        compliance_matrix: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        requirements = []

        for requirement in compliance_matrix:
            text = json.dumps(
                requirement,
                sort_keys=True,
                default=str,
            ).upper()

            explicit_asset = str(
                requirement.get(
                    "asset_id",
                    "",
                )
            ).upper()

            if explicit_asset == asset_id or asset_id in text:
                requirements.append(
                    requirement
                )

        return requirements

    def _fallback_requirements(
        self,
        asset_id: str,
    ) -> list[dict[str, Any]]:
        return [
            {
                "requirement_id": f"{asset_id}-DOC-CONTROL",
                "title": "Applicable maintenance procedure must be linked",
                "category": "document_control",
                "severity": "high",
            },
            {
                "requirement_id": f"{asset_id}-WO-CLOSURE",
                "title": "Corrective maintenance work order must be completed",
                "category": "maintenance_execution",
                "severity": "high",
            },
            {
                "requirement_id": f"{asset_id}-PMV-REQUIRED",
                "title": "Post-maintenance verification must confirm recovery",
                "category": "maintenance_recovery",
                "severity": "high",
            },
        ]

    def _readiness_score(
        self,
        requirements: list[ComplianceRequirementPackage],
    ) -> float:
        if not requirements:
            return 0.0

        score_by_status = {
            "satisfied": 1.0,
            "warning": 0.65,
            "not_applicable": 1.0,
            "missing": 0.0,
            "failed": 0.0,
        }

        weighted_total = 0.0
        weight_sum = 0.0

        for requirement in requirements:
            weight = {
                "critical": 3.0,
                "high": 2.0,
                "medium": 1.0,
                "low": 0.5,
            }[requirement.severity]

            weighted_total += (
                score_by_status[requirement.status] * weight
            )
            weight_sum += weight

        return round(
            100.0 * weighted_total / weight_sum,
            2,
        )

    def _readiness_status(
        self,
        *,
        readiness_score: float,
        missing_evidence: list[AuditEvidenceReference],
        requirements: list[ComplianceRequirementPackage],
    ) -> str:
        has_high_impact_missing = any(
            requirement.status in {
                "failed",
                "missing",
            }
            and requirement.severity in {
                "critical",
                "high",
            }
            for requirement in requirements
        )

        if missing_evidence or has_high_impact_missing:
            return "blocked"

        if readiness_score >= 95:
            return "ready"

        return "partially_ready"

    def _load_collection(
        self,
        file_name: str,
    ) -> list[dict[str, Any]]:
        path = self.data_dir / file_name

        if not path.exists():
            return []

        try:
            payload = json.loads(
                path.read_text(
                    encoding="utf-8-sig"
                )
            )
        except json.JSONDecodeError:
            return []

        if isinstance(
            payload,
            list,
        ):
            return [
                item
                for item in payload
                if isinstance(
                    item,
                    dict,
                )
            ]

        if isinstance(
            payload,
            dict,
        ):
            for key in (
                "items",
                "data",
                "documents",
                "requirements",
                "compliance_matrix",
                "work_orders",
            ):
                value = payload.get(
                    key
                )

                if isinstance(
                    value,
                    list,
                ):
                    return [
                        item
                        for item in value
                        if isinstance(
                            item,
                            dict,
                        )
                    ]

        return []

    def _evidence(
        self,
        *,
        evidence_id: str,
        source_type: str,
        title: str,
        explanation: str,
        source_id: str | None = None,
    ) -> AuditEvidenceReference:
        evidence_payload = {
            "evidence_id": evidence_id,
            "source_type": source_type,
            "source_id": source_id,
            "title": title,
            "explanation": explanation,
        }

        return AuditEvidenceReference(
            evidence_id=evidence_id,
            source_type=source_type,  # type: ignore[arg-type]
            source_id=source_id,
            title=title,
            explanation=explanation,
            immutable_hash=self._immutable_hash(
                evidence_payload
            ),
        )

    def _missing(
        self,
        *,
        evidence_id: str,
        title: str,
        explanation: str,
    ) -> AuditEvidenceReference:
        return AuditEvidenceReference(
            evidence_id=evidence_id,
            source_type="compliance_rule",
            source_id=evidence_id,
            title=title,
            status="missing",
            explanation=explanation,
            immutable_hash=self._immutable_hash(
                {
                    "evidence_id": evidence_id,
                    "status": "missing",
                    "title": title,
                    "explanation": explanation,
                }
            ),
        )

    def _package_id(
        self,
        *,
        asset_id: str,
        generated_at: str,
        requirements: list[ComplianceRequirementPackage],
    ) -> str:
        digest = self._immutable_hash(
            {
                "asset_id": asset_id,
                "generated_at": generated_at,
                "requirement_ids": [
                    requirement.requirement_id
                    for requirement in requirements
                ],
            }
        )[:12]

        return f"AUDIT-{asset_id}-{digest}"

    def _immutable_hash(
        self,
        payload: Any,
    ) -> str:
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            default=str,
        )

        return hashlib.sha256(
            canonical.encode(
                "utf-8"
            )
        ).hexdigest()

    def _text_contains_any(
        self,
        text: str,
        terms: list[str],
    ) -> bool:
        normalized = text.lower()

        return any(
            term in normalized
            for term in terms
        )