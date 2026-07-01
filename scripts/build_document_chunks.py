from pathlib import Path
import csv
import json
import re
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DOCUMENTS_INDEX_FILE = PROCESSED_DIR / "documents_index.csv"
OUTPUT_FILE = PROCESSED_DIR / "document_chunks.json"

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def read_csv_rows(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def read_text_file(file_path):
    try:
        return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def read_json_file(file_path):
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return json.dumps(data, indent=2, ensure_ascii=False)

    except Exception:
        return ""


def normalize_text(text):
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_into_sections(text):
    lines = text.splitlines()

    sections = []
    current_title = "Document Body"
    current_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#"):
            if current_lines:
                sections.append({
                    "section_title": current_title,
                    "text": "\n".join(current_lines).strip()
                })

            current_title = stripped.replace("#", "").strip() or "Untitled Section"
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "section_title": current_title,
            "text": "\n".join(current_lines).strip()
        })

    return sections


def sliding_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = normalize_text(text)

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if end < len(text):
            last_space = chunk.rfind(" ")
            if last_space > chunk_size * 0.7:
                chunk = chunk[:last_space]
                end = start + last_space

        chunks.append(chunk.strip())

        if end >= len(text):
            break

        start = max(0, end - overlap)

    return chunks


def build_document_text(document_record):
    relative_path = document_record["relative_path"]
    file_path = RAW_DIR / relative_path
    suffix = file_path.suffix.lower()

    if suffix in [".md", ".txt", ".csv"]:
        return read_text_file(file_path)

    if suffix == ".json":
        return read_json_file(file_path)

    if suffix == ".png":
        return document_record.get("summary", "")

    return document_record.get("summary", "")


def create_chunks_for_document(document_record):
    document_id = document_record["document_id"]
    document_type = document_record["document_type"]
    source_group = document_record["source_group"]
    asset_ids = document_record.get("asset_ids", "")
    tags = document_record.get("tags", "")
    title = document_record.get("title", "")

    raw_text = build_document_text(document_record)
    text = normalize_text(raw_text)

    if not text:
        text = document_record.get("summary", "")

    sections = split_into_sections(text)

    chunks = []
    chunk_counter = 1

    for section in sections:
        section_title = section["section_title"]
        section_text = section["text"]

        section_chunks = sliding_chunks(section_text)

        for chunk_text in section_chunks:
            chunk_id = f"{document_id}_CHUNK_{chunk_counter:03d}"

            chunks.append({
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_title": title,
                "document_type": document_type,
                "source_group": source_group,
                "section_title": section_title,
                "asset_ids": asset_ids.split(";") if asset_ids else [],
                "tags": tags.split(";") if tags else [],
                "chunk_text": chunk_text,
                "chunk_word_count": len(chunk_text.split()),
                "chunk_character_count": len(chunk_text),
                "relative_path": document_record["relative_path"],
                "created_at": datetime.now().isoformat(timespec="seconds")
            })

            chunk_counter += 1

    return chunks


def main():
    if not DOCUMENTS_INDEX_FILE.exists():
        raise FileNotFoundError(
            f"Missing {DOCUMENTS_INDEX_FILE}. Run build_documents_index.py first."
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    document_records = read_csv_rows(DOCUMENTS_INDEX_FILE)

    all_chunks = []

    for document_record in document_records:
        chunks = create_chunks_for_document(document_record)
        all_chunks.extend(chunks)

    output = {
        "project": "PlantMind AI",
        "artifact": "document_chunks",
        "total_documents": len(document_records),
        "total_chunks": len(all_chunks),
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "chunks": all_chunks
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print("PlantMind AI - Document Chunk Builder")
    print("=" * 50)
    print(f"Documents processed: {len(document_records)}")
    print(f"Chunks created: {len(all_chunks)}")
    print(f"Output created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()