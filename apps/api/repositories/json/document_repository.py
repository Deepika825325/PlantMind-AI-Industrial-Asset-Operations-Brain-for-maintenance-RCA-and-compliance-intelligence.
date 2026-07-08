from __future__ import annotations

from typing import Any

from apps.api.repositories.json.data_source import (
    PROJECT_ROOT,
    load_demo_json,
    load_processed_json,
)


class JsonDocumentRepository:
    """JSON-backed repository for documents and document chunks."""

    def list_documents(self) -> list[dict[str, Any]]:
        data = load_demo_json("documents.json")
        return data.get("documents", [])

    def get_document_by_id(
        self,
        document_id: str,
    ) -> dict[str, Any] | None:
        for document in self.list_documents():
            if document.get("document_id") == document_id:
                return document

        return None

    def list_document_chunks(self) -> list[dict[str, Any]]:
        data = load_processed_json("document_chunks.json")
        return data.get("chunks", [])

    def list_chunks_by_document_id(
        self,
        document_id: str,
    ) -> list[dict[str, Any]]:
        return [
            chunk
            for chunk in self.list_document_chunks()
            if chunk.get("document_id") == document_id
        ]

    def read_document_text(
        self,
        document_id: str,
    ) -> str:
        document = self.get_document_by_id(document_id)

        if not document:
            return ""

        relative_path = document.get("relative_path")

        if not relative_path:
            return ""

        file_path = (
            PROJECT_ROOT
            / "data"
            / "raw"
            / str(relative_path)
        )

        if not file_path.exists() or not file_path.is_file():
            return ""

        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )