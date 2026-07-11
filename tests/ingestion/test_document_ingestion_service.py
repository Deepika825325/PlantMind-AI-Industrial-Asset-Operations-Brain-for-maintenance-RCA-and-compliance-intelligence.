from __future__ import annotations

from pathlib import Path

from apps.api.ingestion.schemas import DocumentIngestionRequest
from apps.api.ingestion.service import (
    DocumentIngestionService,
    IngestionConfig,
)


def make_service(
    tmp_path: Path,
) -> DocumentIngestionService:
    return DocumentIngestionService(
        IngestionConfig(
            raw_dir=tmp_path / "raw",
            normalized_dir=tmp_path / "normalized",
            manifest_dir=tmp_path / "manifests",
        )
    )


def test_ingests_text_document(
    tmp_path: Path,
) -> None:
    source = tmp_path / "P-101 inspection note.txt"
    source.write_text(
        "P-101 vibration is high. Bearing temperature is rising.",
        encoding="utf-8",
    )

    service = make_service(tmp_path)

    result = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
            source_system="manual_upload",
            uploaded_by="admin@plantmind.local",
        )
    )

    assert result.status == "ingested"
    assert result.document_id.startswith("DOC-ING-")
    assert result.asset_ids == ["P-101"]
    assert result.text_extract_status == "extracted"
    assert result.normalized_text_path is not None
    assert Path(result.stored_raw_path).exists()
    assert Path(result.normalized_text_path).exists()
    assert Path(result.manifest_path).exists()
    assert "P-101 vibration is high" in Path(
        result.normalized_text_path
    ).read_text(encoding="utf-8")


def test_duplicate_ingestion_is_deterministic(
    tmp_path: Path,
) -> None:
    source = tmp_path / "pump-note.md"
    source.write_text(
        "# Pump Note\nP-101 requires bearing inspection.",
        encoding="utf-8",
    )

    service = make_service(tmp_path)

    first = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="maintenance_note",
        )
    )

    second = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="maintenance_note",
        )
    )

    assert first.document_id == second.document_id
    assert first.checksum_sha256 == second.checksum_sha256
    assert second.status == "duplicate"


def test_pdf_is_stored_without_text_extraction(
    tmp_path: Path,
) -> None:
    source = tmp_path / "manual.pdf"
    source.write_bytes(b"%PDF-1.4 fake demo pdf")

    service = make_service(tmp_path)

    result = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="manual",
        )
    )

    assert result.status == "ingested"
    assert result.text_extract_status == "stored_only"
    assert result.normalized_text_path is None
    assert Path(result.stored_raw_path).exists()
    assert Path(result.manifest_path).exists()