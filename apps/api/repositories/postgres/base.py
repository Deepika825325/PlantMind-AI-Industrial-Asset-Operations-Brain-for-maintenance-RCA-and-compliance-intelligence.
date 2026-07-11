from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.db.models.dataset import (
    DatasetSnapshot,
)
from apps.api.db.session import (
    get_session_factory,
)


JsonObject = dict[str, Any]
SessionFactory = Callable[[], Session]


def clone_payload(
    payload: JsonObject,
) -> JsonObject:
    """Return a detached copy of a stored JSON payload."""

    return deepcopy(payload)


def get_dataset_metadata(
    session: Session,
    dataset_key: str,
) -> JsonObject:
    """Read a stored top-level dataset wrapper."""

    snapshot = session.scalar(
        select(DatasetSnapshot).where(
            DatasetSnapshot.dataset_key
            == dataset_key,
            DatasetSnapshot.deleted_at.is_(None),
        )
    )

    if snapshot is None:
        return {}

    return clone_payload(snapshot.payload)


class PostgresRepositoryBase:
    """Shared lazy session handling for PostgreSQL repositories."""

    def __init__(
        self,
        session_factory: SessionFactory | None = None,
    ) -> None:
        self._explicit_session_factory = session_factory

    @property
    def _session_factory(self) -> SessionFactory:
        """Return a session factory only when data is actually queried.

        This keeps repository selection testable without requiring
        DATABASE_URL during object construction.
        """

        if self._explicit_session_factory is not None:
            return self._explicit_session_factory

        return get_session_factory()