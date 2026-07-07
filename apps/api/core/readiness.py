from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import csv
import json


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

DEMO_DIR = (
    PROJECT_ROOT
    / "data"
    / "demo"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

REQUIRED_DEMO_FILES = [
    "assets.json",
    "compliance_matrix.json",
    "compliance_rules.json",
    "dashboard_summary.json",
    "demo_answers.json",
    "documents.json",
    "health_scores.json",
    "knowledge_graph.json",
    "maintenance_events.json",
    "maintenance_work_orders.json",
    "pid_view.json",
    "rag_seed_questions.json",
    "rca_cases.json",
]

REQUIRED_PROCESSED_FILES = [
    "asset_metadata.json",
    "benchmark_questions.json",
    "compliance_matrix.json",
    "document_chunks.json",
    "documents_index.csv",
    "knowledge_graph_seed.json",
    "sensor_summary.json",
    "work_orders_processed.json",
]


def validate_json_file(
    path: Path,
) -> tuple[bool, str | None]:
    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
        ) as file:
            json.load(file)
    except json.JSONDecodeError as error:
        return (
            False,
            (
                "Invalid JSON at line "
                f"{error.lineno}, column "
                f"{error.colno}: {error.msg}"
            ),
        )
    except OSError as error:
        return (
            False,
            str(error),
        )

    return (
        True,
        None,
    )


def validate_csv_file(
    path: Path,
) -> tuple[bool, str | None]:
    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.reader(file)
            header = next(
                reader,
                None,
            )
    except OSError as error:
        return (
            False,
            str(error),
        )

    if not header:
        return (
            False,
            "CSV header is missing.",
        )

    if not any(
        str(column).strip()
        for column in header
    ):
        return (
            False,
            "CSV header is empty.",
        )

    return (
        True,
        None,
    )


def validate_required_file(
    path: Path,
) -> dict[str, Any]:
    relative_path = str(
        path.relative_to(
            PROJECT_ROOT
        )
    )

    if not path.exists():
        return {
            "path": relative_path,
            "status": "missing",
            "size_bytes": 0,
            "error": "Required file does not exist.",
        }

    if not path.is_file():
        return {
            "path": relative_path,
            "status": "invalid",
            "size_bytes": 0,
            "error": "Required path is not a file.",
        }

    size_bytes = path.stat().st_size

    if size_bytes == 0:
        return {
            "path": relative_path,
            "status": "invalid",
            "size_bytes": 0,
            "error": "Required file is empty.",
        }

    suffix = path.suffix.lower()

    if suffix == ".json":
        valid, error = validate_json_file(
            path
        )
    elif suffix == ".csv":
        valid, error = validate_csv_file(
            path
        )
    else:
        valid = True
        error = None

    return {
        "path": relative_path,
        "status": (
            "valid"
            if valid
            else "invalid"
        ),
        "size_bytes": size_bytes,
        "error": error,
    }


def validate_data_files() -> dict[str, Any]:
    required_paths = [
        *[
            DEMO_DIR / file_name
            for file_name
            in REQUIRED_DEMO_FILES
        ],
        *[
            PROCESSED_DIR / file_name
            for file_name
            in REQUIRED_PROCESSED_FILES
        ],
    ]

    files = [
        validate_required_file(
            path
        )
        for path in required_paths
    ]

    valid_files = [
        file
        for file in files
        if file["status"] == "valid"
    ]

    missing_files = [
        file
        for file in files
        if file["status"] == "missing"
    ]

    invalid_files = [
        file
        for file in files
        if file["status"] == "invalid"
    ]

    issues = [
        {
            "path": file["path"],
            "code": (
                "DATA_FILE_MISSING"
                if file["status"]
                == "missing"
                else "DATA_FILE_INVALID"
            ),
            "message": file["error"],
        }
        for file in files
        if file["status"]
        in {
            "missing",
            "invalid",
        }
    ]

    ready = not issues

    return {
        "status": (
            "ready"
            if ready
            else "not_ready"
        ),
        "ready": ready,
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "required_file_count": len(
            files
        ),
        "valid_file_count": len(
            valid_files
        ),
        "missing_file_count": len(
            missing_files
        ),
        "invalid_file_count": len(
            invalid_files
        ),
        "issues": issues,
        "files": files,
    }


def assert_data_ready() -> dict[str, Any]:
    result = validate_data_files()

    if not result["ready"]:
        issue_summary = "; ".join(
            (
                f'{issue["path"]}: '
                f'{issue["message"]}'
            )
            for issue in result["issues"]
        )

        raise RuntimeError(
            "PlantMind startup validation "
            f"failed: {issue_summary}"
        )

    return result
