from __future__ import annotations

from sqlalchemy import select

from apps.api.db.models.documents import (
    Document,
    DocumentChunk,
)
from apps.api.repositories.json.data_source import (
    PROJECT_ROOT,
)
from apps.api.repositories.postgres.base import (
    JsonObject,
    PostgresRepositoryBase,
    clone_payload,
)


class PostgresDocumentRepository(
    PostgresRepositoryBase,
):
    """PostgreSQL-backed document repository."""

    def list_documents(self) -> list[JsonObject]:
        with self._session_factory() as session:
            documents = session.scalars(
                select(Document)
                .where(
                    Document.deleted_at.is_(None)
                )
                .order_by(
                    Document.source_order,
                    Document.id,
                )
            ).all()

            return [
                clone_payload(document.payload)
                for document in documents
            ]

    def get_document_by_id(
        self,
        document_id: str,
    ) -> JsonObject | None:
        # Match JsonDocumentRepository:
        # return the first document with matching document_id.
        with self._session_factory() as session:
            document = session.scalars(
                select(Document)
                .where(
                    Document.document_code
                    == document_id,
                    Document.deleted_at.is_(None),
                )
                .order_by(
                    Document.source_order,
                    Document.id,
                )
                .limit(1)
            ).first()

            if document is None:
                return None

            return clone_payload(document.payload)

    def list_document_chunks(
        self,
    ) -> list[JsonObject]:
        with self._session_factory() as session:
            chunks = session.scalars(
                select(DocumentChunk)
                .where(
                    DocumentChunk.deleted_at.is_(None)
                )
                .order_by(
                    DocumentChunk.source_order,
                    DocumentChunk.id,
                )
            ).all()

            return [
                clone_payload(chunk.payload)
                for chunk in chunks
            ]

    def list_chunks_by_document_id(
        self,
        document_id: str,
    ) -> list[JsonObject]:
        # Match JsonDocumentRepository:
        # filter by chunk payload document_id, not by a unique DB document row.
        chunks = self.list_document_chunks()

        return [
            chunk
            for chunk in chunks
            if chunk.get("document_id") == document_id
        ]

    def read_document_text(
        self,
        document_id: str,
    ) -> str:
        document = self.get_document_by_id(
            document_id
        )

        if document is None:
            return ""

        relative_path = document.get(
            "relative_path"
        )

        if not relative_path:
            return ""

        file_path = (
            PROJECT_ROOT
            / "data"
            / "raw"
            / str(relative_path)
        )

        if (
            not file_path.exists()
            or not file_path.is_file()
        ):
            return ""

        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )