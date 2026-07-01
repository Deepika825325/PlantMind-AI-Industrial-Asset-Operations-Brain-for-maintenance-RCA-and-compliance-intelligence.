from functools import lru_cache
from pathlib import Path
import csv
import json
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DEMO_DIR = DATA_DIR / "demo"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"


class DataFileNotFoundError(FileNotFoundError):
    pass


def read_json_file(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        raise DataFileNotFoundError(f"File not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    if not file_path.exists():
        raise DataFileNotFoundError(f"File not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


@lru_cache(maxsize=64)
def load_demo_json(file_name: str) -> Dict[str, Any]:
    return read_json_file(DEMO_DIR / file_name)


@lru_cache(maxsize=64)
def load_processed_json(file_name: str) -> Dict[str, Any]:
    return read_json_file(PROCESSED_DIR / file_name)


@lru_cache(maxsize=32)
def load_processed_csv(file_name: str) -> List[Dict[str, Any]]:
    return read_csv_file(PROCESSED_DIR / file_name)


def clear_data_cache() -> None:
    load_demo_json.cache_clear()
    load_processed_json.cache_clear()
    load_processed_csv.cache_clear()


def get_assets() -> List[Dict[str, Any]]:
    data = load_demo_json("assets.json")
    return data.get("assets", [])


def get_asset_by_id(asset_id: str) -> Dict[str, Any] | None:
    asset_id = asset_id.upper()

    for asset in get_assets():
        if asset.get("asset_id") == asset_id:
            return asset

    return None


def get_documents() -> List[Dict[str, Any]]:
    data = load_demo_json("documents.json")
    return data.get("documents", [])


def get_document_by_id(document_id: str) -> Dict[str, Any] | None:
    for document in get_documents():
        if document.get("document_id") == document_id:
            return document

    return None


def get_document_chunks() -> List[Dict[str, Any]]:
    data = load_processed_json("document_chunks.json")
    return data.get("chunks", [])


def get_chunks_by_document_id(document_id: str) -> List[Dict[str, Any]]:
    chunks = get_document_chunks()

    return [
        chunk for chunk in chunks
        if chunk.get("document_id") == document_id
    ]


def get_compliance_matrix() -> Dict[str, Any]:
    return load_demo_json("compliance_matrix.json")


def get_maintenance_events() -> List[Dict[str, Any]]:
    data = load_demo_json("maintenance_events.json")
    return data.get("events", [])


def get_knowledge_graph() -> Dict[str, Any]:
    return load_demo_json("knowledge_graph.json")


def get_dashboard_summary() -> Dict[str, Any]:
    return load_demo_json("dashboard_summary.json")


def get_health_scores() -> List[Dict[str, Any]]:
    data = load_demo_json("health_scores.json")
    return data.get("health_scores", [])


def get_demo_answers() -> List[Dict[str, Any]]:
    data = load_demo_json("demo_answers.json")
    return data.get("answers", [])


def get_rag_seed_questions() -> List[Dict[str, Any]]:
    data = load_demo_json("rag_seed_questions.json")
    return data.get("questions", [])


def get_file_status() -> Dict[str, Any]:
    demo_files = sorted([file.name for file in DEMO_DIR.glob("*.json")])
    processed_files = sorted([file.name for file in PROCESSED_DIR.glob("*") if file.is_file()])

    return {
        "project_root": str(PROJECT_ROOT),
        "demo_dir": str(DEMO_DIR),
        "processed_dir": str(PROCESSED_DIR),
        "demo_files": demo_files,
        "processed_files": processed_files,
        "demo_file_count": len(demo_files),
        "processed_file_count": len(processed_files),
    }