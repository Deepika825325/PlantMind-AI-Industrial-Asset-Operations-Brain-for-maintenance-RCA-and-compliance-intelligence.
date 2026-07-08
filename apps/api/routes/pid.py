from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from apps.api.repositories.registry import (
    get_repository_registry,
)


router = APIRouter(
    prefix="/pid",
    tags=["P&ID"],
)


@router.get("/{pid_id}")
def get_pid(pid_id: str):
    normalized_pid_id = pid_id.upper()

    if normalized_pid_id != "PID-001":
        raise HTTPException(
            status_code=404,
            detail=f"P&ID not found: {pid_id}",
        )

    repositories = get_repository_registry()
    pid_view = repositories.pid.get_view(
        normalized_pid_id
    )

    if pid_view is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "P&ID visualization data file "
                "was not found"
            ),
        )

    return pid_view


@router.get("/{pid_id}/image")
def get_pid_image(pid_id: str):
    normalized_pid_id = pid_id.upper()

    if normalized_pid_id != "PID-001":
        raise HTTPException(
            status_code=404,
            detail=f"P&ID image not found: {pid_id}",
        )

    repositories = get_repository_registry()
    image_path = repositories.pid.get_image_path(
        normalized_pid_id
    )

    if image_path is None:
        raise HTTPException(
            status_code=404,
            detail="P&ID image file was not found",
        )

    return FileResponse(
        path=image_path,
        media_type="image/png",
        filename=image_path.name,
    )