from __future__ import annotations

import time
from collections import Counter
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from apps.api.security_hardening.policy import security_policy


class SecurityHardeningMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
    ) -> None:
        super().__init__(
            app
        )
        self._request_counts: Counter[tuple[str, str, int]] = Counter()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        content_length = self._content_length(
            request
        )

        if not security_policy.is_upload_allowed(
            content_length
        ):
            return JSONResponse(
                status_code=413,
                content={
                    "detail": "Upload size exceeds configured PlantMind limit.",
                    "max_upload_bytes": security_policy.max_upload_bytes,
                },
            )

        if self._is_rate_limited(
            request
        ):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded.",
                    "rate_limit_per_minute": security_policy.rate_limit_per_minute,
                },
            )

        response = await call_next(
            request
        )

        for header, value in security_policy.security_headers().items():
            response.headers.setdefault(
                header,
                value,
            )

        return response

    def _content_length(
        self,
        request: Request,
    ) -> int | None:
        raw_value = request.headers.get(
            "content-length"
        )

        if raw_value is None:
            return None

        try:
            return int(
                raw_value
            )
        except ValueError:
            return None

    def _is_rate_limited(
        self,
        request: Request,
    ) -> bool:
        client_host = (
            request.client.host
            if request.client
            else "unknown"
        )

        current_window = int(
            time.time() // 60
        )

        key = (
            client_host,
            request.url.path,
            current_window,
        )

        self._request_counts[key] += 1

        self._prune_old_windows(
            current_window
        )

        return (
            self._request_counts[key]
            > security_policy.rate_limit_per_minute
        )

    def _prune_old_windows(
        self,
        current_window: int,
    ) -> None:
        stale_keys = [
            key
            for key in self._request_counts
            if key[2] < current_window - 1
        ]

        for key in stale_keys:
            del self._request_counts[key]