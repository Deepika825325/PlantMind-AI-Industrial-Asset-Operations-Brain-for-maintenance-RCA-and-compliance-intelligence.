from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


DataMode = Literal[
    "demo",
    "postgres",
]


@dataclass(frozen=True, slots=True)
class Settings:
    data_mode: DataMode


def get_settings() -> Settings:
    """Read and normalize PlantMind runtime settings."""

    raw_mode = os.getenv(
        "PLANTMIND_DATA_BACKEND",
        "json",
    ).strip().lower()

    if raw_mode in {
        "json",
        "demo",
    }:
        data_mode: DataMode = "demo"
    elif raw_mode in {
        "postgres",
        "postgresql",
        "database",
        "db",
    }:
        data_mode = "postgres"
    else:
        raise RuntimeError(
            "Unsupported PLANTMIND_DATA_BACKEND: "
            f"{raw_mode!r}. Expected json/demo "
            "or postgres/database."
        )

    return Settings(
        data_mode=data_mode,
    )