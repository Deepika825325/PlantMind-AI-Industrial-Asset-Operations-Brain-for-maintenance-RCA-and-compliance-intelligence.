from __future__ import annotations

from sqlalchemy import select

from apps.api.db.models.compliance import (
    ComplianceAssetSummary,
    ComplianceFinding,
    ComplianceRule,
)
from apps.api.repositories.postgres.base import (
    JsonObject,
    PostgresRepositoryBase,
    clone_payload,
    get_dataset_metadata,
)


class PostgresComplianceRepository(
    PostgresRepositoryBase,
):
    """PostgreSQL-backed compliance repository."""

    def get_rules(self) -> JsonObject:
        with self._session_factory() as session:
            dataset = get_dataset_metadata(
                session,
                "compliance_rules",
            )

            rules = session.scalars(
                select(ComplianceRule)
                .where(
                    ComplianceRule
                    .deleted_at.is_(None)
                )
                .order_by(
                    ComplianceRule.source_order,
                    ComplianceRule.rule_code,
                )
            ).all()

            dataset["rules"] = [
                clone_payload(rule.payload)
                for rule in rules
            ]

            return dataset

    def get_matrix(self) -> JsonObject:
        with self._session_factory() as session:
            dataset = get_dataset_metadata(
                session,
                "compliance_matrix",
            )

            summaries = session.scalars(
                select(ComplianceAssetSummary)
                .where(
                    ComplianceAssetSummary
                    .deleted_at.is_(None)
                )
                .order_by(
                    ComplianceAssetSummary
                    .source_order,
                )
            ).all()

            findings = session.scalars(
                select(ComplianceFinding)
                .where(
                    ComplianceFinding
                    .deleted_at.is_(None)
                )
                .order_by(
                    ComplianceFinding.source_order,
                    ComplianceFinding.finding_code,
                )
            ).all()

            dataset[
                "asset_compliance_summary"
            ] = [
                clone_payload(summary.payload)
                for summary in summaries
            ]

            dataset["gaps"] = [
                clone_payload(finding.payload)
                for finding in findings
            ]

            return dataset