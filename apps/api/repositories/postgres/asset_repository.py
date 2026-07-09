from __future__ import annotations

from sqlalchemy import func, select

from apps.api.db.models.asset import Asset
from apps.api.db.models.dataset import (
    AssetHealthSnapshot,
)
from apps.api.repositories.postgres.base import (
    JsonObject,
    PostgresRepositoryBase,
    clone_payload,
)


class PostgresAssetRepository(
    PostgresRepositoryBase,
):
    """PostgreSQL-backed asset repository."""

    def list_assets(self) -> list[JsonObject]:
        with self._session_factory() as session:
            assets = session.scalars(
                select(Asset)
                .where(
                    Asset.deleted_at.is_(None)
                )
                .order_by(
                    Asset.source_order,
                    Asset.asset_code,
                )
            ).all()

            return [
                clone_payload(asset.payload)
                for asset in assets
            ]

    def get_asset_by_id(
        self,
        asset_id: str,
    ) -> JsonObject | None:
        with self._session_factory() as session:
            asset = session.scalar(
                select(Asset).where(
                    func.upper(Asset.asset_code)
                    == asset_id.upper(),
                    Asset.deleted_at.is_(None),
                )
            )

            if asset is None:
                return None

            return clone_payload(asset.payload)

    def list_health_scores(
        self,
    ) -> list[JsonObject]:
        with self._session_factory() as session:
            snapshots = session.scalars(
                select(AssetHealthSnapshot)
                .where(
                    AssetHealthSnapshot
                    .deleted_at.is_(None)
                )
                .order_by(
                    AssetHealthSnapshot.source_order,
                )
            ).all()

            return [
                clone_payload(snapshot.payload)
                for snapshot in snapshots
            ]