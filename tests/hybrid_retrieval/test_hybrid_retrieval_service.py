from __future__ import annotations

from pathlib import Path

from apps.api.hybrid_retrieval.schemas import HybridRetrievalSearchRequest
from apps.api.hybrid_retrieval.service import (
    HybridRetrievalConfig,
    HybridRetrievalService,
)


def write_extracted_artifact(
    extracted_dir: Path,
    *,
    document_id: str,
    chunks: list[dict],
) -> None:
    extracted_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_path = extracted_dir / f"{document_id}.json"
    artifact_path.write_text(
        {
            "status": "completed",
            "document_id": document_id,
            "chunks": chunks,
        }.__repr__().replace("'", '"'),
        encoding="utf-8",
    )


def make_service(
    tmp_path: Path,
) -> HybridRetrievalService:
    return HybridRetrievalService(
        HybridRetrievalConfig(
            extracted_dir=tmp_path / "extracted",
            collection_dir=tmp_path / "retrieval",
            collection_name="plantmind_test_documents",
        )
    )


def test_hybrid_retrieval_finds_p101_procedure(
    tmp_path: Path,
) -> None:
    extracted_dir = tmp_path / "extracted"

    write_extracted_artifact(
        extracted_dir,
        document_id="DOC-P101-REV-1",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-1-PAGE-0001-CHUNK-0001",
                "text": (
                    "P-101 bearing procedure requires lubrication, "
                    "vibration inspection, and post-maintenance verification."
                ),
                "page_number": 1,
                "section_heading": "P-101 Bearing Procedure",
                "asset_ids": ["P-101"],
            }
        ],
    )

    service = make_service(tmp_path)

    index_result = service.build_index(
        collection_name="plantmind_test_documents",
        rebuild=True,
    )

    assert index_result.total_points == 1

    response = service.search(
        HybridRetrievalSearchRequest(
            query="P-101 bearing lubrication procedure",
            asset_ids=["P-101"],
            top_k=3,
        ),
        collection_name="plantmind_test_documents",
    )

    assert response.total_hits == 1

    hit = response.hits[0]

    assert hit.metadata.document_id == "DOC-P101-REV-1"
    assert hit.metadata.page == 1
    assert hit.metadata.section == "P-101 Bearing Procedure"
    assert "P-101" in hit.metadata.asset_ids
    assert "procedure" in hit.matched_terms


def test_asset_mode_excludes_unrelated_documents(
    tmp_path: Path,
) -> None:
    extracted_dir = tmp_path / "extracted"

    write_extracted_artifact(
        extracted_dir,
        document_id="DOC-P101-REV-1",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-1-PAGE-0001-CHUNK-0001",
                "text": "P-101 bearing lubrication procedure.",
                "page_number": 1,
                "section_heading": "P-101 Procedure",
                "asset_ids": ["P-101"],
            }
        ],
    )

    write_extracted_artifact(
        extracted_dir,
        document_id="DOC-HX301-REV-1",
        chunks=[
            {
                "chunk_id": "DOC-HX301-REV-1-PAGE-0001-CHUNK-0001",
                "text": "HX-301 fouling inspection procedure.",
                "page_number": 1,
                "section_heading": "HX-301 Procedure",
                "asset_ids": ["HX-301"],
            }
        ],
    )

    service = make_service(tmp_path)
    service.build_index(
        collection_name="plantmind_test_documents",
        rebuild=True,
    )

    response = service.search(
        HybridRetrievalSearchRequest(
            query="inspection procedure",
            asset_ids=["P-101"],
            top_k=5,
        ),
        collection_name="plantmind_test_documents",
    )

    assert response.total_hits == 1
    assert response.hits[0].metadata.asset_ids == ["P-101"]


def test_obsolete_documents_are_flagged_and_excluded_by_default(
    tmp_path: Path,
) -> None:
    extracted_dir = tmp_path / "extracted"

    write_extracted_artifact(
        extracted_dir,
        document_id="DOC-P101-REV-1",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-1-PAGE-0001-CHUNK-0001",
                "text": "OBSOLETE P-101 bearing lubrication procedure superseded.",
                "page_number": 1,
                "section_heading": "Old Procedure",
                "asset_ids": ["P-101"],
            }
        ],
    )

    service = make_service(tmp_path)
    service.build_index(
        collection_name="plantmind_test_documents",
        rebuild=True,
    )

    default_response = service.search(
        HybridRetrievalSearchRequest(
            query="P-101 bearing lubrication procedure",
            asset_ids=["P-101"],
        ),
        collection_name="plantmind_test_documents",
    )

    assert default_response.total_hits == 0

    obsolete_response = service.search(
        HybridRetrievalSearchRequest(
            query="P-101 bearing lubrication procedure",
            asset_ids=["P-101"],
            include_obsolete=True,
        ),
        collection_name="plantmind_test_documents",
    )

    assert obsolete_response.total_hits == 1
    assert obsolete_response.hits[0].metadata.is_obsolete is True
    assert obsolete_response.hits[0].metadata.approval_status == "obsolete"


def test_revision_filter_returns_only_requested_revision(
    tmp_path: Path,
) -> None:
    extracted_dir = tmp_path / "extracted"

    write_extracted_artifact(
        extracted_dir,
        document_id="DOC-P101-REV-1",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-1-PAGE-0001-CHUNK-0001",
                "text": "P-101 old procedure.",
                "page_number": 1,
                "section_heading": "Old",
                "asset_ids": ["P-101"],
            }
        ],
    )

    write_extracted_artifact(
        extracted_dir,
        document_id="DOC-P101-REV-2",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-2-PAGE-0001-CHUNK-0001",
                "text": "P-101 updated procedure.",
                "page_number": 1,
                "section_heading": "Updated",
                "asset_ids": ["P-101"],
            }
        ],
    )

    service = make_service(tmp_path)
    service.build_index(
        collection_name="plantmind_test_documents",
        rebuild=True,
    )

    response = service.search(
        HybridRetrievalSearchRequest(
            query="P-101 procedure",
            asset_ids=["P-101"],
            revision=2,
        ),
        collection_name="plantmind_test_documents",
    )

    assert response.total_hits == 1
    assert response.hits[0].metadata.revision == 2
    assert response.hits[0].metadata.section == "Updated"