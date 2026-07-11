from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from apps.api.db.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class Asset(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    __tablename__ = "assets"

    __table_args__ = (
        CheckConstraint(
            "risk_score IS NULL OR "
            "(risk_score >= 0 AND risk_score <= 100)",
            name="asset_risk_score_range",
        ),
        CheckConstraint(
            "health_score IS NULL OR "
            "(health_score >= 0 AND health_score <= 100)",
            name="asset_health_score_range",
        ),
    )

    system_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "systems.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    asset_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    criticality: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        server_default="active",
    )

    risk_score: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    health_score: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
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

    system: Mapped["System"] = relationship(
        back_populates="assets",
    )

    components: Mapped[list["Component"]] = relationship(
        back_populates="asset",
    )

    sensors: Mapped[list["Sensor"]] = relationship(
        back_populates="asset",
    )


class Component(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    __tablename__ = "components"

    __table_args__ = (
        UniqueConstraint(
            "asset_id",
            "component_code",
            name=(
                "uq_components_asset_id_"
                "component_code"
            ),
        ),
    )

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "assets.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    component_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    component_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    manufacturer: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    model_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    serial_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    asset: Mapped[Asset] = relationship(
        back_populates="components",
    )

    sensors: Mapped[list["Sensor"]] = relationship(
        back_populates="component",
    )


class Sensor(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    __tablename__ = "sensors"

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "assets.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    component_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "components.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    sensor_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    sensor_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        server_default="active",
    )

    asset: Mapped[Asset] = relationship(
        back_populates="sensors",
    )

    component: Mapped[Component | None] = relationship(
        back_populates="sensors",
    )