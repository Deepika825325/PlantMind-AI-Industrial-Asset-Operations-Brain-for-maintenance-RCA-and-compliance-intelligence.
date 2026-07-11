from __future__ import annotations

from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
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


class Plant(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    __tablename__ = "plants"

    plant_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="Asia/Kolkata",
        server_default="Asia/Kolkata",
    )

    areas: Mapped[list["Area"]] = relationship(
        back_populates="plant",
    )


class Area(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    __tablename__ = "areas"

    __table_args__ = (
        UniqueConstraint(
            "plant_id",
            "area_code",
            name="uq_areas_plant_id_area_code",
        ),
    )

    plant_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "plants.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    area_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    plant: Mapped[Plant] = relationship(
        back_populates="areas",
    )

    systems: Mapped[list["System"]] = relationship(
        back_populates="area",
    )


class System(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    __tablename__ = "systems"

    __table_args__ = (
        UniqueConstraint(
            "area_id",
            "system_code",
            name="uq_systems_area_id_system_code",
        ),
    )

    area_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "areas.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    system_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    area: Mapped[Area] = relationship(
        back_populates="systems",
    )

    assets: Mapped[list["Asset"]] = relationship(
        back_populates="system",
    )