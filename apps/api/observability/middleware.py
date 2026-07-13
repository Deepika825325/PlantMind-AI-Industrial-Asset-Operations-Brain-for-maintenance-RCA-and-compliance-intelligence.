from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from apps.api.observability.metrics import Timer, metrics_store


class PrometheusObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        timer = Timer()
        status_code = 500

        try:
            response = await call_next(
                request
            )
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            metrics_store.record_request(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                latency_ms=timer.elapsed_ms(),
            )