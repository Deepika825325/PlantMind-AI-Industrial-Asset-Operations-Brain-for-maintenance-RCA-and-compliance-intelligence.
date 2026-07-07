from apps.api.services.evidence_integrity_service import enrich_ask_response
import re
from typing import Any, Dict, List, Optional, Tuple

from apps.api.services.data_loader import (
    get_compliance_matrix,
    get_demo_answers,
    get_document_chunks,
    get_documents,
    get_maintenance_events,
    get_rag_seed_questions,
)

from apps.api.services.structured_answer_service import answer_structured_question


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "why", "what", "which",
    "who", "where", "when", "how", "to", "for", "of", "in", "on", "and",
    "or", "with", "by", "as", "it", "this", "that", "be", "been", "from",
    "current", "generate", "list", "all", "show", "tell", "me", "does",
    "do", "did", "should", "can", "could", "would", "about"
}

ASSET_IDS = ["P-101", "C-201", "HX-301"]

ANSWER_TYPE_KEYWORDS = {
    "risk_explanation": ["risk", "high risk", "medium risk", "why"],
    "rca": ["rca", "root cause", "cause", "failure reason"],
    "compliance_gap": ["compliance", "gap", "missing", "delayed", "overdue", "non-compliant"],
    "maintenance_recommendation": ["maintenance", "action", "recommend", "work order", "planned"],
    "sensor_evidence": ["sensor", "reading", "vibration", "temperature", "pressure", "rul", "efficiency"],
    "document_retrieval": ["document", "sop", "inspection", "report", "evidence"],
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z0-9\-]+", text.lower())

    return [
        token for token in tokens
        if token not in STOPWORDS and len(token) > 1
    ]


def detect_assets(question: str) -> List[str]:
    question_upper = question.upper()

    return [
        asset_id for asset_id in ASSET_IDS
        if asset_id in question_upper
    ]


def detect_answer_type(question: str) -> str:
    question_lower = question.lower()

    best_type = "general"
    best_score = 0

    for answer_type, keywords in ANSWER_TYPE_KEYWORDS.items():
        score = 0

        for keyword in keywords:
          if keyword in question_lower:
              score += 1

        if score > best_score:
            best_score = score
            best_type = answer_type

    return best_type


def get_document_lookup() -> Dict[str, Dict[str, Any]]:
    documents = get_documents()

    lookup = {}

    for document in documents:
        lookup[document["document_id"]] = document

        clean_id = document["document_id"].replace("_Pump_Vibration_Inspection", "")
        lookup[clean_id] = document

    return lookup


def phrase_bonus(question: str, chunk_text: str) -> int:
    question_lower = question.lower()
    chunk_lower = chunk_text.lower()

    bonus = 0

    important_phrases = [
        "high vibration",
        "bearing temperature",
        "abnormal noise",
        "lubrication evidence",
        "work permit",
        "filter replacement",
        "outlet temperature",
        "pressure drop",
        "efficiency index",
        "cleaning evidence",
        "root cause",
        "fouling",
        "remaining useful life",
        "rul",
        "non-compliant",
    ]

    for phrase in important_phrases:
        if phrase in question_lower and phrase in chunk_lower:
            bonus += 4

    return bonus


def answer_type_bonus(answer_type: str, chunk: Dict[str, Any]) -> int:
    document_type = chunk.get("document_type", "").lower()
    section_title = chunk.get("section_title", "").lower()
    text = chunk.get("chunk_text", "").lower()

    bonus = 0

    if answer_type == "risk_explanation":
        if "risk" in section_title or "risk" in text:
            bonus += 4
        if "inspection" in document_type or "incident" in document_type:
            bonus += 3

    elif answer_type == "rca":
        if "root cause" in text or "cause" in text or "rca" in text:
            bonus += 5
        if "incident" in document_type:
            bonus += 4

    elif answer_type == "compliance_gap":
        if "compliance" in document_type or "gap" in text or "missing" in text:
            bonus += 5

    elif answer_type == "maintenance_recommendation":
        if "recommended action" in section_title or "recommended" in text:
            bonus += 5
        if "work order" in text:
            bonus += 3

    elif answer_type == "sensor_evidence":
        sensor_terms = ["vibration", "temperature", "pressure", "rul", "efficiency", "reading"]
        if any(term in text for term in sensor_terms):
            bonus += 4

    elif answer_type == "document_retrieval":
        if "sop" in document_type or "inspection" in document_type or "document" in text:
            bonus += 3

    return bonus


def keyword_score(query_tokens: List[str], text: str) -> int:
    text_lower = text.lower()
    score = 0

    for token in query_tokens:
        if token in text_lower:
            score += 1

    return score


def score_chunk(
    question: str,
    query_tokens: List[str],
    detected_assets: List[str],
    answer_type: str,
    chunk: Dict[str, Any]
) -> int:
    chunk_text = chunk.get("chunk_text", "")
    chunk_assets = chunk.get("asset_ids", [])
    chunk_tags = chunk.get("tags", [])
    document_title = chunk.get("document_title", "")
    document_type = chunk.get("document_type", "")

    score = 0

    score += keyword_score(query_tokens, chunk_text)
    score += keyword_score(query_tokens, document_title)
    score += keyword_score(query_tokens, document_type)

    for detected_asset in detected_assets:
        if detected_asset in chunk_assets:
            score += 8
        if detected_asset in chunk_tags:
            score += 5
        if detected_asset in chunk_text:
            score += 4

    score += phrase_bonus(question, chunk_text)
    score += answer_type_bonus(answer_type, chunk)

    return score


def retrieve_chunks(
    question: str,
    asset_id: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    chunks = get_document_chunks()
    query_tokens = tokenize(question)
    detected_assets = detect_assets(question)
    answer_type = detect_answer_type(question)

    if asset_id:
        detected_assets = [asset_id.upper()]

    scored_chunks = []

    for chunk in chunks:
        score = score_chunk(
            question=question,
            query_tokens=query_tokens,
            detected_assets=detected_assets,
            answer_type=answer_type,
            chunk=chunk
        )

        if score > 0:
            scored_chunks.append({
                "score": score,
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("document_id"),
                "document_title": chunk.get("document_title"),
                "document_type": chunk.get("document_type"),
                "section_title": chunk.get("section_title"),
                "asset_ids": chunk.get("asset_ids", []),
                "tags": chunk.get("tags", []),
                "relative_path": chunk.get("relative_path"),
                "chunk_text": chunk.get("chunk_text", ""),
            })

    scored_chunks = sorted(
        scored_chunks,
        key=lambda item: item["score"],
        reverse=True
    )

    return scored_chunks[:top_k]


def find_demo_answer(question: str) -> Tuple[Dict[str, Any] | None, int]:
    demo_answers = get_demo_answers()
    query_tokens = tokenize(question)

    best_answer = None
    best_score = 0

    for answer in demo_answers:
        candidate_text = f'{answer.get("question", "")} {answer.get("answer", "")}'
        score = keyword_score(query_tokens, candidate_text)

        for asset_id in detect_assets(question):
            if answer.get("asset_id") == asset_id:
                score += 6

        if score > best_score:
            best_score = score
            best_answer = answer

    if best_answer and best_score >= 2:
        return best_answer, best_score

    return None, best_score


def make_citations(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    citations = []
    seen = set()

    for index, chunk in enumerate(retrieved_chunks, start=1):
        document_id = chunk.get("document_id")

        if not document_id or document_id in seen:
            continue

        seen.add(document_id)

        chunk_text = chunk.get("chunk_text", "")
        evidence_excerpt = chunk_text[:350].strip()

        if len(chunk_text) > 350:
            evidence_excerpt += "..."

        citations.append({
            "citation_id": f"CIT-{index:03d}",
            "document_id": document_id,
            "document_title": chunk.get("document_title"),
            "document_type": chunk.get("document_type"),
            "section_title": chunk.get("section_title"),
            "relative_path": chunk.get("relative_path"),
            "evidence_excerpt": evidence_excerpt,
        })

    return citations


def calculate_confidence(
    answer_mode: str,
    retrieved_chunks: List[Dict[str, Any]],
    supporting_sources: List[str]
) -> float:
    if not retrieved_chunks and not supporting_sources:
        return 0.25

    top_score = retrieved_chunks[0]["score"] if retrieved_chunks else 0
    source_count = len(set(supporting_sources))
    chunk_count = len(retrieved_chunks)

    confidence = 0.35

    if answer_mode == "demo_answer_match":
        confidence += 0.25

    confidence += min(top_score / 25, 0.2)
    confidence += min(source_count * 0.04, 0.12)
    confidence += min(chunk_count * 0.02, 0.08)

    return round(min(confidence, 0.95), 2)


def source_ids_from_chunks(retrieved_chunks: List[Dict[str, Any]]) -> List[str]:
    sources = []

    for chunk in retrieved_chunks:
        document_id = chunk.get("document_id")
        if document_id and document_id not in sources:
            sources.append(document_id)

    return sources


def generate_rule_based_answer(
    question: str,
    retrieved_chunks: List[Dict[str, Any]]
) -> str:
    question_lower = normalize_text(question)
    detected_assets = detect_assets(question)

    if "p-101" in question_lower and "risk" in question_lower:
        return (
            "P-101 is high risk because the available evidence indicates critical vibration, "
            "bearing temperature warning, abnormal bearing noise, and missing lubrication or work permit evidence."
        )

    if "p-101" in question_lower and ("root cause" in question_lower or "rca" in question_lower):
        return (
            "The likely root causes for P-101 are bearing wear, lubrication degradation, shaft misalignment, "
            "loose mounting, or mechanical imbalance. Missing lubrication evidence increases the likelihood of "
            "lubrication-related bearing risk."
        )

    if "c-201" in question_lower and "risk" in question_lower:
        return (
            "C-201 is medium risk because its estimated RUL is decreasing, outlet temperature is above normal, "
            "pressure ratio is unstable, and filter replacement verification is delayed."
        )

    if "hx-301" in question_lower and ("fouled" in question_lower or "fouling" in question_lower or "risk" in question_lower):
        return (
            "HX-301 is suspected to be fouled because outlet temperature is below normal, pressure drop is high, "
            "efficiency is reduced, and cleaning/fouling inspection evidence is overdue."
        )

    if "non-compliant" in question_lower or "compliance" in question_lower:
        return (
            "The non-compliant assets are P-101, C-201, and HX-301. P-101 has missing lubrication and work permit "
            "evidence, C-201 has delayed filter replacement verification, and HX-301 has overdue cleaning and missing "
            "work permit evidence."
        )

    if retrieved_chunks:
        top_chunk = retrieved_chunks[0]
        text = top_chunk.get("chunk_text", "")
        short_text = text[:700].strip()

        return (
            "Based on the retrieved project documents, the most relevant evidence says: "
            f"{short_text}"
        )

    if detected_assets:
        return (
            f"I found the asset {', '.join(detected_assets)}, but I could not retrieve enough supporting text. "
            "Try asking about risk, RCA, compliance gaps, maintenance action, or sensor evidence."
        )

    return (
        "I could not find strong supporting evidence for this question in the current PlantMind demo dataset. "
        "Try asking about P-101 risk, C-201 RUL, HX-301 fouling, compliance gaps, work orders, or P&ID assets."
    )


def suggested_followups_for_answer(question: str, detected_assets: List[str], answer_type: str) -> List[str]:
    asset = detected_assets[0] if detected_assets else None

    if asset == "P-101":
        return [
            "What is the likely root cause of P-101 vibration?",
            "Which compliance evidence is missing for P-101?",
            "What maintenance action is recommended for P-101?"
        ]

    if asset == "C-201":
        return [
            "Why is C-201 medium risk?",
            "Which C-201 evidence is delayed?",
            "What maintenance should be planned for C-201?"
        ]

    if asset == "HX-301":
        return [
            "Why is HX-301 suspected to be fouled?",
            "Which evidence is missing for HX-301?",
            "Generate RCA for HX-301 low heat transfer efficiency."
        ]

    if answer_type == "compliance_gap":
        return [
            "Which assets are non-compliant?",
            "Which compliance evidence is missing for P-101?",
            "Which evidence is missing for HX-301?"
        ]

    return [
        "Why is P-101 high risk?",
        "Why is C-201 medium risk?",
        "Why is HX-301 suspected to be fouled?"
    ]


def ask_plantmind(
    question: str,
    asset_id: Optional[str] = None,
    top_k: int = 5
) -> Dict[str, Any]:
    answer_type = detect_answer_type(question)
    detected_assets = detect_assets(question)

    if asset_id:
        detected_assets = [asset_id.upper()]

    structured_answer = answer_structured_question(
        question=question,
        asset_id=asset_id
    )

    if structured_answer:
        structured_answer_type = structured_answer.get(
            "answer_type",
            answer_type
        )

        response = {
            "question": question,
            "detected_assets": detected_assets,
            "answer_type": structured_answer_type,
            "answer": structured_answer.get(
                "answer",
                ""
            ),
            "answer_mode": structured_answer.get(
                "answer_mode",
                "structured_domain_answer"
            ),
            "confidence_score": structured_answer.get(
                "confidence_score",
                0.98
            ),
            "supporting_sources": structured_answer.get(
                "supporting_sources",
                []
            ),
            "citations": structured_answer.get(
                "citations",
                []
            ),
            "retrieved_context": structured_answer.get(
                "retrieved_context",
                []
            ),
            "structured_context": structured_answer.get(
                "structured_context",
                {}
            ),
            "suggested_followups": suggested_followups_for_answer(
                question=question,
                detected_assets=detected_assets,
                answer_type=structured_answer_type
            )
        }

        return enrich_ask_response(
            response,
            asset_id=asset_id
        )

    retrieved_chunks = retrieve_chunks(
        question=question,
        asset_id=asset_id,
        top_k=top_k
    )

    demo_answer, demo_score = find_demo_answer(question)

    if demo_answer:
        answer = demo_answer.get("answer")
        supporting_sources = demo_answer.get(
            "supporting_sources",
            []
        )
        answer_mode = "demo_answer_match"
    else:
        answer = generate_rule_based_answer(
            question,
            retrieved_chunks
        )
        supporting_sources = (
            source_ids_from_chunks(
                retrieved_chunks
            )
        )
        answer_mode = "retrieval_rule_based"

    citations = make_citations(
        retrieved_chunks
    )

    confidence_score = calculate_confidence(
        answer_mode=answer_mode,
        retrieved_chunks=retrieved_chunks,
        supporting_sources=supporting_sources
    )

    response = {
        "question": question,
        "detected_assets": detected_assets,
        "answer_type": answer_type,
        "answer": answer,
        "answer_mode": answer_mode,
        "confidence_score": confidence_score,
        "supporting_sources": supporting_sources,
        "citations": citations,
        "retrieved_context": retrieved_chunks,
        "structured_context": {},
        "suggested_followups": suggested_followups_for_answer(
            question=question,
            detected_assets=detected_assets,
            answer_type=answer_type
        )
    }

    return enrich_ask_response(
        response,
        asset_id=asset_id
    )


def search_evidence(
    query: str,
    asset_id: Optional[str] = None,
    top_k: int = 10
) -> Dict[str, Any]:
    chunks = retrieve_chunks(
        question=query,
        asset_id=asset_id,
        top_k=top_k
    )

    return {
        "query": query,
        "asset_id": asset_id,
        "total": len(chunks),
        "results": chunks
    }


def get_suggested_questions() -> List[Dict[str, Any]]:
    return get_rag_seed_questions()
