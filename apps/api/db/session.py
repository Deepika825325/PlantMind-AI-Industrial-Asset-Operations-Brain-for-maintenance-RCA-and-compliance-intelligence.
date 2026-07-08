from __future__ import annotations

import os
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)


def get_database_url() -> str:
    """Return the configured SQLAlchemy database URL."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is required for database operations."
        )

    return database_url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create the shared SQLAlchemy engine lazily."""

    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Return the shared session factory."""

    return sessionmaker(
        bind=get_engine(),
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )


def get_db_session() -> Generator[Session, None, None]:
    """Yield one database session and always close it."""

    session = get_session_factory()()

    try:
        yield session
    finally:
        session.close()


def clear_database_runtime_cache() -> None:
    """Clear cached engine/session objects for tests."""

    if get_engine.cache_info().currsize:
        get_engine().dispose()

    get_session_factory.cache_clear()
    get_engine.cache_clear()