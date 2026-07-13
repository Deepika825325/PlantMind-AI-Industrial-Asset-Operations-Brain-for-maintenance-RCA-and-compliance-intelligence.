from __future__ import annotations

import inspect
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from apps.api.compliance_evidence_package.service import (
    ComplianceAuditPackageService,
)
from apps.api.main import app
from apps.api.routes import compliance_evidence_package as audit_package_route


client = TestClient(app)


def _write_json(
    path: Path,
    payload: Any,
) -> None:
    path.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_audit_ready_dataset(
    data_dir: Path,
) -> None:
    _write_json(
        data_dir / "documents.json",
        {
            "documents": [
                {
                    "document_id": "SOP-P101-001",
                    "asset_id": "P-101",
                    "title": "P-101 maintenance procedure and LOTO checklist",
                }
            ]
        },
    )

    _write_json(
        data_dir / "compliance_matrix.json",
        {
            "compliance_matrix": [
                {
                    "requirement_id": "P101-DOC-CONTROL",
                    "asset_id": "P-101",
                    "title": "Applicable maintenance procedure must be linked",
                    "category": "document_control",
                    "severity": "high",
                },
                {
                    "requirement_id": "P101-WO-CLOSURE",
                    "asset_id": "P-101",
                    "title": "Corrective maintenance work order must be completed",
                    "category": "maintenance_execution",
                    "severity": "high",
                },
                {
                    "requirement_id": "P101-PMV-REQUIRED",
                    "asset_id": "P-101",
                    "title": "Post-maintenance verification must confirm recovery",
                    "category": "maintenance_recovery",
                    "severity": "high",
                },
            ]
        },
    )

    _write_json(
        data_dir / "maintenance_work_orders.json",
        {
            "work_orders": [
                {
                    "work_order_id": "WO-P101-VERIFIED-001",
                    "asset_id": "P-101",
                    "title": "Conduct post-maintenance vibration test",
                    "priority": "high",
                    "lifecycle_status": "verified",
                    "risk_score": 81.0,
                    "approval_reference": "APP-P101-001",
                    "verification_reference": "PMV-P101-SUCCESS-001",
                    "verification_outcome": "successful",
                }
            ]
        },
    )


def _write_missing_verification_dataset(
    data_dir: Path,
) -> None:
    _write_json(
        data_dir / "documents.json",
        {
            "documents": [
                {
                    "document_id": "SOP-P101-001",
                    "asset_id": "P-101",
                    "title": "P-101 maintenance procedure and LOTO checklist",
                }
            ]
        },
    )

    _write_json(
        data_dir / "compliance_matrix.json",
        {
            "compliance_matrix": [
                {
                    "requirement_id": "P101-DOC-CONTROL",
                    "asset_id": "P-101",
                    "title": "Applicable maintenance procedure must be linked",
                    "category": "document_control",
                    "severity": "high",
                },
                {
                    "requirement_id": "P101-WO-CLOSURE",
                    "asset_id": "P-101",
                    "title": "Corrective maintenance work order must be completed",
                    "category": "maintenance_execution",
                    "severity": "high",
                },
                {
                    "requirement_id": "P101-PMV-REQUIRED",
                    "asset_id": "P-101",
                    "title": "Post-maintenance verification must confirm recovery",
                    "category": "maintenance_recovery",
                    "severity": "high",
                },
            ]
        },
    )

    _write_json(
        data_dir / "maintenance_work_orders.json",
        {
            "work_orders": [
                {
                    "work_order_id": "WO-P101-COMPLETE-001",
                    "asset_id": "P-101",
                    "title": "Conduct post-maintenance vibration test",
                    "priority": "high",
                    "lifecycle_status": "completed",
                    "risk_score": 81.0,
                    "approval_reference": "APP-P101-001",
                }
            ]
        },
    )


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        audit_package_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_user(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "compliance-audit-package-tester",
        "email": "compliance-audit-package@plantmind.local",
        "role": "maintenance_engineer",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_audit_package_service(
    data_dir: Path,
) -> Iterator[ComplianceAuditPackageService]:
    original_service = audit_package_route.compliance_audit_package_service
    service = ComplianceAuditPackageService(
        data_dir=data_dir
    )

    audit_package_route.compliance_audit_package_service = service

    try:
        yield service
    finally:
        audit_package_route.compliance_audit_package_service = original_service


def test_p101_audit_package_explains_every_failed_requirement(
    tmp_path: Path,
) -> None:
    _write_missing_verification_dataset(
        tmp_path
    )

    service = ComplianceAuditPackageService(
        data_dir=tmp_path
    )

    package = service.build_asset_audit_package(
        "P-101"
    )

    failed_requirements = [
        requirement
        for requirement in package.requirements
        if requirement.status in {
            "failed",
            "missing",
        }
    ]

    assert failed_requirements
    assert package.summary.readiness_status == "blocked"
    assert package.summary.missing_count == len(
        failed_requirements
    )
    assert len(
        package.failed_requirement_explanations
    ) == len(
        failed_requirements
    )

    for requirement in failed_requirements:
        matching_explanations = [
            explanation
            for explanation in package.failed_requirement_explanations
            if requirement.requirement_id in explanation
        ]

        assert matching_explanations
        assert requirement.explanation in matching_explanations[0]


def test_missing_post_maintenance_verification_prevents_full_compliance(
    tmp_path: Path,
) -> None:
    _write_missing_verification_dataset(
        tmp_path
    )

    service = ComplianceAuditPackageService(
        data_dir=tmp_path
    )

    package = service.build_asset_audit_package(
        "P-101"
    )

    missing_titles = {
        evidence.title
        for evidence in package.missing_evidence
    }

    assert package.summary.readiness_status == "blocked"
    assert package.summary.readiness_score < 100.0
    assert "Post-maintenance verification missing" in missing_titles
    assert not package.post_maintenance_verifications

    assert any(
        "verification"
        in explanation.lower()
        for explanation in package.failed_requirement_explanations
    )


def test_resolved_verified_work_orders_update_readiness(
    tmp_path: Path,
) -> None:
    _write_missing_verification_dataset(
        tmp_path
    )

    blocked_service = ComplianceAuditPackageService(
        data_dir=tmp_path
    )

    blocked_package = blocked_service.build_asset_audit_package(
        "P-101"
    )

    _write_audit_ready_dataset(
        tmp_path
    )

    ready_service = ComplianceAuditPackageService(
        data_dir=tmp_path
    )

    ready_package = ready_service.build_asset_audit_package(
        "P-101"
    )

    assert blocked_package.summary.readiness_status == "blocked"
    assert ready_package.summary.readiness_score > blocked_package.summary.readiness_score
    assert ready_package.summary.readiness_status == "ready"
    assert ready_package.summary.missing_count == 0
    assert ready_package.post_maintenance_verifications
    assert ready_package.completed_work_orders
    assert ready_package.approvals


def test_audit_package_contains_immutable_evidence_and_decision_history(
    tmp_path: Path,
) -> None:
    _write_audit_ready_dataset(
        tmp_path
    )

    service = ComplianceAuditPackageService(
        data_dir=tmp_path
    )

    package = service.build_asset_audit_package(
        "P-101"
    )

    assert package.summary.package_id.startswith(
        "AUDIT-P-101-"
    )
    assert len(
        package.summary.immutable_evidence_hash
    ) == 64
    assert package.decision_history
    assert package.applicable_documents
    assert package.completed_work_orders
    assert package.post_maintenance_verifications

    for evidence in (
        package.applicable_documents
        + package.completed_work_orders
        + package.approvals
        + package.post_maintenance_verifications
    ):
        assert evidence.immutable_hash
        assert len(
            evidence.immutable_hash
        ) == 64


def test_compliance_audit_package_endpoint_returns_p101_package(
    tmp_path: Path,
) -> None:
    _write_missing_verification_dataset(
        tmp_path
    )

    with isolated_audit_package_service(
        tmp_path
    ):
        with authorized_user(
            "get_asset_compliance_audit_package"
        ):
            response = client.get(
                "/compliance/audit-packages/assets/P-101"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["summary"]["asset_id"] == "P-101"
    assert payload["summary"]["readiness_status"] == "blocked"
    assert payload["missing_evidence"]
    assert payload["failed_requirement_explanations"]
    assert any(
        evidence["title"] == "Post-maintenance verification missing"
        for evidence in payload["missing_evidence"]
    )


def test_compliance_audit_package_endpoint_requires_authentication() -> None:
    response = client.get(
        "/compliance/audit-packages/assets/P-101"
    )

    assert response.status_code == 401