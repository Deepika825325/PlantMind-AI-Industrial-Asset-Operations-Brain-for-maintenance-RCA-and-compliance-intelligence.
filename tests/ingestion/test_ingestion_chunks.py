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
            chunks_dir=tmp_path / "chunks",
            chunk_size_chars=80,
            chunk_overlap_chars=10,
        )
    )


def test_ingestion_creates_chunk_manifest(
    tmp_path: Path,
) -> None:
    source = tmp_path / "inspection-note.txt"
    source.write_text(
        "P-101 vibration increased. "
        "Bearing temperature increased. "
        "Lubrication evidence is missing. "
        "Maintenance inspection is required.",
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

    assert result.chunk_count >= 1
    assert result.chunk_manifest_path is not None
    assert Path(result.chunk_manifest_path).exists()

    chunk_manifest = service.load_chunk_manifest(
        result.document_id
    )

    assert chunk_manifest.document_id == result.document_id
    assert chunk_manifest.total_chunks == result.chunk_count
    assert chunk_manifest.chunks[0].chunk_id.startswith(
        f"{result.document_id}-CHUNK-"
    )
    assert chunk_manifest.chunks[0].asset_ids == ["P-101"]


def test_long_text_is_split_into_multiple_chunks(
    tmp_path: Path,
) -> None:
    source = tmp_path / "long-inspection-note.txt"
    source.write_text(
        "P-101 high vibration and bearing temperature. " * 20,
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

    chunk_manifest = service.load_chunk_manifest(
        result.document_id
    )

    assert result.chunk_count > 1
    assert chunk_manifest.total_chunks == result.chunk_count
    assert all(
        chunk.token_estimate >= 1
        for chunk in chunk_manifest.chunks
    )


def test_stored_only_document_has_no_chunks(
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

    assert result.text_extract_status == "stored_only"
    assert result.chunk_count == 0
    assert result.chunk_manifest_path is None