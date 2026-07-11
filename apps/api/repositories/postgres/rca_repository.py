from __future__ import annotations

from sqlalchemy import func, select

from apps.api.db.models.asset import Asset
from apps.api.db.models.operational import (
    Evidence,
    RcaCase,
)
from apps.api.repositories.postgres.base import (
    JsonObject,
    PostgresRepositoryBase,
    clone_payload,
    get_dataset_metadata,
)


class PostgresRcaRepository(
    PostgresRepositoryBase,
):
    """PostgreSQL-backed RCA repository."""

    def get_dataset(self) -> JsonObject:
        with self._session_factory() as session:
            dataset = get_dataset_metadata(
                session,
                "rca_cases",
            )

            cases = session.scalars(
                select(RcaCase)
                .where(
                    RcaCase.deleted_at.is_(None)
                )
                .order_by(
                    RcaCase.source_order,
                    RcaCase.case_code,
                )
            ).all()

            case_payloads = [
                clone_payload(case.payload)
                for case in cases
            ]

            dataset["cases"] = case_payloads
            dataset["case_count"] = len(
                case_payloads
            )

            return dataset

    def list_cases(self) -> list[JsonObject]:
        return self.get_dataset().get(
            "cases",
            [],
        )

    def get_case_by_id(
        self,
        case_id: str,
    ) -> JsonObject | None:
        with self._session_factory() as session:
            case = session.scalar(
                select(RcaCase).where(
                    func.lower(RcaCase.case_code)
                    == case_id.strip().lower(),
                    RcaCase.deleted_at.is_(None),
                )
            )

            if case is None:
                return None

            return clone_payload(case.payload)

    def list_cases_for_asset(
        self,
        asset_id: str,
    ) -> list[JsonObject]:
        with self._session_factory() as session:
            cases = session.scalars(
                select(RcaCase)
                .join(
                    Asset,
                    Asset.id == RcaCase.asset_id,
                )
                .where(
                    func.upper(Asset.asset_code)
                    == asset_id.upper(),
                    Asset.deleted_at.is_(None),
                    RcaCase.deleted_at.is_(None),
                )
                .order_by(
                    RcaCase.detected_at.desc(),
                    RcaCase.source_order,
                )
            ).all()

            return [
                clone_payload(case.payload)
                for case in cases
            ]

    def get_evidence(
        self,
        case_id: str,
        evidence_id: str,
    ) -> JsonObject | None:
        with self._session_factory() as session:
            evidence = session.scalar(
                select(Evidence)
                .join(
                    RcaCase,
                    RcaCase.id
                    == Evidence.rca_case_id,
                )
                .where(
                    func.lower(RcaCase.case_code)
                    == case_id.strip().lower(),
                    func.lower(
                        Evidence.evidence_code
                    )
                    == evidence_id.strip().lower(),
                    RcaCase.deleted_at.is_(None),
                    Evidence.deleted_at.is_(None),
                )
            )

            if evidence is None:
                return None

            return clone_payload(
                evidence.payload
            )