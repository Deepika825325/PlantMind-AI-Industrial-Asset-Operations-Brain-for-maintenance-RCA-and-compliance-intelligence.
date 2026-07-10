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
            chunk_size_chars=120,
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


def test_search_returns_relevant_p101_chunk(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-inspection.txt"
    source.write_text(
        "P-101 vibration increased and bearing temperature increased. "
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

    indexing_service.build_index()

    response = indexing_service.search_index(
        "Why is P-101 vibration high?",
        asset_id="P-101",
    )

    assert response.total >= 1
    assert response.hits[0].rank == 1
    assert response.hits[0].asset_ids == ["P-101"]
    assert "vibration" in response.hits[0].matched_terms


def test_search_respects_asset_filter(
    tmp_path: Path,
) -> None:
    p101 = tmp_path / "p101-note.txt"
    hx301 = tmp_path / "hx301-note.txt"

    p101.write_text(
        "P-101 vibration increased near the bearing.",
        encoding="utf-8",
    )
    hx301.write_text(
        "HX-301 fouling reduced heat transfer efficiency.",
        encoding="utf-8",
    )

    ingestion_service = make_ingestion_service(tmp_path)

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(p101),
            asset_ids=["P-101"],
            document_type="inspection_note",
        )
    )

    ingestion_service.ingest_document(
        DocumentIngestionRequest(
            source_path=str(hx301),
            asset_ids=["HX-301"],
            document_type="inspection_note",
        )
    )

    indexing_service = make_indexing_service(
        tmp_path,
        ingestion_service,
    )

    indexing_service.build_index()

    response = indexing_service.search_index(
        "fouling heat transfer",
        asset_id="HX-301",
    )

    assert response.total >= 1
    assert response.hits[0].asset_ids == ["HX-301"]
    assert "fouling" in response.hits[0].matched_terms


def test_search_returns_empty_when_no_match(
    tmp_path: Path,
) -> None:
    source = tmp_path / "p101-note.txt"
    source.write_text(
        "P-101 vibration increased near the bearing.",
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

    indexing_service.build_index()

    response = indexing_service.search_index(
        "compressor seal leakage",
        asset_id="C-201",
    )

    assert response.total == 0
    assert response.hits == []