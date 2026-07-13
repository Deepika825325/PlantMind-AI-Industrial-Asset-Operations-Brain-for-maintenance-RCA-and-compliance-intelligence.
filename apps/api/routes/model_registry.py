from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.api.auth.dependencies import require_permission
from apps.api.model_registry.schemas import (
    ModelRegistryOverview,
    ModelStage,
    ProductionModelSelection,
    RegisterModelVersionRequest,
    RegisteredModelVersion,
    RegistryAuditEvent,
    RestoreProductionRequest,
    TransitionModelStageRequest,
)
from apps.api.model_registry.service import ModelRegistryService


router = APIRouter(
    prefix="/mlops/model-registry",
    tags=["model-registry"],
)

model_registry_service = ModelRegistryService()


@router.get(
    "/overview",
    response_model=ModelRegistryOverview,
)
def get_model_registry_overview(
    user=Depends(require_permission("document.read")),
) -> ModelRegistryOverview:
    return model_registry_service.overview()


@router.get(
    "/stages",
    response_model=list[ModelStage],
)
def get_model_registry_stages(
    user=Depends(require_permission("document.read")),
) -> list[ModelStage]:
    return model_registry_service.stages()


@router.get(
    "/models",
    response_model=list[str],
)
def list_registered_models(
    user=Depends(require_permission("document.read")),
) -> list[str]:
    return model_registry_service.list_models()


@router.get(
    "/models/{model_name}/versions",
    response_model=list[RegisteredModelVersion],
)
def list_model_versions(
    model_name: str,
    user=Depends(require_permission("document.read")),
) -> list[RegisteredModelVersion]:
    return model_registry_service.list_versions(
        model_name
    )


@router.get(
    "/production/{model_name}",
    response_model=ProductionModelSelection,
)
def get_production_model(
    model_name: str,
    user=Depends(require_permission("document.read")),
) -> ProductionModelSelection:
    try:
        return model_registry_service.get_production_model(
            model_name
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/audit-events",
    response_model=list[RegistryAuditEvent],
)
def list_model_registry_audit_events(
    model_name: str | None = None,
    user=Depends(require_permission("document.read")),
) -> list[RegistryAuditEvent]:
    return model_registry_service.audit_events(
        model_name=model_name
    )


@router.post(
    "/register",
    response_model=RegisteredModelVersion,
)
def register_model_version(
    request: RegisterModelVersionRequest,
    user=Depends(require_permission("evidence.write")),
) -> RegisteredModelVersion:
    try:
        return model_registry_service.register_model_version(
            request
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.post(
    "/transition-stage",
    response_model=RegisteredModelVersion,
)
def transition_model_stage(
    request: TransitionModelStageRequest,
    user=Depends(require_permission("evidence.write")),
) -> RegisteredModelVersion:
    try:
        return model_registry_service.transition_stage(
            request
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/restore-production",
    response_model=ProductionModelSelection,
)
def restore_production_model(
    request: RestoreProductionRequest,
    user=Depends(require_permission("evidence.write")),
) -> ProductionModelSelection:
    try:
        return model_registry_service.restore_previous_production_model(
            request
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc