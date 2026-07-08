from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / "data"
DEMO_DIR = DATA_DIR / "demo"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"


class DataFileNotFoundError(FileNotFoundError):
    """Raised when a required PlantMind data file is unavailable."""


def read_json_file(
    file_path: Path,
    *,
    encoding: str = "utf-8",
) -> dict[str, Any]:
    if not file_path.exists():
        raise DataFileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding=encoding,
    ) as file:
        return json.load(file)


def read_csv_file(
    file_path: Path,
) -> list[dict[str, Any]]:
    if not file_path.exists():
        raise DataFileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        return list(reader)


@lru_cache(maxsize=64)
def load_demo_json(
    file_name: str,
) -> dict[str, Any]:
    return read_json_file(
        DEMO_DIR / file_name
    )


@lru_cache(maxsize=64)
def load_processed_json(
    file_name: str,
) -> dict[str, Any]:
    return read_json_file(
        PROCESSED_DIR / file_name
    )


@lru_cache(maxsize=32)
def load_processed_csv(
    file_name: str,
) -> list[dict[str, Any]]:
    return read_csv_file(
        PROCESSED_DIR / file_name
    )


def clear_json_data_cache() -> None:
    load_demo_json.cache_clear()
    load_processed_json.cache_clear()
    load_processed_csv.cache_clear()