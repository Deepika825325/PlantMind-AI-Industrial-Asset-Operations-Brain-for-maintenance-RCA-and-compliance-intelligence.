from apps.api.routes.ingestion import router as ingestion_router
from apps.api.routes.rag_indexing import router as rag_indexing_router
from apps.api.routes.rag_answering import router as rag_answering_router
from apps.api.routes.rag_evaluation import router as rag_evaluation_router
from apps.api.routes.ingestion_workers import router as ingestion_workers_router
from apps.api.routes.hybrid_retrieval import router as hybrid_retrieval_router
from apps.api.routes.verified_ask import router as verified_ask_router
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.auth.dependencies import (
    require_permission_if_auth_enabled,
)
from apps.api.auth.rbac import (
    Permission,
)
from apps.api.core.errors import ApiError
from apps.api.core.exception_handlers import (
    register_exception_handlers,
)
from apps.api.core.logging import (
    configure_logging,
    get_logger,
)
from apps.api.core.middleware import (
    RequestContextMiddleware,
)
from apps.api.core.readiness import (
    assert_data_ready,
    validate_data_files,
)
from apps.api.routes import (
    ask,
    auth,
    audit,
    assets,
    compliance,
    dashboard,
    documents,
    knowledge_graph,
    maintenance,
    pid,
    rca,
)
from apps.api.services.data_loader import (
    clear_data_cache,
    get_file_status,
)
from apps.api.services.demo_reset_service import (
    reset_demo_state,
)


configure_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    logger.info(
        "plantmind_startup_started"
    )

    readiness = assert_data_ready()

    app.state.readiness = readiness

    logger.info(
        "plantmind_startup_completed",
        extra={
            "status_code": 200,
        },
    )

    yield

    logger.info(
        "plantmind_shutdown_completed"
    )


app = FastAPI(
    title="PlantMind AI API",
    description=(
        "Backend API for Industrial Asset "
        "and Operations Intelligence demo."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID",
    ],
)

app.add_middleware(
    RequestContextMiddleware
)

register_exception_handlers(
    app
)

app.include_router(
    auth.router
)

app.include_router(
    audit.router
)

app.include_router(
    dashboard.router
)

app.include_router(
    assets.router
)

app.include_router(
    documents.router
)

app.include_router(
    compliance.router
)

app.include_router(
    maintenance.router
)

app.include_router(
    knowledge_graph.router
)

app.include_router(
    ask.router
)

app.include_router(
    pid.router
)

app.include_router(
    rca.router
)
app.include_router(ingestion_router)
app.include_router(rag_indexing_router)
app.include_router(rag_answering_router)
app.include_router(rag_evaluation_router)
app.include_router(ingestion_workers_router)
app.include_router(hybrid_retrieval_router)
app.include_router(verified_ask_router)


@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "message": (
            "PlantMind AI API is running"
        ),
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "readiness": "/ready",
        "file_status": "/status/files",
    }


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    return {
        "status": "healthy",
        "service": "PlantMind AI API",
        "version": "0.2.0",
    }


@app.get(
    "/ready",
    tags=["System"],
)
def readiness_check():
    result = validate_data_files()

    if not result["ready"]:
        raise ApiError(
            status_code=503,
            code="SERVICE_NOT_READY",
            message=(
                "PlantMind is not ready to "
                "serve requests."
            ),
            details={
                "status": result["status"],
                "issues": result["issues"],
                "required_file_count": result[
                    "required_file_count"
                ],
                "valid_file_count": result[
                    "valid_file_count"
                ],
                "missing_file_count": result[
                    "missing_file_count"
                ],
                "invalid_file_count": result[
                    "invalid_file_count"
                ],
            },
        )

    return result


@app.get(
    "/status/files",
    tags=["System"],
)
def file_status():
    return {
        "inventory": get_file_status(),
        "validation": (
            validate_data_files()
        ),
    }


@app.post(
    "/admin/reload-cache",
    tags=["System"],
)
def reload_cache(
    _current_user=Depends(
        require_permission_if_auth_enabled(
            Permission.ADMIN_RELOAD_CACHE
        )
    ),
):
    clear_data_cache()

    readiness = validate_data_files()

    if not readiness["ready"]:
        raise ApiError(
            status_code=503,
            code=(
                "CACHE_RELOAD_VALIDATION_FAILED"
            ),
            message=(
                "The cache was cleared, but "
                "data validation failed."
            ),
            details={
                "issues": readiness["issues"],
            },
        )

    return {
        "status": "cache_reloaded",
        "message": (
            "Data cache cleared and source "
            "files validated successfully."
        ),
        "readiness": {
            "ready": readiness["ready"],
            "valid_file_count": readiness[
                "valid_file_count"
            ],
            "required_file_count": readiness[
                "required_file_count"
            ],
        },
    }


@app.post(
    "/admin/reset-demo",
    tags=["System"],
)
def reset_demo(
    _current_user=Depends(
        require_permission_if_auth_enabled(
            Permission.ADMIN_RESET_DEMO
        )
    ),
):
    try:
        return reset_demo_state()
    except (
        FileNotFoundError,
        OSError,
        RuntimeError,
        ValueError,
    ) as error:
        raise ApiError(
            status_code=500,
            code="DEMO_RESET_FAILED",
            message=(
                "PlantMind could not reset "
                "the demo environment."
            ),
            details={
                "reason": str(error),
            },
        ) from error


@app.get(
    "/admin/test-error",
    tags=["System"],
    include_in_schema=False,
)
def test_structured_error():
    raise ApiError(
        status_code=503,
        code="DEMO_TEST_ERROR",
        message=(
            "Structured error handling "
            "is operational."
        ),
    )
