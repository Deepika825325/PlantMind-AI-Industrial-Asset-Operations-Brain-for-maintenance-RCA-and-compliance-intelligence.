from __future__ import annotations

from pathlib import Path

import pytest

from apps.api.ingestion.schemas import DocumentIngestionRequest
from apps.api.ingestion.service import (
    DocumentIngestionService,
    IngestionConfig,
)


def make_service(
    tmp_path: Path,
    *,
    max_file_size_bytes: int = 1024 * 1024,
) -> DocumentIngestionService:
    return DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
            chunks_dir=tmp_path / "chunks",
            max_file_size_bytes=max_file_size_bytes,
        )
    )


def test_ingestion_adds_validation_lifecycle_and_revision_metadata(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-note.txt"
    source.write_text(
        "P-101 vibration increased near the bearing.",
        encoding="utf-8",
    )

    service = make_service(tmp_path)

    result = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    assert result.status == "ingested"
    assert result.lifecycle_status == "ready"
    assert result.upload_status == "uploaded"
    assert result.processing_status == "ready"
    assert result.detected_mime_type == "text/plain"
    assert result.max_file_size_bytes == 1024 * 1024
    assert result.storage_backend == "local_object_store"
    assert result.object_storage_path == result.stored_raw_path
    assert result.revision_group_id == "DOC-REV-P101-NOTE"
    assert result.revision_number == 1
    assert result.is_duplicate is False
    assert result.duplicate_of_document_id is None
    assert result.validation_errors == []


def test_duplicate_ingestion_is_detected_with_duplicate_metadata(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-note.txt"
    source.write_text(
        "P-101 vibration increased near the bearing.",
        encoding="utf-8",
    )

    service = make_service(tmp_path)

    first_result = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    second_result = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    assert second_result.status == "duplicate"
    assert second_result.is_duplicate is True
    assert second_result.duplicate_of_document_id == first_result.document_id
    assert second_result.revision_number == first_result.revision_number


def test_new_file_content_in_same_revision_group_increments_revision(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-note.txt"
    source.write_text(
        "P-101 vibration increased near the bearing.",
        encoding="utf-8",
    )

    service = make_service(tmp_path)

    first_result = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    source.write_text(
        "P-101 vibration increased and bearing temperature increased.",
        encoding="utf-8",
    )

    second_result = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    assert second_result.status == "ingested"
    assert second_result.document_id != first_result.document_id
    assert second_result.revision_group_id == first_result.revision_group_id
    assert second_result.revision_number == 2


def test_unsupported_extension_returns_structured_validation_error(
    tmp_path: Path,
) -> None:
    source = tmp_path / "unsupported.exe"
    source.write_text(
        "not a supported document",
        encoding="utf-8",
    )

    service = make_service(tmp_path)

    with pytest.raises(ValueError) as exc_info:
        service.ingest_document(
            DocumentIngestionRequest(
                source_path=str(source),
                asset_ids=["P-101"],
                document_type="unknown",
            )
        )

    assert "Unsupported file extension" in str(exc_info.value)


def test_file_size_validation_rejects_large_document(
    tmp_path: Path,
) -> None:
    source = tmp_path / "large-note.txt"
    source.write_text(
        "x" * 50,
        encoding="utf-8",
    )

    service = make_service(
        tmp_path,
        max_file_size_bytes=10,
    )

    with pytest.raises(ValueError) as exc_info:
        service.ingest_document(
            DocumentIngestionRequest(
                source_path=str(source),
                asset_ids=["P-101"],
                document_type="inspection_note",
            )
        )

    assert "maximum allowed size" in str(exc_info.value)