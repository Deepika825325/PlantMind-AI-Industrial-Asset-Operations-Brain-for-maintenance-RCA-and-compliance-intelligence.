import re
from typing import Any, Dict, List, Optional

from apps.api.services.data_loader import (
    get_demo_answers,
    get_document_chunks,
    get_rag_seed_questions,
)


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "why", "what", "which",
    "who", "where", "when", "how", "to", "for", "of", "in", "on", "and",
    "or", "with", "by", "as", "it", "this", "that", "be", "been", "from",
    "current", "generate", "list", "all"
}


ASSET_IDS = ["P-101", "C-201", "HX-301"]


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


def keyword_score(query_tokens: List[str], text: str) -> int:
    text_lower = text.lower()
    score = 0

    for token in query_tokens:
        if token in text_lower:
            score += 1

    return score


def retrieve_chunks(
    question: str,
    asset_id: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    chunks = get_document_chunks()
    query_tokens = tokenize(question)

    detected_assets = detect_assets(question)

    if asset_id:
        detected_assets = [asset_id.upper()]

    scored_chunks = []

    for chunk in chunks:
        chunk_text = chunk.get("chunk_text", "")
        chunk_assets = chunk.get("asset_ids", [])
        chunk_tags = chunk.get("tags", [])

        score = keyword_score(query_tokens, chunk_text)

        for detected_asset in detected_assets:
            if detected_asset in chunk_assets or detected_asset in chunk_tags:
                score += 5

        if score > 0:
            scored_chunks.append({
                "score": score,
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("document_id"),
                "document_title": chunk.get("document_title"),
                "document_type": chunk.get("document_type"),
                "section_title": chunk.get("section_title"),
                "asset_ids": chunk_assets,
                "tags": chunk_tags,
                "relative_path": chunk.get("relative_path"),
                "chunk_text": chunk_text,
            })

    scored_chunks = sorted(
        scored_chunks,
        key=lambda item: item["score"],
        reverse=True
    )

    return scored_chunks[:top_k]


def find_demo_answer(question: str) -> Dict[str, Any] | None:
    demo_answers = get_demo_answers()
    query_tokens = tokenize(question)

    best_answer = None
    best_score = 0

    for answer in demo_answers:
        candidate_text = f'{answer.get("question", "")} {answer.get("answer", "")}'
        score = keyword_score(query_tokens, candidate_text)

        for asset_id in detect_assets(question):
            if answer.get("asset_id") == asset_id:
                score += 5

        if score > best_score:
            best_score = score
            best_answer = answer

    if best_answer and best_score >= 2:
        return best_answer

    return None


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
        short_text = text[:600].strip()

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


def ask_plantmind(
    question: str,
    asset_id: Optional[str] = None,
    top_k: int = 5
) -> Dict[str, Any]:
    retrieved_chunks = retrieve_chunks(
        question=question,
        asset_id=asset_id,
        top_k=top_k
    )

    demo_answer = find_demo_answer(question)

    if demo_answer:
        answer = demo_answer.get("answer")
        supporting_sources = demo_answer.get("supporting_sources", [])
        answer_mode = "demo_answer_match"
    else:
        answer = generate_rule_based_answer(question, retrieved_chunks)
        supporting_sources = [
            chunk["document_id"] for chunk in retrieved_chunks
        ]
        answer_mode = "retrieval_rule_based"

    return {
        "question": question,
        "detected_assets": detect_assets(question),
        "answer": answer,
        "answer_mode": answer_mode,
        "supporting_sources": supporting_sources,
        "retrieved_context": retrieved_chunks,
    }


def get_suggested_questions() -> List[Dict[str, Any]]:
    return get_rag_seed_questions()