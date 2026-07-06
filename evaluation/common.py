from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import json
import math
import re
import urllib.error
import urllib.request


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DIR = PROJECT_ROOT / "evaluation"
CHARTS_DIR = EVALUATION_DIR / "charts"

ASSET_PATTERN = re.compile(r"\b(?:P|C|HX)-\d{3}\b", re.IGNORECASE)
WORK_ORDER_PATTERN = re.compile(r"\b(?:MWO-[A-Z0-9-]+|WO-[A-Z0-9-]+)\b", re.IGNORECASE)
RCA_PATTERN = re.compile(r"\bRCA-[A-Z0-9-]+\b", re.IGNORECASE)
CAUSE_PATTERN = re.compile(r"\b[A-Z]\d{3}-RC-\d{3}\b", re.IGNORECASE)
ACTION_PATTERN = re.compile(r"\b[A-Z]\d{3}-CA-\d{3}\b", re.IGNORECASE)
EVIDENCE_PATTERN = re.compile(r"\b[A-Z]\d{3}-EV-\d{3}\b", re.IGNORECASE)

FAILURE_MODE_PATTERNS = {
    "high vibration": re.compile(r"\bhigh vibration\b|\bvibration exceeded\b", re.IGNORECASE),
    "bearing wear": re.compile(r"\bbearing wear\b", re.IGNORECASE),
    "lubrication degradation": re.compile(
        r"\blubrication degradation\b|\bdegraded lubrication\b|\binsufficient lubrication\b",
        re.IGNORECASE,
    ),
    "shaft misalignment": re.compile(r"\bshaft misalignment\b|\bmisalignment\b", re.IGNORECASE),
    "fouling": re.compile(r"\bfouling\b", re.IGNORECASE),
    "low heat transfer efficiency": re.compile(
        r"\blow heat transfer efficiency\b|\breduced heat transfer\b",
        re.IGNORECASE,
    ),
    "filter verification delay": re.compile(
        r"\bfilter replacement verification\b.*\bdelayed\b|\bdelayed filter verification\b",
        re.IGNORECASE,
    ),
}


def ensure_output_directories() -> None:
    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def normalize_text(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9./%-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(value: Any) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:[./%-][a-z0-9]+)*", normalize_text(value))


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def f1_score(precision: float, recall: float) -> float:
    return safe_divide(2 * precision * recall, precision + recall)


def set_metrics(expected: Iterable[str], predicted: Iterable[str]) -> dict[str, float | int]:
    expected_set = {normalize_text(item) for item in expected if normalize_text(item)}
    predicted_set = {normalize_text(item) for item in predicted if normalize_text(item)}
    true_positive = len(expected_set & predicted_set)
    false_positive = len(predicted_set - expected_set)
    false_negative = len(expected_set - predicted_set)
    precision = safe_divide(true_positive, true_positive + false_positive)
    recall = safe_divide(true_positive, true_positive + false_negative)
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1_score(precision, recall),
    }


def jaccard_score(expected: Iterable[str], predicted: Iterable[str]) -> float:
    expected_set = {normalize_text(item) for item in expected if normalize_text(item)}
    predicted_set = {normalize_text(item) for item in predicted if normalize_text(item)}
    union = expected_set | predicted_set
    return safe_divide(len(expected_set & predicted_set), len(union)) if union else 1.0


def keyword_coverage(answer: str, expected_keywords: list[str]) -> float:
    answer_text = normalize_text(answer)
    if not expected_keywords:
        return 1.0
    matches = sum(1 for keyword in expected_keywords if normalize_text(keyword) in answer_text)
    return safe_divide(matches, len(expected_keywords))


def extract_entities(text: str, known_document_ids: Iterable[str] | None = None) -> dict[str, list[str]]:
    entities = {
        "asset_ids": sorted({match.upper() for match in ASSET_PATTERN.findall(text)}),
        "work_order_ids": sorted({match.upper() for match in WORK_ORDER_PATTERN.findall(text)}),
        "rca_case_ids": sorted({match.upper() for match in RCA_PATTERN.findall(text)}),
        "root_cause_ids": sorted({match.upper() for match in CAUSE_PATTERN.findall(text)}),
        "corrective_action_ids": sorted({match.upper() for match in ACTION_PATTERN.findall(text)}),
        "evidence_ids": sorted({match.upper() for match in EVIDENCE_PATTERN.findall(text)}),
        "failure_modes": sorted(
            name for name, pattern in FAILURE_MODE_PATTERNS.items() if pattern.search(text)
        ),
        "document_ids": [],
    }
    if known_document_ids:
        normalized_text = normalize_text(text)
        matches = []
        for document_id in known_document_ids:
            if normalize_text(document_id) in normalized_text:
                matches.append(document_id)
        entities["document_ids"] = sorted(set(matches))
    return entities


def flatten_records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []
    records: list[dict[str, Any]] = []
    for nested in value.values():
        if isinstance(nested, list) and nested and all(isinstance(item, dict) for item in nested):
            records.extend(nested)
    return records


def primary_record_id(record: dict[str, Any], fallback: str) -> str:
    for key in (
        "work_order_id",
        "case_id",
        "asset_id",
        "document_id",
        "rule_id",
        "gap_id",
        "event_id",
        "node_id",
        "id",
    ):
        value = record.get(key)
        if value:
            return str(value)
    return fallback


def load_document_catalog() -> list[dict[str, Any]]:
    path = PROJECT_ROOT / "data" / "demo" / "documents.json"
    if not path.exists():
        return []
    data = load_json(path)
    if isinstance(data, dict):
        return [item for item in data.get("documents", []) if isinstance(item, dict)]
    return []


def known_document_ids() -> list[str]:
    return [
        str(item.get("document_id"))
        for item in load_document_catalog()
        if item.get("document_id")
    ]


def _split_text(text: str, max_chars: int = 1800) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}".strip()
        else:
            if current:
                chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def load_retrieval_corpus() -> list[dict[str, str]]:
    corpus: list[dict[str, str]] = []
    processed_path = PROJECT_ROOT / "data" / "processed" / "document_chunks.json"
    if processed_path.exists():
        data = load_json(processed_path)
        chunks = data.get("chunks", []) if isinstance(data, dict) else []
        for index, chunk in enumerate(chunks):
            if not isinstance(chunk, dict):
                continue
            text = str(
                chunk.get("text")
                or chunk.get("content")
                or chunk.get("chunk_text")
                or ""
            )
            if not text:
                continue
            source_id = str(
                chunk.get("document_id")
                or chunk.get("source_id")
                or f"processed-chunk-{index + 1}"
            )
            corpus.append(
                {
                    "source_id": source_id,
                    "text": text,
                    "source_path": str(processed_path.relative_to(PROJECT_ROOT)),
                }
            )

    raw_root = PROJECT_ROOT / "data" / "raw"
    if raw_root.exists():
        for path in sorted(raw_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".json", ".csv"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for index, chunk in enumerate(_split_text(text)):
                corpus.append(
                    {
                        "source_id": path.stem,
                        "text": chunk,
                        "source_path": str(path.relative_to(PROJECT_ROOT)),
                        "chunk_id": f"{path.stem}-{index + 1}",
                    }
                )

    demo_root = PROJECT_ROOT / "data" / "demo"
    if demo_root.exists():
        for path in sorted(demo_root.glob("*.json")):
            try:
                data = load_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            records = flatten_records(data)
            if records:
                for index, record in enumerate(records):
                    corpus.append(
                        {
                            "source_id": primary_record_id(record, f"{path.stem}-{index + 1}"),
                            "text": json.dumps(record, ensure_ascii=False),
                            "source_path": str(path.relative_to(PROJECT_ROOT)),
                        }
                    )
            else:
                corpus.append(
                    {
                        "source_id": path.name,
                        "text": json.dumps(data, ensure_ascii=False),
                        "source_path": str(path.relative_to(PROJECT_ROOT)),
                    }
                )

    deduplicated: dict[tuple[str, str], dict[str, str]] = {}
    for item in corpus:
        key = (item["source_id"], item["text"])
        deduplicated[key] = item
    return list(deduplicated.values())


def lexical_retrieve(question: str, corpus: list[dict[str, str]], top_k: int = 5) -> list[dict[str, Any]]:
    query_tokens = set(tokenize(question))
    query_text = normalize_text(question)
    scored: list[dict[str, Any]] = []
    for item in corpus:
        text_tokens = set(tokenize(item["text"]))
        overlap = len(query_tokens & text_tokens)
        if not overlap:
            continue
        score = overlap / max(len(query_tokens), 1)
        source_id = normalize_text(item["source_id"])
        if source_id and source_id in query_text:
            score += 1.0
        for entity in extract_entities(question).values():
            for value in entity:
                if normalize_text(value) in normalize_text(item["text"]):
                    score += 0.15
        scored.append({**item, "score": score})
    return sorted(scored, key=lambda row: row["score"], reverse=True)[:top_k]


def extractive_answer(question: str, retrieved: list[dict[str, Any]]) -> str:
    if not retrieved:
        return "No relevant evidence was retrieved from the local PlantMind corpus."
    query_tokens = set(tokenize(question))
    candidates: list[tuple[float, str]] = []
    for item in retrieved:
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", item["text"]):
            sentence = sentence.strip(" -*\t")
            if len(sentence) < 20:
                continue
            sentence_tokens = set(tokenize(sentence))
            overlap = safe_divide(len(query_tokens & sentence_tokens), max(len(query_tokens), 1))
            if overlap > 0:
                candidates.append((overlap, sentence))
    selected: list[str] = []
    for _, sentence in sorted(candidates, key=lambda pair: pair[0], reverse=True):
        if sentence not in selected:
            selected.append(sentence)
        if len(selected) == 4:
            break
    if not selected:
        selected = [retrieved[0]["text"][:600]]
    return " ".join(selected)


def _post_json(url: str, payload: dict[str, Any], timeout_seconds: float) -> Any:
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def extract_answer_payload(payload: Any) -> tuple[str, list[str], list[str]]:
    if isinstance(payload, str):
        return payload, [], []

    if not isinstance(payload, dict):
        return json.dumps(payload, ensure_ascii=False), [], []

    answer = str(
        payload.get("answer")
        or payload.get("response")
        or payload.get("result")
        or payload.get("message")
        or ""
    )

    citation_values = payload.get("citations") or []
    if isinstance(citation_values, dict):
        citation_values = list(citation_values.values())
    if not isinstance(citation_values, list):
        citation_values = [citation_values]

    citations: list[str] = []
    support_texts: list[str] = []

    for item in citation_values:
        if isinstance(item, str):
            citations.append(item)
            continue

        if not isinstance(item, dict):
            continue

        citation_id = (
            item.get("document_id")
            or item.get("source_id")
            or item.get("id")
            or item.get("title")
            or item.get("relative_path")
        )

        if citation_id:
            citations.append(str(citation_id))

        support = (
            item.get("evidence_excerpt")
            or item.get("chunk_text")
            or item.get("text")
            or item.get("content")
            or item.get("excerpt")
            or item.get("snippet")
        )

        if support:
            support_texts.append(str(support))

    retrieved_context = payload.get("retrieved_context") or []

    if isinstance(retrieved_context, dict):
        retrieved_context = list(retrieved_context.values())

    if not isinstance(retrieved_context, list):
        retrieved_context = [retrieved_context]

    retrieved_document_ids: list[str] = []

    for item in retrieved_context:
        if not isinstance(item, dict):
            continue

        document_id = (
            item.get("document_id")
            or item.get("source_id")
            or item.get("id")
        )

        if document_id:
            retrieved_document_ids.append(str(document_id))

        support = (
            item.get("chunk_text")
            or item.get("evidence_excerpt")
            or item.get("text")
            or item.get("content")
            or item.get("excerpt")
            or item.get("snippet")
        )

        if support:
            support_texts.append(str(support))

    if not citations:
        citations.extend(retrieved_document_ids)

    return (
        answer,
        sorted(set(citations)),
        list(dict.fromkeys(support_texts)),
    )


def ask_plantmind_api(
    question: str,
    api_base: str,
    timeout_seconds: float = 20.0,
) -> tuple[str, list[str], list[str], str]:
    detected_assets = extract_entities(question).get(
        "asset_ids",
        [],
    )

    payload: dict[str, Any] = {
        "question": question,
        "top_k": 10,
    }

    if detected_assets:
        payload["asset_id"] = detected_assets[0]

    endpoint = "/ask"

    try:
        result = _post_json(
            f"{api_base.rstrip('/')}{endpoint}",
            payload,
            timeout_seconds,
        )
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
    ) as error:
        raise RuntimeError(
            f"{endpoint}: {error}"
        ) from error

    answer, citations, support_texts = (
        extract_answer_payload(result)
    )

    if not answer:
        raise RuntimeError(
            f"{endpoint}: response did not contain an answer"
        )

    return (
        answer,
        citations,
        support_texts,
        endpoint,
    )


def lexical_unsupported_claim_rate(answer: str, support_texts: list[str]) -> float:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", answer)
        if len(sentence.strip()) >= 15
    ]
    if not sentences:
        return 0.0
    support_tokens = set(tokenize(" ".join(support_texts)))
    if not support_tokens:
        return 1.0
    unsupported = 0
    for sentence in sentences:
        sentence_tokens = set(tokenize(sentence))
        if not sentence_tokens:
            continue
        overlap = safe_divide(len(sentence_tokens & support_tokens), len(sentence_tokens))
        if overlap < 0.15:
            unsupported += 1
    return safe_divide(unsupported, len(sentences))


def round_metrics(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return 0.0
        return round(value, 4)
    if isinstance(value, dict):
        return {key: round_metrics(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [round_metrics(item) for item in value]
    return value
