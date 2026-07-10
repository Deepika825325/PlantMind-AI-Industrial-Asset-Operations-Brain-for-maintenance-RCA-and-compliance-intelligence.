from __future__ import annotations

from pathlib import Path

from apps.api.ingestion.schemas import DocumentIngestionRequest
from apps.api.ingestion.service import (
    DocumentIngestionService,
    IngestionConfig,
)
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
    RagIndexingConfig,
)


def make_ingestion_service(
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


def make_indexing_service(
    tmp_path: Path,
    ingestion_service: DocumentIngestionService,
) -> IngestionRagIndexingService:
    return IngestionRagIndexingService(
        ingestion_service=ingestion_service,
        config=RagIndexingConfig(
            index_dir=tmp_path / "rag_index",
        ),
    )


def test_builds_rag_index_from_ingestion_chunks(
    tmp_path: Path,
) -> None:
    source = tmp_path / "inspection-note.txt"
    source.write_text(
        "P-101 vibration increased. "
        "Bearing temperature increased. "
        "Lubrication evidence is missing.",
        encoding="utf-8",
    )

    ingestion_service = make_ingestion_service(tmp_path)

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    indexing_service = make_indexing_service(
        tmp_path,
        ingestion_service,
    )

    result = indexing_service.build_index()

    assert result.status == "built"
    assert result.total_documents == 1
    assert result.total_chunks >= 1
    assert Path(result.index_path).exists()
    assert Path(result.manifest_path).exists()

    chunks = indexing_service.load_index()

    assert chunks
    assert chunks[0].document_id.startswith("DOC-ING-")
    assert chunks[0].chunk_id.startswith(
        f"{chunks[0].document_id}-CHUNK-"
    )
    assert chunks[0].asset_ids == ["P-101"]
    assert "vibration" in chunks[0].keyword_terms


def test_builds_empty_index_when_no_ingested_chunks(
    tmp_path: Path,
) -> None:
    ingestion_service = make_ingestion_service(tmp_path)

    indexing_service = make_indexing_service(
        tmp_path,
        ingestion_service,
    )

    result = indexing_service.build_index()

    assert result.status == "built"
    assert result.total_documents == 0
    assert result.total_chunks == 0

    chunks = indexing_service.load_index()
    manifest = indexing_service.load_manifest()

    assert chunks == []
    assert manifest.total_documents == 0
    assert manifest.total_chunks == 0


def test_pdf_ingestion_is_skipped_from_rag_index(
    tmp_path: Path,
) -> None:
    source = tmp_path / "manual.pdf"
    source.write_bytes(b"%PDF-1.4 fake demo pdf")

    ingestion_service = make_ingestion_service(tmp_path)

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="manual",
        )
    )

    indexing_service = make_indexing_service(
        tmp_path,
        ingestion_service,
    )

    result = indexing_service.build_index()

    assert result.total_documents == 0
    assert result.total_chunks == 0
    assert indexing_service.load_index() == []