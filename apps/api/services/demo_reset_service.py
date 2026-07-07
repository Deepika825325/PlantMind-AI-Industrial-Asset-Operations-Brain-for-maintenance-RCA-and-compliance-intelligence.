from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import shutil

from apps.api.core.readiness import (
    validate_data_files,
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


def validate_seed_files() -> list[
    dict[str, Any]
]:
    results: list[
        dict[str, Any]
    ] = []

    for file_name in RESET_FILE_NAMES:
        path = (
            SEED_DIR
            / file_name
        )

        if not path.exists():
            raise FileNotFoundError(
                "Required reset seed "
                f"does not exist: {path}"
            )

        if not path.is_file():
            raise RuntimeError(
                "Reset seed path is not "
                f"a file: {path}"
            )

        if path.stat().st_size == 0:
            raise RuntimeError(
                "Reset seed file is "
                f"empty: {path}"
            )

        payload = load_json_file(
            path
        )

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Reset seed must contain "
                f"a JSON object: {path}"
            )

        results.append(
            {
                "path": relative_path(
                    path
                ),
                "size_bytes": (
                    path.stat().st_size
                ),
                "status": "valid",
            }
        )

    return results


def restore_seed_file(
    file_name: str,
) -> dict[str, Any]:
    source = (
        SEED_DIR
        / file_name
    )

    destination = (
        DEMO_DIR
        / file_name
    )

    temporary_path = (
        destination.parent
        / (
            f".{destination.name}"
            ".reset.tmp"
        )
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
        "source": relative_path(
            source
        ),
        "destination": relative_path(
            destination
        ),
        "size_bytes": (
            destination.stat().st_size
        ),
        "status": "restored",
    }


def clear_directory_contents(
    directory: Path,
) -> dict[str, Any]:
    removed_files = 0
    removed_directories = 0

    if not directory.exists():
        return {
            "path": relative_path(
                directory
            ),
            "existed": False,
            "removed_files": 0,
            "removed_directories": 0,
        }

    if not directory.is_dir():
        raise RuntimeError(
            "Temporary upload path is "
            f"not a directory: {directory}"
        )

    for child in list(
        directory.iterdir()
    ):
        if (
            child.is_symlink()
            or child.is_file()
        ):
            child.unlink()
            removed_files += 1
            continue

        if child.is_dir():
            removed_files += sum(
                1
                for nested in child.rglob(
                    "*"
                )
                if (
                    nested.is_file()
                    or nested.is_symlink()
                )
            )

            shutil.rmtree(
                child
            )

            removed_directories += 1

    return {
        "path": relative_path(
            directory
        ),
        "existed": True,
        "removed_files": (
            removed_files
        ),
        "removed_directories": (
            removed_directories
        ),
    }


def reset_demo_state() -> dict[str, Any]:
    seed_validation = (
        validate_seed_files()
    )

    restored_files = [
        restore_seed_file(
            file_name
        )
        for file_name
        in RESET_FILE_NAMES
    ]

    temporary_cleanup = [
        clear_directory_contents(
            directory
        )
        for directory
        in TEMPORARY_UPLOAD_DIRECTORIES
    ]

    clear_data_cache()

    readiness = validate_data_files()

    if not readiness["ready"]:
        raise RuntimeError(
            "Demo reset completed, but "
            "data readiness validation "
            "failed."
        )

    return {
        "status": "demo_reset",
        "message": (
            "PlantMind demo state was "
            "restored successfully."
        ),
        "reset_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed_validation": (
            seed_validation
        ),
        "restored_files": (
            restored_files
        ),
        "temporary_cleanup": (
            temporary_cleanup
        ),
        "cache_cleared": True,
        "readiness": {
            "status": readiness[
                "status"
            ],
            "ready": readiness[
                "ready"
            ],
            "required_file_count": (
                readiness[
                    "required_file_count"
                ]
            ),
            "valid_file_count": (
                readiness[
                    "valid_file_count"
                ]
            ),
            "missing_file_count": (
                readiness[
                    "missing_file_count"
                ]
            ),
            "invalid_file_count": (
                readiness[
                    "invalid_file_count"
                ]
            ),
        },
    }
