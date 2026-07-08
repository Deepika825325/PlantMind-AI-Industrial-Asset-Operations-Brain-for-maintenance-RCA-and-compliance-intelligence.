from __future__ import annotations

from pathlib import Path
from typing import Any

from apps.api.repositories.json.data_source import (
    DataFileNotFoundError,
    load_demo_json,
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

PID_IMAGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "documents"
    / "drawings"
    / "PID-001_Demo_Process_Line.png"
)


class JsonPidRepository:
    """JSON-backed repository for P&ID views and image files."""

    def get_view(
        self,
        pid_id: str,
    ) -> dict[str, Any] | None:
        if pid_id.upper() != "PID-001":
            return None

        try:
            return load_demo_json("pid_view.json")
        except DataFileNotFoundError:
            return None

    def get_image_path(
        self,
        pid_id: str,
    ) -> Path | None:
        if pid_id.upper() != "PID-001":
            return None

        if (
            not PID_IMAGE_PATH.exists()
            or not PID_IMAGE_PATH.is_file()
        ):
            return None

        return PID_IMAGE_PATH