from __future__ import annotations

import inspect
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from apps.api.hybrid_retrieval.service import (
    HybridRetrievalConfig,
    HybridRetrievalService,
)
from apps.api.main import app
from apps.api.routes import hybrid_retrieval as hybrid_route


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        hybrid_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_retrieval_user(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "test-data-scientist",
        "email": "data.scientist@plantmind.local",
        "role": "data_scientist",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_hybrid_service(
    tmp_path: Path,
) -> Iterator[HybridRetrievalService]:
    original_service = hybrid_route.hybrid_retrieval_service

    service = HybridRetrievalService(
        HybridRetrievalConfig(
            extracted_dir=tmp_path / "extracted",
            collection_dir=tmp_path / "retrieval",
            collection_name="plantmind_test_documents",
        )
    )

    hybrid_route.hybrid_retrieval_service = service

    try:
        yield service
    finally:
        hybrid_route.hybrid_retrieval_service = original_service


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
        json.dumps(
            {
                "status": "completed",
                "document_id": document_id,
                "chunks": chunks,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_hybrid_retrieval_index_api_builds_collection(
    tmp_path: Path,
) -> None:
    write_extracted_artifact(
        tmp_path / "extracted",
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

    with isolated_hybrid_service(tmp_path):
        with authorized_retrieval_user(
            "build_hybrid_retrieval_index"
        ):
            response = client.post(
                "/hybrid-retrieval/index",
                json={
                    "collection_name": "plantmind_test_documents",
                    "rebuild": True,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["collection_name"] == "plantmind_test_documents"
    assert payload["total_points"] == 1
    assert payload["indexed_document_ids"] == ["DOC-P101-REV-1"]


def test_hybrid_retrieval_search_api_filters_by_asset_and_revision(
    tmp_path: Path,
) -> None:
    write_extracted_artifact(
        tmp_path / "extracted",
        document_id="DOC-P101-REV-1",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-1-PAGE-0001-CHUNK-0001",
                "text": "P-101 old bearing procedure.",
                "page_number": 1,
                "section_heading": "Old P-101 Procedure",
                "asset_ids": ["P-101"],
            }
        ],
    )

    write_extracted_artifact(
        tmp_path / "extracted",
        document_id="DOC-P101-REV-2",
        chunks=[
            {
                "chunk_id": "DOC-P101-REV-2-PAGE-0001-CHUNK-0001",
                "text": "P-101 updated bearing lubrication procedure.",
                "page_number": 2,
                "section_heading": "Updated P-101 Procedure",
                "asset_ids": ["P-101"],
            }
        ],
    )

    with isolated_hybrid_service(tmp_path) as service:
        service.build_index(
            collection_name="plantmind_test_documents",
            rebuild=True,
        )

        with authorized_retrieval_user(
            "search_hybrid_retrieval"
        ):
            response = client.post(
                "/hybrid-retrieval/search",
                json={
                    "query": "P-101 bearing lubrication procedure",
                    "asset_ids": ["P-101"],
                    "revision": 2,
                    "top_k": 5,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total_hits"] == 1
    assert payload["hits"][0]["metadata"]["revision"] == 2
    assert payload["hits"][0]["metadata"]["section"] == "Updated P-101 Procedure"


def test_hybrid_retrieval_search_api_excludes_obsolete_by_default(
    tmp_path: Path,
) -> None:
    write_extracted_artifact(
        tmp_path / "extracted",
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

    with isolated_hybrid_service(tmp_path) as service:
        service.build_index(
            collection_name="plantmind_test_documents",
            rebuild=True,
        )

        with authorized_retrieval_user(
            "search_hybrid_retrieval"
        ):
            response = client.post(
                "/hybrid-retrieval/search",
                json={
                    "query": "P-101 bearing lubrication procedure",
                    "asset_ids": ["P-101"],
                    "top_k": 5,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total_hits"] == 0


def test_hybrid_retrieval_search_api_can_include_obsolete_documents(
    tmp_path: Path,
) -> None:
    write_extracted_artifact(
        tmp_path / "extracted",
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

    with isolated_hybrid_service(tmp_path) as service:
        service.build_index(
            collection_name="plantmind_test_documents",
            rebuild=True,
        )

        with authorized_retrieval_user(
            "search_hybrid_retrieval"
        ):
            response = client.post(
                "/hybrid-retrieval/search",
                json={
                    "query": "P-101 bearing lubrication procedure",
                    "asset_ids": ["P-101"],
                    "include_obsolete": True,
                    "top_k": 5,
                },
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total_hits"] == 1
    assert payload["hits"][0]["metadata"]["is_obsolete"] is True
    assert payload["hits"][0]["metadata"]["approval_status"] == "obsolete"


def test_hybrid_retrieval_requires_authentication() -> None:
    response = client.post(
        "/hybrid-retrieval/search",
        json={
            "query": "P-101 bearing procedure",
        },
    )

    assert response.status_code == 401