from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps.api.hybrid_retrieval.schemas import (
    HybridRetrievalHit,
    HybridRetrievalIndexResult,
    HybridRetrievalSearchRequest,
    HybridRetrievalSearchResponse,
    RetrievalDocumentMetadata,
)


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9-]+")
VECTOR_DIMENSIONS = 64


@dataclass(frozen=True)
class HybridRetrievalConfig:
    extracted_dir: Path = Path("data/ingestion/extracted")
    collection_dir: Path = Path("data/retrieval")
    collection_name: str = "plantmind_industrial_documents"


class HybridRetrievalService:
    def __init__(
        self,
        config: HybridRetrievalConfig | None = None,
    ) -> None:
        self.config = config or HybridRetrievalConfig()
        self.config.collection_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def build_index(
        self,
        *,
        collection_name: str | None = None,
        rebuild: bool = True,
    ) -> HybridRetrievalIndexResult:
        active_collection = collection_name or self.config.collection_name
        collection_path = self._collection_path(
            active_collection,
        )

        if collection_path.exists() and not rebuild:
            points = self._load_points(
                active_collection,
            )
            return HybridRetrievalIndexResult(
                collection_name=active_collection,
                total_points=len(points),
                indexed_document_ids=sorted(
                    {
                        point["metadata"]["document_id"]
                        for point in points
                    }
                ),
                message="Existing hybrid retrieval collection reused.",
            )

        points: list[dict[str, Any]] = []

        for artifact_path in sorted(
            self.config.extracted_dir.glob("*.json")
        ):
            artifact = json.loads(
                artifact_path.read_text(
                    encoding="utf-8",
                )
            )

            if artifact.get("status") != "completed":
                continue

            for chunk in artifact.get("chunks", []):
                metadata = self._metadata_from_artifact(
                    artifact=artifact,
                    chunk=chunk,
                )

                points.append(
                    {
                        "point_id": self._point_id(
                            chunk["chunk_id"]
                        ),
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        "tokens": self._tokens(
                            chunk["text"]
                        ),
                        "embedding": self._embed_text(
                            chunk["text"]
                        ),
                        "metadata": metadata.model_dump(),
                    }
                )

        collection_path.write_text(
            json.dumps(
                {
                    "collection_name": active_collection,
                    "vector_dimensions": VECTOR_DIMENSIONS,
                    "points": points,
                },
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return HybridRetrievalIndexResult(
            collection_name=active_collection,
            total_points=len(points),
            indexed_document_ids=sorted(
                {
                    point["metadata"]["document_id"]
                    for point in points
                }
            ),
            message="Hybrid retrieval collection built.",
        )

    def search(
        self,
        request: HybridRetrievalSearchRequest,
        *,
        collection_name: str | None = None,
    ) -> HybridRetrievalSearchResponse:
        active_collection = collection_name or self.config.collection_name
        points = self._load_points(
            active_collection,
        )

        query_tokens = self._tokens(
            request.query,
        )
        query_embedding = self._embed_text(
            request.query,
        )

        hits: list[HybridRetrievalHit] = []

        for point in points:
            metadata = RetrievalDocumentMetadata.model_validate(
                point["metadata"]
            )

            if not self._passes_filters(
                metadata=metadata,
                request=request,
            ):
                continue

            point_tokens = point["tokens"]
            matched_terms = sorted(
                set(query_tokens) & set(point_tokens)
            )

            keyword_score = self._keyword_score(
                query_tokens=query_tokens,
                document_tokens=point_tokens,
            )

            vector_score = self._cosine_similarity(
                query_embedding,
                point["embedding"],
            )

            if request.mode == "keyword":
                hybrid_score = keyword_score
            elif request.mode == "vector":
                hybrid_score = vector_score
            else:
                hybrid_score = (
                    0.65 * keyword_score
                    + 0.35 * vector_score
                )

            if hybrid_score <= 0:
                continue

            hits.append(
                HybridRetrievalHit(
                    point_id=point["point_id"],
                    chunk_id=point["chunk_id"],
                    text=point["text"],
                    keyword_score=round(keyword_score, 6),
                    vector_score=round(vector_score, 6),
                    hybrid_score=round(hybrid_score, 6),
                    matched_terms=matched_terms,
                    metadata=metadata,
                )
            )

        hits.sort(
            key=lambda hit: hit.hybrid_score,
            reverse=True,
        )

        trimmed_hits = hits[
            : max(1, request.top_k)
        ]

        return HybridRetrievalSearchResponse(
            query=request.query,
            mode=request.mode,
            total_hits=len(trimmed_hits),
            hits=trimmed_hits,
        )

    def _metadata_from_artifact(
        self,
        artifact: dict[str, Any],
        chunk: dict[str, Any],
    ) -> RetrievalDocumentMetadata:
        document_id = artifact["document_id"]
        chunk_text = chunk.get("text", "")

        is_obsolete = bool(
            re.search(
                r"\bobsolete\b|\bsuperseded\b|\barchived\b",
                chunk_text,
                flags=re.IGNORECASE,
            )
        )

        revision = self._infer_revision(
            document_id=document_id,
        )

        return RetrievalDocumentMetadata(
            document_id=document_id,
            revision=revision,
            page=chunk.get("page_number", 1),
            section=chunk.get("section_heading"),
            asset_ids=chunk.get("asset_ids", []),
            source_quality=0.6 if is_obsolete else 1.0,
            approval_status="obsolete" if is_obsolete else "approved",
            effective_date=None,
            document_status="ready",
            is_obsolete=is_obsolete,
            source_filename=f"{document_id}.json",
            document_type="industrial_document",
        )

    def _passes_filters(
        self,
        metadata: RetrievalDocumentMetadata,
        request: HybridRetrievalSearchRequest,
    ) -> bool:
        if (
            request.document_status != "all"
            and metadata.document_status != request.document_status
        ):
            return False

        if (
            not request.include_obsolete
            and metadata.is_obsolete
        ):
            return False

        if (
            request.revision is not None
            and metadata.revision != request.revision
        ):
            return False

        if request.asset_ids:
            requested_assets = set(
                request.asset_ids
            )
            document_assets = set(
                metadata.asset_ids
            )

            if not requested_assets & document_assets:
                return False

        return True

    def _keyword_score(
        self,
        query_tokens: list[str],
        document_tokens: list[str],
    ) -> float:
        if not query_tokens or not document_tokens:
            return 0.0

        query_set = set(query_tokens)
        document_set = set(document_tokens)

        overlap = query_set & document_set

        return len(overlap) / len(query_set)

    def _tokens(
        self,
        text: str,
    ) -> list[str]:
        return [
            token.lower()
            for token in TOKEN_PATTERN.findall(text)
        ]

    def _embed_text(
        self,
        text: str,
    ) -> list[float]:
        vector = [0.0] * VECTOR_DIMENSIONS

        for token in self._tokens(text):
            digest = hashlib.sha256(
                token.encode("utf-8")
            ).digest()

            index = int.from_bytes(
                digest[:2],
                "big",
            ) % VECTOR_DIMENSIONS

            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(
            sum(value * value for value in vector)
        )

        if norm == 0:
            return vector

        return [
            value / norm
            for value in vector
        ]

    def _cosine_similarity(
        self,
        left: list[float],
        right: list[float],
    ) -> float:
        if not left or not right:
            return 0.0

        score = sum(
            left_value * right_value
            for left_value, right_value in zip(
                left,
                right,
                strict=False,
            )
        )

        return max(
            0.0,
            score,
        )

    def _infer_revision(
        self,
        document_id: str,
    ) -> int:
        match = re.search(
            r"REV-(\d+)",
            document_id,
        )

        if not match:
            return 1

        return int(
            match.group(1)
        )

    def _point_id(
        self,
        chunk_id: str,
    ) -> str:
        return hashlib.sha256(
            chunk_id.encode("utf-8")
        ).hexdigest()

    def _collection_path(
        self,
        collection_name: str,
    ) -> Path:
        safe_name = re.sub(
            r"[^A-Za-z0-9._-]+",
            "_",
            collection_name,
        )

        return self.config.collection_dir / f"{safe_name}.json"

    def _load_points(
        self,
        collection_name: str,
    ) -> list[dict[str, Any]]:
        collection_path = self._collection_path(
            collection_name,
        )

        if not collection_path.exists():
            return []

        payload = json.loads(
            collection_path.read_text(
                encoding="utf-8",
            )
        )

        return payload.get(
            "points",
            [],
        )