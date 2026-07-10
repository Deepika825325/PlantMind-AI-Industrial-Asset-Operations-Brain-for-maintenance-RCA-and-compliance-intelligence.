from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

from apps.api.rag_answering.schemas import (
    RagAnswerCitation,
    RagAnswerRequest,
    RagAnswerResponse,
)
from apps.api.rag_indexing.service import (
    IngestionRagIndexingService,
)


@dataclass(frozen=True)
class RagAnsweringConfig:
    max_citations: int = 4
    max_quote_chars: int = 360


class IngestionRagAnsweringService:
    def __init__(
        self,
        rag_indexing_service: IngestionRagIndexingService,
        config: RagAnsweringConfig | None = None,
    ) -> None:
        self.rag_indexing_service = rag_indexing_service
        self.config = config or RagAnsweringConfig()

    def answer_question(
        self,
        request: RagAnswerRequest,
    ) -> RagAnswerResponse:
        search_response = self.rag_indexing_service.search_index(
            query=request.question,
            asset_id=request.asset_id,
            document_type=request.document_type,
            limit=request.limit,
        )

        if not search_response.hits:
            return RagAnswerResponse(
                answer_id=self._answer_id(),
                question=request.question,
                answer=(
                    "I could not find enough evidence in the ingested "
                    "documents to answer this question. Ingest more "
                    "relevant documents or broaden the asset/document filter."
                ),
                confidence=0.0,
                retrieval_status="no_relevant_context",
                total_citations=0,
                citations=[],
            )

        citations: list[RagAnswerCitation] = []

        for index, hit in enumerate(
            search_response.hits[
                : self.config.max_citations
            ],
            start=1,
        ):
            citations.append(
                RagAnswerCitation(
                    citation_id=f"CIT-{index:03d}",
                    document_id=hit.document_id,
                    chunk_id=hit.chunk_id,
                    chunk_index=hit.chunk_index,
                    source_filename=hit.source_filename,
                    asset_ids=hit.asset_ids,
                    document_type=hit.document_type,
                    score=hit.score,
                    matched_terms=hit.matched_terms,
                    quoted_text=self._quote_text(
                        hit.text,
                    ),
                )
            )

        answer = self._compose_answer(
            question=request.question,
            citations=citations,
        )

        confidence = self._confidence(
            citations=citations,
        )

        return RagAnswerResponse(
            answer_id=self._answer_id(),
            question=request.question,
            answer=answer,
            confidence=confidence,
            retrieval_status="answered_with_ingested_context",
            total_citations=len(citations),
            citations=citations,
        )

    def _compose_answer(
        self,
        question: str,
        citations: list[RagAnswerCitation],
    ) -> str:
        evidence_lines = []

        for citation in citations:
            sentence = self._best_sentence(
                citation.quoted_text,
                citation.matched_terms,
            )

            evidence_lines.append(
                f"{sentence} [{citation.citation_id}]"
            )

        joined_evidence = " ".join(evidence_lines)

        return (
            "Based on the ingested PlantMind documents, "
            f"the answer to '{question}' is supported by the following evidence: "
            f"{joined_evidence}"
        )

    def _best_sentence(
        self,
        text: str,
        matched_terms: list[str],
    ) -> str:
        sentences = [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?])\s+",
                text.strip(),
            )
            if sentence.strip()
        ]

        if not sentences:
            return text.strip()

        if not matched_terms:
            return sentences[0]

        ranked = sorted(
            sentences,
            key=lambda sentence: sum(
                term.lower() in sentence.lower()
                for term in matched_terms
            ),
            reverse=True,
        )

        return ranked[0]

    def _quote_text(
        self,
        text: str,
    ) -> str:
        cleaned = re.sub(
            r"\s+",
            " ",
            text.strip(),
        )

        if len(cleaned) <= self.config.max_quote_chars:
            return cleaned

        return cleaned[
            : self.config.max_quote_chars
        ].rstrip() + "..."

    def _confidence(
        self,
        citations: list[RagAnswerCitation],
    ) -> float:
        if not citations:
            return 0.0

        best_score = max(
            citation.score
            for citation in citations
        )

        citation_bonus = min(
            0.25,
            len(citations) * 0.06,
        )

        score_component = min(
            0.7,
            best_score / 20,
        )

        return round(
            min(
                0.95,
                0.15 + score_component + citation_bonus,
            ),
            4,
        )

    def _answer_id(self) -> str:
        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d%H%M%S%f")

        return f"RAG-ANS-{timestamp}"