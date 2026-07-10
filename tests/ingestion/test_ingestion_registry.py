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


def test_lists_ingestion_manifests(
    tmp_path: Path,
) -> None:
    source = tmp_path / "inspection-note.txt"
    source.write_text(
        "P-101 inspection found vibration increase.",
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

    manifests = service.list_manifests()

    assert len(manifests) == 1
    assert manifests[0].document_id == result.document_id
    assert manifests[0].asset_ids == ["P-101"]


def test_loads_single_ingestion_manifest(
    tmp_path: Path,
) -> None:
    source = tmp_path / "maintenance-note.md"
    source.write_text(
        "P-101 bearing inspection is required.",
        encoding="utf-8",
    )

    service = make_service(tmp_path)

    result = service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(source),
            asset_ids=["P-101"],
            document_type="maintenance_note",
        )
    )

    manifest = service.load_manifest(
        result.document_id
    )

    assert manifest.document_id == result.document_id
    assert manifest.document_type == "maintenance_note"
    assert manifest.text_extract_status == "extracted"