from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from apps.api.core.errors import (
    ApiError,
    build_error_payload,
)
from apps.api.core.logging import get_logger


logger = get_logger(__name__)


def get_request_id(
    request: Request,
) -> str:
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    if request_id:
        return str(request_id)

    header_request_id = (
        request.headers.get(
            "x-request-id",
            "",
        ).strip()
    )

    if header_request_id:
        return header_request_id

    return str(uuid4())


async def api_error_handler(
    request: Request,
    error: ApiError,
) -> JSONResponse:
    request_id = get_request_id(
        request
    )

    logger.warning(
        "api_error",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": error.status_code,
            "error_code": error.code,
        },
    )

    return JSONResponse(
        status_code=error.status_code,
        content=jsonable_encoder(
            build_error_payload(
                code=error.code,
                message=error.message,
                request_id=request_id,
                details=error.details,
            )
        ),
        headers={
            "X-Request-ID": request_id,
        },
    )


async def http_exception_handler(
    request: Request,
    error: StarletteHTTPException,
) -> JSONResponse:
    request_id = get_request_id(
        request
    )

    detail = error.detail

    if isinstance(detail, str):
        message = detail
        details = None
    else:
        message = "The request could not be completed."
        details = detail

    error_code = (
        "RESOURCE_NOT_FOUND"
        if error.status_code == 404
        else "HTTP_ERROR"
    )

    logger.warning(
        "http_error",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": error.status_code,
            "error_code": error_code,
        },
    )

    headers = dict(
        error.headers or {}
    )

    headers[
        "X-Request-ID"
    ] = request_id

    return JSONResponse(
        status_code=error.status_code,
        content=jsonable_encoder(
            build_error_payload(
                code=error_code,
                message=message,
                request_id=request_id,
                details=details,
            )
        ),
        headers=headers,
    )


async def validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    request_id = get_request_id(
        request
    )

    details = jsonable_encoder(
        error.errors()
    )

    logger.warning(
        "request_validation_failed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": 422,
            "error_code": (
                "REQUEST_VALIDATION_ERROR"
            ),
        },
    )

    return JSONResponse(
        status_code=422,
        content=build_error_payload(
            code=(
                "REQUEST_VALIDATION_ERROR"
            ),
            message=(
                "The request contains invalid "
                "or missing values."
            ),
            request_id=request_id,
            details=details,
        ),
        headers={
            "X-Request-ID": request_id,
        },
    )


async def unexpected_error_handler(
    request: Request,
    error: Exception,
) -> JSONResponse:
    request_id = get_request_id(
        request
    )

    logger.exception(
        "unhandled_api_error",
        exc_info=error,
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
            "error_code": (
                "INTERNAL_SERVER_ERROR"
            ),
        },
    )

    return JSONResponse(
        status_code=500,
        content=build_error_payload(
            code=(
                "INTERNAL_SERVER_ERROR"
            ),
            message=(
                "PlantMind encountered an "
                "unexpected server error."
            ),
            request_id=request_id,
        ),
        headers={
            "X-Request-ID": request_id,
        },
    )


def register_exception_handlers(
    app: FastAPI,
) -> None:
    app.add_exception_handler(
        ApiError,
        api_error_handler,
    )

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,
    )

    app.add_exception_handler(
        Exception,
        unexpected_error_handler,
    )
