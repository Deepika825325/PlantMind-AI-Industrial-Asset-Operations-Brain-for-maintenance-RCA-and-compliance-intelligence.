from dataclasses import dataclass
from typing import Any


@dataclass(
    slots=True
)
class ApiError(Exception):
    status_code: int
    code: str
    message: str
    details: (
        dict[str, Any]
        | list[Any]
        | None
    ) = None

    def __str__(self) -> str:
        return self.message


def build_error_payload(
    code: str,
    message: str,
    request_id: str,
    details: (
        dict[str, Any]
        | list[Any]
        | None
    ) = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
            "details": details,
        }
    }
