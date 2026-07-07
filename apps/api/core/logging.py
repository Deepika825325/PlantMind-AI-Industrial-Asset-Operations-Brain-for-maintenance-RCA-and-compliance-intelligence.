from datetime import datetime, timezone
import json
import logging
import os
import sys
from typing import Any

from apps.api.core.request_context import (
    get_request_id,
)


class JsonLogFormatter(
    logging.Formatter
):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(
            record,
            "request_id",
            None,
        ) or get_request_id()

        if request_id:
            payload["request_id"] = (
                request_id
            )

        optional_fields = [
            "method",
            "path",
            "status_code",
            "duration_ms",
            "error_code",
        ]

        for field in optional_fields:
            value = getattr(
                record,
                field,
                None,
            )

            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = (
                self.formatException(
                    record.exc_info
                )
            )

        return json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )


def configure_logging() -> None:
    root_logger = logging.getLogger()

    if getattr(
        root_logger,
        "_plantmind_configured",
        False,
    ):
        return

    level_name = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    level = getattr(
        logging,
        level_name,
        logging.INFO,
    )

    handler = logging.StreamHandler(
        sys.stdout
    )

    handler.setFormatter(
        JsonLogFormatter()
    )

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    setattr(
        root_logger,
        "_plantmind_configured",
        True,
    )


def get_logger(
    name: str,
) -> logging.Logger:
    return logging.getLogger(name)
