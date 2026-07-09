from apps.api.repositories.postgres import (
    PostgresAssetRepository,
)
from apps.api.repositories.registry import (
    get_repository_registry,
)


def test_json_mode_remains_default(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "PLANTMIND_DATA_BACKEND",
        raising=False,
    )

    get_repository_registry.cache_clear()

    registry = get_repository_registry()

    assert registry.mode == "demo"


def test_postgres_mode_can_be_selected(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "PLANTMIND_DATA_BACKEND",
        "postgres",
    )

    get_repository_registry.cache_clear()

    registry = get_repository_registry()

    assert registry.mode == "postgres"
    assert isinstance(
        registry.assets,
        PostgresAssetRepository,
    )

    get_repository_registry.cache_clear()


def test_demo_alias_can_be_selected(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "PLANTMIND_DATA_BACKEND",
        "demo",
    )

    get_repository_registry.cache_clear()

    assert (
        get_repository_registry().mode
        == "demo"
    )

    get_repository_registry.cache_clear()