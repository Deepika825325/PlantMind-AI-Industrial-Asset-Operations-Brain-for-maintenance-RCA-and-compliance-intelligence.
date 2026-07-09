from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import hashlib
import json
import os
import shutil
import socket

from apps.api.core.readiness import (
    validate_data_files,
)
from apps.api.core.settings import (
    get_settings,
)
from apps.api.db.seed.seed_demo_data import (
    seed_demo_database_from_url,
)
from apps.api.db.session import (
    clear_database_runtime_cache,
)
from apps.api.repositories.registry import (
    get_repository_registry,
)
from apps.api.services.data_loader import (
    clear_data_cache,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

DEMO_DIR = (
    PROJECT_ROOT
    / "data"
    / "demo"
)

SEED_DIR = (
    PROJECT_ROOT
    / "data"
    / "seed"
)

RESET_FILE_NAMES = (
    "maintenance_work_orders.json",
    "compliance_matrix.json",
    "rca_cases.json",
)

TEMPORARY_UPLOAD_DIRECTORIES = (
    PROJECT_ROOT
    / "data"
    / "uploads",
    PROJECT_ROOT
    / "data"
    / "temp",
    PROJECT_ROOT
    / "data"
    / "tmp",
    PROJECT_ROOT
    / "runtime"
    / "uploads",
    PROJECT_ROOT
    / "runtime"
    / "temp",
)


def load_json_file(
    path: Path,
) -> Any:
    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        return json.load(file)


def relative_path(
    path: Path,
) -> str:
    return str(
        path.relative_to(
            PROJECT_ROOT
        )
    )


def validate_seed_files() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for file_name in RESET_FILE_NAMES:
        path = SEED_DIR / file_name

        if not path.exists():
            raise FileNotFoundError(
                "Required reset seed does not exist: "
                f"{path}"
            )

        if not path.is_file():
            raise RuntimeError(
                "Reset seed path is not a file: "
                f"{path}"
            )

        if path.stat().st_size == 0:
            raise RuntimeError(
                "Reset seed file is empty: "
                f"{path}"
            )

        payload = load_json_file(path)

        if not isinstance(payload, dict):
            raise RuntimeError(
                "Reset seed must contain a JSON object: "
                f"{path}"
            )

        results.append(
            {
                "path": relative_path(path),
                "size_bytes": path.stat().st_size,
                "status": "valid",
            }
        )

    return results


def restore_seed_file(
    file_name: str,
) -> dict[str, Any]:
    source = SEED_DIR / file_name
    destination = DEMO_DIR / file_name

    temporary_path = (
        destination.parent
        / f".{destination.name}.reset.tmp"
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        temporary_path.write_bytes(
            source.read_bytes()
        )

        load_json_file(
            temporary_path
        )

        os.replace(
            temporary_path,
            destination,
        )
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return {
        "source": relative_path(source),
        "destination": relative_path(destination),
        "size_bytes": destination.stat().st_size,
        "status": "restored",
    }


def clear_directory_contents(
    directory: Path,
) -> dict[str, Any]:
    removed_files = 0
    removed_directories = 0

    if not directory.exists():
        return {
            "path": relative_path(directory),
            "existed": False,
            "removed_files": 0,
            "removed_directories": 0,
        }

    if not directory.is_dir():
        raise RuntimeError(
            "Temporary upload path is not a directory: "
            f"{directory}"
        )

    for child in list(directory.iterdir()):
        if child.is_symlink() or child.is_file():
            child.unlink()
            removed_files += 1
            continue

        if child.is_dir():
            removed_files += sum(
                1
                for nested in child.rglob("*")
                if nested.is_file()
                or nested.is_symlink()
            )

            shutil.rmtree(child)
            removed_directories += 1

    return {
        "path": relative_path(directory),
        "existed": True,
        "removed_files": removed_files,
        "removed_directories": removed_directories,
    }


def build_reset_signature(
    payload: dict[str, Any],
) -> str:
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def reset_json_demo_state() -> dict[str, Any]:
    seed_validation = validate_seed_files()

    restored_files = [
        restore_seed_file(file_name)
        for file_name in RESET_FILE_NAMES
    ]

    temporary_cleanup = [
        clear_directory_contents(directory)
        for directory in TEMPORARY_UPLOAD_DIRECTORIES
    ]

    clear_data_cache()

    readiness = validate_data_files()

    if not readiness["ready"]:
        raise RuntimeError(
            "Demo reset completed, but data readiness "
            "validation failed."
        )

    return {
        "status": "demo_reset",
        "data_mode": "demo",
        "message": (
            "PlantMind demo state was restored "
            "successfully."
        ),
        "reset_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed_validation": seed_validation,
        "restored_files": restored_files,
        "temporary_cleanup": temporary_cleanup,
        "cache_cleared": True,
        "readiness": {
            "status": readiness["status"],
            "ready": readiness["ready"],
            "required_file_count": readiness[
                "required_file_count"
            ],
            "valid_file_count": readiness[
                "valid_file_count"
            ],
            "missing_file_count": readiness[
                "missing_file_count"
            ],
            "invalid_file_count": readiness[
                "invalid_file_count"
            ],
        },
    }


def clear_optional_redis_cache() -> dict[str, Any]:
    redis_url = (
        os.getenv("REDIS_URL")
        or os.getenv("PLANTMIND_REDIS_URL")
    )

    if not redis_url:
        return {
            "status": "skipped",
            "reason": "REDIS_URL is not configured",
        }

    parsed = urlparse(redis_url)

    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    database = (
        parsed.path.strip("/")
        if parsed.path
        else "0"
    ) or "0"
    password = parsed.password

    def encode_command(
        *parts: str,
    ) -> bytes:
        command = [
            f"*{len(parts)}\r\n".encode("utf-8")
        ]

        for part in parts:
            encoded = part.encode("utf-8")
            command.append(
                f"${len(encoded)}\r\n".encode("utf-8")
            )
            command.append(encoded)
            command.append(b"\r\n")

        return b"".join(command)

    def expect_ok(
        response: bytes,
        action: str,
    ) -> None:
        if not (
            response.startswith(b"+OK")
            or response.startswith(b"+PONG")
        ):
            raise RuntimeError(
                f"Redis {action} failed: "
                f"{response.decode('utf-8', errors='replace')}"
            )

    try:
        with socket.create_connection(
            (host, port),
            timeout=3,
        ) as sock:
            if password:
                sock.sendall(
                    encode_command(
                        "AUTH",
                        password,
                    )
                )
                expect_ok(
                    sock.recv(1024),
                    "AUTH",
                )

            if database != "0":
                sock.sendall(
                    encode_command(
                        "SELECT",
                        database,
                    )
                )
                expect_ok(
                    sock.recv(1024),
                    "SELECT",
                )

            sock.sendall(
                encode_command("FLUSHDB")
            )
            expect_ok(
                sock.recv(1024),
                "FLUSHDB",
            )
    except OSError as error:
        return {
            "status": "failed",
            "reason": str(error),
            "host": host,
            "port": port,
            "database": database,
        }

    return {
        "status": "cleared",
        "host": host,
        "port": port,
        "database": database,
    }


def validate_database_relationships() -> dict[str, Any]:
    get_repository_registry.cache_clear()

    repositories = get_repository_registry()

    assets = repositories.assets.list_assets()
    documents = repositories.documents.list_documents()
    chunks = repositories.documents.list_document_chunks()
    work_orders = repositories.work_orders.list_work_orders()
    rca_cases = repositories.rca.list_cases()
    compliance_rules = (
        repositories.compliance
        .get_rules()
        .get("rules", [])
    )

    asset_ids = {
        str(asset.get("asset_id"))
        for asset in assets
        if asset.get("asset_id")
    }

    document_ids = {
        str(document.get("document_id"))
        for document in documents
        if document.get("document_id")
    }

    rca_case_ids = {
        str(case.get("case_id"))
        for case in rca_cases
        if case.get("case_id")
    }

    root_cause_ids = {
        str(root_cause.get("cause_id"))
        for case in rca_cases
        for root_cause in case.get("root_causes", [])
        if root_cause.get("cause_id")
    }

    evidence_ids = {
        str(evidence.get("evidence_id"))
        for case in rca_cases
        for evidence in case.get("evidence", [])
        if evidence.get("evidence_id")
    }

    issues: list[str] = []

    orphan_work_orders = [
        str(work_order.get("work_order_id"))
        for work_order in work_orders
        if str(work_order.get("asset_id")) not in asset_ids
    ]

    if orphan_work_orders:
        issues.append(
            "Work orders reference missing assets: "
            + ", ".join(orphan_work_orders)
        )

    orphan_rca_cases = [
        str(case.get("case_id"))
        for case in rca_cases
        if str(case.get("asset_id")) not in asset_ids
    ]

    if orphan_rca_cases:
        issues.append(
            "RCA cases reference missing assets: "
            + ", ".join(orphan_rca_cases)
        )

    orphan_rca_links = [
        str(work_order.get("work_order_id"))
        for work_order in work_orders
        if work_order.get("linked_rca_case_id")
        and str(work_order.get("linked_rca_case_id"))
        not in rca_case_ids
    ]

    if orphan_rca_links:
        issues.append(
            "Work orders reference missing RCA cases: "
            + ", ".join(orphan_rca_links)
        )

    orphan_evidence_links = [
        str(work_order.get("work_order_id"))
        for work_order in work_orders
        if work_order.get("linked_rca_case_id")
        for evidence_id in work_order.get(
            "linked_evidence_ids",
            [],
        )
        if str(evidence_id) not in evidence_ids
    ]

    if orphan_evidence_links:
        issues.append(
            "RCA-linked work orders reference missing "
            "RCA evidence: "
            + ", ".join(
                sorted(set(orphan_evidence_links))
            )
        )

    orphan_root_cause_links = [
        str(work_order.get("work_order_id"))
        for work_order in work_orders
        if work_order.get("linked_rca_case_id")
        for root_cause_id in work_order.get(
            "linked_root_cause_ids",
            [],
        )
        if str(root_cause_id) not in root_cause_ids
    ]

    if orphan_root_cause_links:
        issues.append(
            "RCA-linked work orders reference missing "
            "root causes: "
            + ", ".join(
                sorted(set(orphan_root_cause_links))
            )
        )

    chunk_document_issues = [
        str(chunk.get("chunk_id"))
        for chunk in chunks
        if str(chunk.get("document_id")) not in document_ids
    ]

    if chunk_document_issues:
        issues.append(
            "Document chunks reference missing documents: "
            + ", ".join(chunk_document_issues[:10])
        )

    p101_cases = [
        case
        for case in rca_cases
        if case.get("case_id") == "RCA-P101-001"
    ]

    p101_case = (
        p101_cases[0]
        if p101_cases
        else {}
    )

    p101_work_orders = [
        work_order
        for work_order in work_orders
        if work_order.get("linked_rca_case_id")
        == "RCA-P101-001"
    ]

    counts = {
        "assets": len(assets),
        "documents": len(documents),
        "document_chunks": len(chunks),
        "rca_cases": len(rca_cases),
        "root_causes_for_p101": len(
            p101_case.get("root_causes", [])
        ),
        "evidence_for_p101": len(
            p101_case.get("evidence", [])
        ),
        "rca_linked_work_orders_for_p101": len(
            p101_work_orders
        ),
        "work_orders": len(work_orders),
        "compliance_rules": len(compliance_rules),
    }

    expected_counts = {
        "assets": 3,
        "documents": 19,
        "document_chunks": 163,
        "rca_cases": 1,
        "root_causes_for_p101": 3,
        "evidence_for_p101": 4,
        "rca_linked_work_orders_for_p101": 4,
        "work_orders": 9,
        "compliance_rules": 8,
    }

    for key, expected_value in expected_counts.items():
        actual_value = counts.get(key)

        if actual_value != expected_value:
            issues.append(
                f"{key} expected {expected_value}, "
                f"got {actual_value}"
            )

    signature_payload = {
        "counts": counts,
        "expected_counts": expected_counts,
        "issues": issues,
    }

    return {
        "status": (
            "valid"
            if not issues
            else "invalid"
        ),
        "counts": counts,
        "expected_counts": expected_counts,
        "issues": issues,
        "signature": build_reset_signature(
            signature_payload
        ),
    }


def reset_database_demo_state() -> dict[str, Any]:
    seed_counts = seed_demo_database_from_url()

    clear_database_runtime_cache()
    get_repository_registry.cache_clear()

    relationship_validation = (
        validate_database_relationships()
    )

    if relationship_validation["status"] != "valid":
        raise RuntimeError(
            "Database reset completed, but relationship "
            "validation failed: "
            + "; ".join(
                relationship_validation["issues"]
            )
        )

    temporary_cleanup = [
        clear_directory_contents(directory)
        for directory in TEMPORARY_UPLOAD_DIRECTORIES
    ]

    redis_cleanup = clear_optional_redis_cache()

    clear_data_cache()
    clear_database_runtime_cache()
    get_repository_registry.cache_clear()

    reset_payload = {
        "seed_counts": seed_counts,
        "relationship_validation": (
            relationship_validation
        ),
        "redis_cleanup": redis_cleanup,
    }

    return {
        "status": "database_demo_reset",
        "data_mode": "postgres",
        "message": (
            "PlantMind PostgreSQL demo state was "
            "restored successfully."
        ),
        "reset_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed_counts": seed_counts,
        "relationship_validation": (
            relationship_validation
        ),
        "temporary_cleanup": temporary_cleanup,
        "redis_cleanup": redis_cleanup,
        "cache_cleared": True,
        "reset_signature": build_reset_signature(
            reset_payload
        ),
    }


def reset_demo_state() -> dict[str, Any]:
    settings = get_settings()

    if settings.data_mode == "postgres":
        return reset_database_demo_state()

    return reset_json_demo_state()
