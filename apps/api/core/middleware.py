from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.responses import Response

from apps.api.core.logging import (
    get_logger,
)
from apps.api.core.request_context import (
    reset_request_id,
    set_request_id,
)


logger = get_logger(__name__)


class RequestContextMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        request_id = (
            request.headers.get(
                "x-request-id",
                "",
            ).strip()
            or str(uuid4())
        )

        request.state.request_id = (
            request_id
        )

        token = set_request_id(
            request_id
        )

        started_at = perf_counter()

        try:
            response = await call_next(
                request
            )

            duration_ms = round(
                (
                    perf_counter()
                    - started_at
                )
                * 1000,
                2,
            )

            response.headers[
                "X-Request-ID"
            ] = request_id

            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": (
                        response.status_code
                    ),
                    "duration_ms": (
                        duration_ms
                    ),
                },
            )

            return response
        except Exception:
            duration_ms = round(
                (
                    perf_counter()
                    - started_at
                )
                * 1000,
                2,
            )

            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": (
                        duration_ms
                    ),
                },
            )

            raise
        finally:
            reset_request_id(
                token
            )
