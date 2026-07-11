from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from apps.api.db.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class DatasetSnapshot(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    """Top-level metadata for imported demo datasets."""

    __tablename__ = "dataset_snapshots"

    dataset_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )


class AssetHealthSnapshot(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    """Latest API-compatible health payload for an asset."""

    __tablename__ = "asset_health_snapshots"

    __table_args__ = (
        UniqueConstraint(
            "asset_id",
            name=(
                "uq_asset_health_snapshots_"
                "asset_id"
            ),
        ),
    )

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "assets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )