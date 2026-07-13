from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ModelStage = Literal[
    "Development",
    "Candidate",
    "Validated",
    "Staging",
    "Production",
    "Archived",
]

ApprovalStatus = Literal[
    "pending",
    "approved",
    "rejected",
    "not_required",
]

SelectionSource = Literal[
    "environment_config",
    "registry_stage",
    "fallback",
]


class RegisteredModelVersion(BaseModel):
    model_name: str
    model_version: str
    dataset_version: str
    feature_version: str
    parameters: dict[str, str | int | float | bool] = Field(
        default_factory=dict
    )
    metrics: dict[str, float] = Field(
        default_factory=dict
    )
    artifact_location: str
    deployment_stage: ModelStage
    approval: ApprovalStatus = "pending"
    approved_by: str | None = None
    rollback_target: str | None = None
    created_at: str
    updated_at: str
    description: str | None = None
    tags: dict[str, str] = Field(
        default_factory=dict
    )


class RegisterModelVersionRequest(BaseModel):
    model_name: str
    model_version: str
    dataset_version: str
    feature_version: str
    parameters: dict[str, str | int | float | bool] = Field(
        default_factory=dict
    )
    metrics: dict[str, float] = Field(
        default_factory=dict
    )
    artifact_location: str
    deployment_stage: ModelStage = "Development"
    approval: ApprovalStatus = "pending"
    approved_by: str | None = None
    rollback_target: str | None = None
    description: str | None = None
    tags: dict[str, str] = Field(
        default_factory=dict
    )


class TransitionModelStageRequest(BaseModel):
    model_name: str
    model_version: str
    target_stage: ModelStage
    approval: ApprovalStatus | None = None
    approved_by: str | None = None
    actor: str = "system"
    reason: str


class RestoreProductionRequest(BaseModel):
    model_name: str
    actor: str = "system"
    reason: str = "Restore previous production model"


class RegistryAuditEvent(BaseModel):
    event_id: str
    event_type: Literal[
        "model_registered",
        "stage_transitioned",
        "production_restored",
        "production_selected",
    ]
    model_name: str
    model_version: str
    from_stage: ModelStage | None = None
    to_stage: ModelStage | None = None
    actor: str
    reason: str
    created_at: str


class ProductionModelSelection(BaseModel):
    model_name: str
    selected_version: str
    selection_source: SelectionSource
    configuration_key: str | None = None
    rollback_target: str | None = None
    model: RegisteredModelVersion


class ModelRegistryOverview(BaseModel):
    stages: list[ModelStage]
    registered_model_count: int
    model_version_count: int
    production_model_count: int
    model_names: list[str]
    audit_event_count: int


class ModelRegistryState(BaseModel):
    model_versions: list[RegisteredModelVersion]
    audit_events: list[RegistryAuditEvent]