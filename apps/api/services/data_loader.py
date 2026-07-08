from __future__ import annotations

from typing import Any

from apps.api.repositories.json.data_source import (
    DATA_DIR,
    DEMO_DIR,
    PROCESSED_DIR,
    PROJECT_ROOT,
    RAW_DIR,
    DataFileNotFoundError,
    clear_json_data_cache,
    load_demo_json,
    load_processed_csv,
    load_processed_json,
    read_csv_file,
    read_json_file,
)
from apps.api.repositories.registry import (
    get_repository_registry,
)


def clear_data_cache() -> None:
    clear_json_data_cache()
    get_repository_registry.cache_clear()


def get_assets() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.assets.list_assets()


def get_asset_by_id(
    asset_id: str,
) -> dict[str, Any] | None:
    repositories = get_repository_registry()
    return repositories.assets.get_asset_by_id(
        asset_id
    )


def get_documents() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.documents.list_documents()


def get_document_by_id(
    document_id: str,
) -> dict[str, Any] | None:
    repositories = get_repository_registry()
    return repositories.documents.get_document_by_id(
        document_id
    )


def get_document_chunks() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.documents.list_document_chunks()


def get_chunks_by_document_id(
    document_id: str,
) -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return (
        repositories.documents
        .list_chunks_by_document_id(document_id)
    )


def get_compliance_matrix() -> dict[str, Any]:
    repositories = get_repository_registry()
    return repositories.compliance.get_matrix()


def get_maintenance_events() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.work_orders.list_maintenance_events()


def get_knowledge_graph() -> dict[str, Any]:
    return load_demo_json(
        "knowledge_graph.json"
    )


def get_dashboard_summary() -> dict[str, Any]:
    return load_demo_json(
        "dashboard_summary.json"
    )


def get_health_scores() -> list[dict[str, Any]]:
    repositories = get_repository_registry()
    return repositories.assets.list_health_scores()


def get_demo_answers() -> list[dict[str, Any]]:
    data = load_demo_json(
        "demo_answers.json"
    )
    return data.get("answers", [])


def get_rag_seed_questions() -> list[dict[str, Any]]:
    data = load_demo_json(
        "rag_seed_questions.json"
    )
    return data.get("questions", [])


def get_file_status() -> dict[str, Any]:
    demo_files = sorted(
        file.name
        for file in DEMO_DIR.glob("*.json")
    )

    processed_files = sorted(
        file.name
        for file in PROCESSED_DIR.glob("*")
        if file.is_file()
    )

    return {
        "project_root": str(PROJECT_ROOT),
        "demo_dir": str(DEMO_DIR),
        "processed_dir": str(PROCESSED_DIR),
        "demo_files": demo_files,
        "processed_files": processed_files,
        "demo_file_count": len(demo_files),
        "processed_file_count": len(
            processed_files
        ),
    }