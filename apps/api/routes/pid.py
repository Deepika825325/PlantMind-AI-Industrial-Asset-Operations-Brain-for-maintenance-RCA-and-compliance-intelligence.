import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(prefix="/pid", tags=["P&ID"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PID_DATA_PATH = PROJECT_ROOT / "data" / "demo" / "pid_view.json"

PID_IMAGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "documents"
    / "drawings"
    / "PID-001_Demo_Process_Line.png"
)


@router.get("/{pid_id}")
def get_pid(pid_id: str):
    normalized_pid_id = pid_id.upper()

    if normalized_pid_id != "PID-001":
        raise HTTPException(
            status_code=404,
            detail=f"P&ID not found: {pid_id}"
        )

    if not PID_DATA_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="P&ID visualization data file was not found"
        )

    with PID_DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


@router.get("/{pid_id}/image")
def get_pid_image(pid_id: str):
    normalized_pid_id = pid_id.upper()

    if normalized_pid_id != "PID-001":
        raise HTTPException(
            status_code=404,
            detail=f"P&ID image not found: {pid_id}"
        )

    if not PID_IMAGE_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="P&ID image file was not found"
        )

    return FileResponse(
        path=PID_IMAGE_PATH,
        media_type="image/png",
        filename="PID-001_Demo_Process_Line.png"
    )