from sqlalchemy import Uuid

from apps.api.db import models as _models  # noqa: F401
from apps.api.db.base import Base


EXPECTED_TABLES = {
    "plants",
    "areas",
    "systems",
    "assets",
    "components",
    "sensors",
    "users",
    "roles",
    "user_roles",
}

ENTITY_TABLES = EXPECTED_TABLES - {
    "user_roles",
}


def test_expected_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_entity_tables_have_uuid_primary_keys() -> None:
    for table_name in ENTITY_TABLES:
        table = Base.metadata.tables[table_name]

        assert "id" in table.c
        assert table.c.id.primary_key
        assert isinstance(
            table.c.id.type,
            Uuid,
        )


def test_entity_tables_have_timestamps() -> None:
    for table_name in ENTITY_TABLES:
        columns = Base.metadata.tables[
            table_name
        ].c

        assert "created_at" in columns
        assert "updated_at" in columns


def test_entity_tables_support_soft_deletion() -> None:
    for table_name in ENTITY_TABLES:
        columns = Base.metadata.tables[
            table_name
        ].c

        assert "deleted_at" in columns


def test_asset_code_is_unique() -> None:
    assets = Base.metadata.tables["assets"]

    unique_columns = {
        column.name
        for constraint in assets.constraints
        if constraint.__class__.__name__
        == "UniqueConstraint"
        for column in constraint.columns
    }

    assert "asset_code" in unique_columns


def test_foundational_foreign_keys_exist() -> None:
    expected = {
        "areas": "plants.id",
        "systems": "areas.id",
        "assets": "systems.id",
        "components": "assets.id",
        "sensors": "assets.id",
    }

    for table_name, target in expected.items():
        table = Base.metadata.tables[table_name]

        targets = {
            foreign_key.target_fullname
            for foreign_key in table.foreign_keys
        }

        assert target in targets