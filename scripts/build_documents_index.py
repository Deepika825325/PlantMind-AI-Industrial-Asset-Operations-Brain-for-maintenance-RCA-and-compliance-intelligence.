from pathlib import Path
import csv
import json
import re
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = PROCESSED_DIR / "documents_index.csv"

ASSET_PATTERN = re.compile(r"\b(P-101|C-201|HX-301)\b")
TAG_PATTERN = re.compile(r"\b(P-101|C-201|HX-301|FT-101|PT-201|TT-301|V-101|V-201|PID-001)\b")


def read_text_file(file_path):
    try:
        return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def read_json_file(file_path):
    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def extract_document_id(file_path, content):
    file_name = file_path.name

    if file_name.endswith(".metadata.json"):
        return file_name.replace(".metadata.json", "")

    if file_name.endswith(".md"):
        return file_name.replace(".md", "")

    if file_name.endswith(".txt"):
        return file_name.replace(".txt", "")

    if file_name.endswith(".png"):
        return file_name.replace(".png", "")

    first_line = content.splitlines()[0] if content else file_path.stem
    return first_line.replace("#", "").strip() or file_path.stem


def detect_document_type(file_path):
    path_text = str(file_path).replace("\\", "/").lower()
    file_name = file_path.name.lower()

    if "manuals_sops" in path_text:
        return "SOP / Manual"

    if "inspection_reports" in path_text:
        return "Inspection Report"

    if "incident_reports" in path_text:
        return "Incident Report"

    if "compliance" in path_text:
        return "Compliance Checklist"

    if "drawings" in path_text and file_name.endswith(".png"):
        return "P&ID Drawing Image"

    if "drawings" in path_text and file_name.endswith(".json"):
        return "P&ID Drawing Metadata"

    if "public_sources" in path_text:
        return "Public Source Reference"

    return "Document"


def detect_source_group(file_path):
    relative = file_path.relative_to(RAW_DIR)
    parts = relative.parts

    if len(parts) >= 2:
        return parts[1]

    return parts[0]


def extract_title_from_markdown(content, fallback):
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.replace("#", "").strip()

    return fallback


def extract_summary(content, max_chars=280):
    cleaned_lines = []

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            line = line.replace("#", "").strip()

        cleaned_lines.append(line)

    summary = " ".join(cleaned_lines)

    if len(summary) > max_chars:
        summary = summary[:max_chars].rstrip() + "..."

    return summary


def extract_assets_and_tags(content, file_path):
    combined_text = content + " " + file_path.name

    assets = sorted(set(ASSET_PATTERN.findall(combined_text)))
    tags = sorted(set(TAG_PATTERN.findall(combined_text)))

    return assets, tags


def build_markdown_or_text_record(file_path):
    content = read_text_file(file_path)
    document_id = extract_document_id(file_path, content)
    document_type = detect_document_type(file_path)
    title = extract_title_from_markdown(content, document_id)
    summary = extract_summary(content)
    assets, tags = extract_assets_and_tags(content, file_path)

    return {
        "document_id": document_id,
        "title": title,
        "file_name": file_path.name,
        "relative_path": str(file_path.relative_to(RAW_DIR)).replace("\\", "/"),
        "document_type": document_type,
        "source_group": detect_source_group(file_path),
        "asset_ids": ";".join(assets),
        "tags": ";".join(tags),
        "word_count": len(content.split()),
        "character_count": len(content),
        "summary": summary,
        "indexed_at": datetime.now().isoformat(timespec="seconds"),
    }


def build_json_record(file_path):
    data = read_json_file(file_path)
    content = json.dumps(data, ensure_ascii=False)

    document_id = data.get("document_id") or extract_document_id(file_path, content)
    title = data.get("title") or data.get("document_name") or document_id
    document_type = data.get("document_type") or detect_document_type(file_path)
    summary = data.get("rag_summary") or data.get("description") or extract_summary(content)

    assets, tags = extract_assets_and_tags(content, file_path)

    return {
        "document_id": document_id,
        "title": title,
        "file_name": file_path.name,
        "relative_path": str(file_path.relative_to(RAW_DIR)).replace("\\", "/"),
        "document_type": document_type,
        "source_group": detect_source_group(file_path),
        "asset_ids": ";".join(assets),
        "tags": ";".join(tags),
        "word_count": len(content.split()),
        "character_count": len(content),
        "summary": summary,
        "indexed_at": datetime.now().isoformat(timespec="seconds"),
    }


def build_image_record(file_path):
    document_id = extract_document_id(file_path, "")
    document_type = detect_document_type(file_path)
    assets, tags = extract_assets_and_tags("", file_path)

    return {
        "document_id": document_id,
        "title": document_id,
        "file_name": file_path.name,
        "relative_path": str(file_path.relative_to(RAW_DIR)).replace("\\", "/"),
        "document_type": document_type,
        "source_group": detect_source_group(file_path),
        "asset_ids": ";".join(assets),
        "tags": ";".join(tags),
        "word_count": 0,
        "character_count": 0,
        "summary": "P&ID-style drawing image used for PlantMind AI demo process line.",
        "indexed_at": datetime.now().isoformat(timespec="seconds"),
    }


def collect_document_files():
    files = []

    documents_root = RAW_DIR / "documents"

    allowed_document_extensions = {".md", ".json", ".png"}

    if documents_root.exists():
        for file_path in documents_root.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in allowed_document_extensions:
                files.append(file_path)

    public_sources_root = RAW_DIR / "public_sources"

    if public_sources_root.exists():
        for file_path in public_sources_root.rglob("*"):
            file_name = file_path.name.lower()

            if file_path.is_file() and file_name.startswith("readme") and file_path.suffix.lower() in {".md", ".txt"}:
                files.append(file_path)

    files = sorted(set(files), key=lambda path: str(path).lower())

    return files

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    document_files = collect_document_files()

    for file_path in document_files:
        suffix = file_path.suffix.lower()

        if suffix in [".md", ".txt"]:
            records.append(build_markdown_or_text_record(file_path))

        elif suffix == ".json":
            records.append(build_json_record(file_path))

        elif suffix == ".png":
            records.append(build_image_record(file_path))

    fieldnames = [
        "document_id",
        "title",
        "file_name",
        "relative_path",
        "document_type",
        "source_group",
        "asset_ids",
        "tags",
        "word_count",
        "character_count",
        "summary",
        "indexed_at",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print("PlantMind AI - Documents Index Builder")
    print("=" * 50)
    print(f"Documents indexed: {len(records)}")
    print(f"Output created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()