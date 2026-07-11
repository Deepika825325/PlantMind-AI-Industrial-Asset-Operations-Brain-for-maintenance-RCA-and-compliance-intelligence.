from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from apps.api.ingestion.service import DocumentIngestionService
from apps.api.rag_indexing.schemas import (
    RagIndexBuildResult,
    RagIndexManifest,
    RagIndexedChunk,
    RagSearchHit,
    RagSearchResponse,
    RagSearchHit,
    RagSearchResponse,
)


@dataclass(frozen=True)
class RagIndexingConfig:
    index_dir: Path = Path("data/ingestion/rag_index")
    index_filename: str = "rag_chunks.json"
    manifest_filename: str = "rag_index_manifest.json"
    max_keyword_terms: int = 20


class IngestionRagIndexingService:
    def __init__(
        self,
        ingestion_service: DocumentIngestionService,
        config: RagIndexingConfig | None = None,
    ) -> None:
        self.ingestion_service = ingestion_service
        self.config = config or RagIndexingConfig()
        self.config.index_dir.mkdir(parents=True, exist_ok=True)

    def build_index(self) -> RagIndexBuildResult:
        manifests = self.ingestion_service.list_manifests()

        indexed_chunks: list[RagIndexedChunk] = []

        for manifest in manifests:
            if not manifest.chunk_count:
                continue

            try:
                chunk_manifest = (
                    self.ingestion_service.load_chunk_manifest(
                        manifest.document_id
                    )
                )
            except FileNotFoundError:
                continue

            for chunk in chunk_manifest.chunks:
                normalized_text = self._normalize_text(
                    chunk.text
                )

                indexed_chunks.append(
                    RagIndexedChunk(
                        document_id=chunk.document_id,
                        chunk_id=chunk.chunk_id,
                        chunk_index=chunk.chunk_index,
                        text=chunk.text,
                        normalized_text=normalized_text,
                        keyword_terms=self._keyword_terms(
                            normalized_text
                        ),
                        asset_ids=chunk.asset_ids,
                        document_type=chunk.document_type,
                        source_filename=chunk.source_filename,
                        character_start=chunk.character_start,
                        character_end=chunk.character_end,
                        token_estimate=chunk.token_estimate,
                    )
                )

        index_path = self.config.index_dir / self.config.index_filename
        manifest_path = self.config.index_dir / self.config.manifest_filename

        index_path.write_text(
            json.dumps(
                [
                    chunk.model_dump()
                    for chunk in indexed_chunks
                ],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        asset_ids = sorted(
            {
                asset_id
                for chunk in indexed_chunks
                for asset_id in chunk.asset_ids
            }
        )

        document_types = sorted(
            {
                chunk.document_type
                for chunk in indexed_chunks
            }
        )

        index_manifest = RagIndexManifest(
            index_id=self._index_id(),
            source="ingestion_chunk_manifests",
            total_documents=len(
                {
                    chunk.document_id
                    for chunk in indexed_chunks
                }
            ),
            total_chunks=len(indexed_chunks),
            asset_ids=asset_ids,
            document_types=document_types,
            index_path=str(index_path),
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

        manifest_path.write_text(
            index_manifest.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return RagIndexBuildResult(
            index_id=index_manifest.index_id,
            status="built",
            total_documents=index_manifest.total_documents,
            total_chunks=index_manifest.total_chunks,
            index_path=str(index_path),
            manifest_path=str(manifest_path),
            message="Ingestion chunks indexed for RAG retrieval.",
        )


    def search_index(
        self,
        query: str,
        *,
        asset_id: str | None = None,
        document_type: str | None = None,
        limit: int = 5,
    ) -> RagSearchResponse:
        normalized_query = self._normalize_text(query)
        query_terms = self._keyword_terms(
            normalized_query
        )

        chunks = self.load_index()

        scored_hits: list[tuple[float, RagIndexedChunk, list[str]]] = []

        for chunk in chunks:
            if asset_id and asset_id not in chunk.asset_ids:
                continue

            if document_type and chunk.document_type != document_type:
                continue

            matched_terms = [
                term
                for term in query_terms
                if term in chunk.normalized_text
                or term in chunk.keyword_terms
            ]

            if not matched_terms:
                continue

            score = self._score_chunk(
                chunk=chunk,
                query_terms=query_terms,
                matched_terms=matched_terms,
                asset_id=asset_id,
                document_type=document_type,
            )

            scored_hits.append(
                (
                    score,
                    chunk,
                    matched_terms,
                )
            )

        scored_hits.sort(
            key=lambda item: (
                item[0],
                -item[1].chunk_index,
            ),
            reverse=True,
        )

        hits = [
            RagSearchHit(
                rank=index + 1,
                score=round(score, 4),
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                asset_ids=chunk.asset_ids,
                document_type=chunk.document_type,
                source_filename=chunk.source_filename,
                matched_terms=matched_terms,
            )
            for index, (
                score,
                chunk,
                matched_terms,
            ) in enumerate(scored_hits[: max(1, limit)])
        ]

        return RagSearchResponse(
            query=query,
            total=len(hits),
            hits=hits,
        )

    def _score_chunk(
        self,
        chunk: RagIndexedChunk,
        query_terms: list[str],
        matched_terms: list[str],
        asset_id: str | None,
        document_type: str | None,
    ) -> float:
        score = 0.0

        for term in matched_terms:
            score += 3.0

            if term in chunk.keyword_terms:
                score += 2.0

            score += min(
                3,
                chunk.normalized_text.count(term),
            ) * 0.5

        if asset_id and asset_id in chunk.asset_ids:
            score += 1.5

        if document_type and document_type == chunk.document_type:
            score += 1.0

        if query_terms:
            score += len(matched_terms) / len(query_terms)

        return score

    def load_index(self) -> list[RagIndexedChunk]:
        index_path = self.config.index_dir / self.config.index_filename

        if not index_path.exists():
            raise FileNotFoundError(
                f"RAG index not found: {index_path}"
            )

        raw_chunks = json.loads(
            index_path.read_text(
                encoding="utf-8",
            )
        )

        return [
            RagIndexedChunk.model_validate(chunk)
            for chunk in raw_chunks
        ]

    def load_manifest(self) -> RagIndexManifest:
        manifest_path = self.config.index_dir / self.config.manifest_filename

        if not manifest_path.exists():
            raise FileNotFoundError(
                f"RAG index manifest not found: {manifest_path}"
            )

        return RagIndexManifest.model_validate_json(
            manifest_path.read_text(
                encoding="utf-8",
            )
        )

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        return re.sub(
            r"\s+",
            " ",
            text.lower().strip(),
        )

    def _keyword_terms(
        self,
        normalized_text: str,
    ) -> list[str]:
        tokens = re.findall(
            r"[a-zA-Z][a-zA-Z0-9_-]{2,}",
            normalized_text,
        )

        stopwords = {
            "and",
            "the",
            "for",
            "with",
            "from",
            "this",
            "that",
            "into",
            "are",
            "was",
            "were",
            "has",
            "have",
            "had",
            "will",
            "shall",
            "should",
            "required",
        }

        terms: list[str] = []

        for token in tokens:
            if token in stopwords:
                continue

            if token not in terms:
                terms.append(token)

            if len(terms) >= self.config.max_keyword_terms:
                break

        return terms

    def _index_id(self) -> str:
        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d%H%M%S")

        return f"RAG-IDX-{timestamp}"