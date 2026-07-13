from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

from apps.api.model_registry.schemas import (
    ModelRegistryOverview,
    ModelRegistryState,
    ModelStage,
    ProductionModelSelection,
    RegisterModelVersionRequest,
    RegisteredModelVersion,
    RegistryAuditEvent,
    RestoreProductionRequest,
    TransitionModelStageRequest,
)


MODEL_STAGES: list[ModelStage] = [
    "Development",
    "Candidate",
    "Validated",
    "Staging",
    "Production",
    "Archived",
]

DEFAULT_ANOMALY_MODEL_NAME = "plantmind-p101-anomaly-detector"


class ModelRegistryService:
    def __init__(
        self,
        *,
        registry_path: Path | None = None,
    ) -> None:
        self.registry_path = registry_path or Path(
            "data/demo/model_registry.json"
        )

    def overview(self) -> ModelRegistryOverview:
        state = self._load_state()
        model_names = sorted(
            {
                model.model_name
                for model in state.model_versions
            }
        )

        return ModelRegistryOverview(
            stages=MODEL_STAGES,
            registered_model_count=len(model_names),
            model_version_count=len(state.model_versions),
            production_model_count=sum(
                1
                for model in state.model_versions
                if model.deployment_stage == "Production"
            ),
            model_names=model_names,
            audit_event_count=len(state.audit_events),
        )

    def stages(self) -> list[ModelStage]:
        return MODEL_STAGES

    def list_models(self) -> list[str]:
        state = self._load_state()

        return sorted(
            {
                model.model_name
                for model in state.model_versions
            }
        )

    def list_versions(
        self,
        model_name: str,
    ) -> list[RegisteredModelVersion]:
        state = self._load_state()

        return sorted(
            [
                model
                for model in state.model_versions
                if model.model_name == model_name
            ],
            key=lambda model: model.updated_at,
            reverse=True,
        )

    def audit_events(
        self,
        model_name: str | None = None,
    ) -> list[RegistryAuditEvent]:
        state = self._load_state()

        events = state.audit_events

        if model_name:
            events = [
                event
                for event in events
                if event.model_name == model_name
            ]

        return sorted(
            events,
            key=lambda event: event.created_at,
            reverse=True,
        )

    def get_production_model(
        self,
        model_name: str = DEFAULT_ANOMALY_MODEL_NAME,
    ) -> ProductionModelSelection:
        state = self._load_state()

        configured_version, configuration_key = (
            self._configured_production_version()
        )

        if configured_version:
            configured_model = self._find_model_version(
                state=state,
                model_name=model_name,
                model_version=configured_version,
            )

            if configured_model and configured_model.deployment_stage != "Archived":
                return ProductionModelSelection(
                    model_name=model_name,
                    selected_version=configured_model.model_version,
                    selection_source="environment_config",
                    configuration_key=configuration_key,
                    rollback_target=configured_model.rollback_target,
                    model=configured_model,
                )

        production_model = self._registry_production_model(
            state=state,
            model_name=model_name,
        )

        if production_model:
            return ProductionModelSelection(
                model_name=model_name,
                selected_version=production_model.model_version,
                selection_source="registry_stage",
                configuration_key=None,
                rollback_target=production_model.rollback_target,
                model=production_model,
            )

        fallback_model = self._fallback_model(
            state=state,
            model_name=model_name,
        )

        if not fallback_model:
            raise ValueError(
                f"No model versions registered for {model_name}."
            )

        return ProductionModelSelection(
            model_name=model_name,
            selected_version=fallback_model.model_version,
            selection_source="fallback",
            configuration_key=None,
            rollback_target=fallback_model.rollback_target,
            model=fallback_model,
        )

    def register_model_version(
        self,
        request: RegisterModelVersionRequest,
    ) -> RegisteredModelVersion:
        state = self._load_state()

        existing = self._find_model_version(
            state=state,
            model_name=request.model_name,
            model_version=request.model_version,
        )

        if existing:
            raise ValueError(
                f"Model {request.model_name} version "
                f"{request.model_version} is already registered."
            )

        if (
            request.deployment_stage == "Production"
            and request.approval != "approved"
        ):
            raise ValueError(
                "Production model registration requires approval."
            )

        now = self._now()

        model = RegisteredModelVersion(
            model_name=request.model_name,
            model_version=request.model_version,
            dataset_version=request.dataset_version,
            feature_version=request.feature_version,
            parameters=request.parameters,
            metrics=request.metrics,
            artifact_location=request.artifact_location,
            deployment_stage=request.deployment_stage,
            approval=request.approval,
            approved_by=request.approved_by,
            rollback_target=request.rollback_target,
            created_at=now,
            updated_at=now,
            description=request.description,
            tags=request.tags,
        )

        state.model_versions.append(
            model
        )

        state.audit_events.append(
            self._event(
                event_type="model_registered",
                model_name=model.model_name,
                model_version=model.model_version,
                from_stage=None,
                to_stage=model.deployment_stage,
                actor=request.approved_by or "system",
                reason="Model version registered in PlantMind registry.",
            )
        )

        self._save_state(
            state
        )

        return model

    def transition_stage(
        self,
        request: TransitionModelStageRequest,
    ) -> RegisteredModelVersion:
        state = self._load_state()

        model = self._find_model_version(
            state=state,
            model_name=request.model_name,
            model_version=request.model_version,
        )

        if not model:
            raise ValueError(
                f"Model {request.model_name} version "
                f"{request.model_version} was not found."
            )

        if request.target_stage == "Production":
            approval = request.approval or model.approval

            if approval != "approved":
                raise ValueError(
                    "Transition to Production requires approved status."
                )

        previous_stage = model.deployment_stage
        now = self._now()

        if request.target_stage == "Production":
            previous_production = self._registry_production_model(
                state=state,
                model_name=request.model_name,
            )

            if (
                previous_production
                and previous_production.model_version != model.model_version
            ):
                previous_production.deployment_stage = "Staging"
                previous_production.updated_at = now
                model.rollback_target = previous_production.model_version

        model.deployment_stage = request.target_stage
        model.updated_at = now

        if request.approval:
            model.approval = request.approval

        if request.approved_by:
            model.approved_by = request.approved_by

        state.audit_events.append(
            self._event(
                event_type="stage_transitioned",
                model_name=model.model_name,
                model_version=model.model_version,
                from_stage=previous_stage,
                to_stage=model.deployment_stage,
                actor=request.actor,
                reason=request.reason,
            )
        )

        self._save_state(
            state
        )

        return model

    def restore_previous_production_model(
        self,
        request: RestoreProductionRequest,
    ) -> ProductionModelSelection:
        state = self._load_state()

        current_production = self._registry_production_model(
            state=state,
            model_name=request.model_name,
        )

        if not current_production:
            raise ValueError(
                f"No production model found for {request.model_name}."
            )

        rollback_target = current_production.rollback_target

        if not rollback_target:
            raise ValueError(
                f"Production model {current_production.model_version} "
                "does not define a rollback target."
            )

        rollback_model = self._find_model_version(
            state=state,
            model_name=request.model_name,
            model_version=rollback_target,
        )

        if not rollback_model:
            raise ValueError(
                f"Rollback target {rollback_target} was not found."
            )

        now = self._now()

        current_production.deployment_stage = "Staging"
        current_production.updated_at = now

        rollback_model.deployment_stage = "Production"
        rollback_model.approval = "approved"
        rollback_model.updated_at = now
        rollback_model.rollback_target = current_production.model_version

        state.audit_events.append(
            self._event(
                event_type="production_restored",
                model_name=rollback_model.model_name,
                model_version=rollback_model.model_version,
                from_stage="Staging",
                to_stage="Production",
                actor=request.actor,
                reason=request.reason,
            )
        )

        self._save_state(
            state
        )

        return ProductionModelSelection(
            model_name=request.model_name,
            selected_version=rollback_model.model_version,
            selection_source="registry_stage",
            configuration_key=None,
            rollback_target=rollback_model.rollback_target,
            model=rollback_model,
        )

    def _load_state(self) -> ModelRegistryState:
        if not self.registry_path.exists():
            return self._default_state()

        try:
            payload = json.loads(
                self.registry_path.read_text(
                    encoding="utf-8-sig"
                )
            )
        except json.JSONDecodeError:
            return self._default_state()

        return self._state_from_payload(
            payload
        )

    def _save_state(
        self,
        state: ModelRegistryState,
    ) -> None:
        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = state.model_dump(
            mode="json"
        )

        self.registry_path.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def _state_from_payload(
        self,
        payload: object,
    ) -> ModelRegistryState:
        if not isinstance(
            payload,
            dict,
        ):
            return self._default_state()

        model_versions = payload.get(
            "model_versions",
            [],
        )
        audit_events = payload.get(
            "audit_events",
            [],
        )

        if not isinstance(
            model_versions,
            list,
        ):
            model_versions = []

        if not isinstance(
            audit_events,
            list,
        ):
            audit_events = []

        return ModelRegistryState(
            model_versions=[
                RegisteredModelVersion(
                    **model
                )
                for model in model_versions
                if isinstance(
                    model,
                    dict,
                )
            ],
            audit_events=[
                RegistryAuditEvent(
                    **event
                )
                for event in audit_events
                if isinstance(
                    event,
                    dict,
                )
            ],
        )

    def _default_state(self) -> ModelRegistryState:
        return ModelRegistryState(
            model_versions=[
                RegisteredModelVersion(
                    model_name=DEFAULT_ANOMALY_MODEL_NAME,
                    model_version="v0.3.11",
                    dataset_version="telemetry-demo-v1",
                    feature_version="p101-multivariate-features-v1",
                    parameters={
                        "window_size": 12,
                        "contamination": 0.08,
                        "feature_count": 5,
                        "random_state": 42,
                    },
                    metrics={
                        "precision": 0.94,
                        "recall": 0.91,
                        "f1_score": 0.925,
                        "roc_auc": 0.96,
                        "false_positive_rate": 0.04,
                        "model_latency_ms": 18.0,
                    },
                    artifact_location=(
                        "artifacts/models/p101-anomaly-detector/"
                        "v0.3.11/model.pkl"
                    ),
                    deployment_stage="Production",
                    approval="approved",
                    approved_by="maintenance_lead",
                    rollback_target="v0.3.10",
                    created_at="2026-07-10T09:00:00+00:00",
                    updated_at="2026-07-10T09:00:00+00:00",
                    description=(
                        "P-101 multivariate anomaly detector promoted "
                        "after evaluation."
                    ),
                    tags={
                        "asset_id": "P-101",
                        "model_family": "anomaly_detection",
                        "source_commit": "b774f59",
                    },
                ),
                RegisteredModelVersion(
                    model_name=DEFAULT_ANOMALY_MODEL_NAME,
                    model_version="v0.3.10",
                    dataset_version="telemetry-demo-v1",
                    feature_version="p101-multivariate-features-v1",
                    parameters={
                        "window_size": 8,
                        "contamination": 0.1,
                        "feature_count": 5,
                        "random_state": 42,
                    },
                    metrics={
                        "precision": 0.89,
                        "recall": 0.87,
                        "f1_score": 0.88,
                        "roc_auc": 0.92,
                        "false_positive_rate": 0.07,
                        "model_latency_ms": 16.0,
                    },
                    artifact_location=(
                        "artifacts/models/p101-anomaly-detector/"
                        "v0.3.10/model.pkl"
                    ),
                    deployment_stage="Validated",
                    approval="approved",
                    approved_by="maintenance_lead",
                    rollback_target=None,
                    created_at="2026-07-09T09:00:00+00:00",
                    updated_at="2026-07-09T09:00:00+00:00",
                    description=(
                        "Previous validated anomaly detector available "
                        "for rollback."
                    ),
                    tags={
                        "asset_id": "P-101",
                        "model_family": "anomaly_detection",
                        "source_commit": "7243b52",
                    },
                ),
            ],
            audit_events=[
                RegistryAuditEvent(
                    event_id="REG-P101-ANOMALY-V0311",
                    event_type="model_registered",
                    model_name=DEFAULT_ANOMALY_MODEL_NAME,
                    model_version="v0.3.11",
                    from_stage=None,
                    to_stage="Production",
                    actor="system",
                    reason=(
                        "Seed production anomaly model for Day 28 registry."
                    ),
                    created_at="2026-07-10T09:00:00+00:00",
                )
            ],
        )

    def _configured_production_version(
        self,
    ) -> tuple[str | None, str | None]:
        config_keys = [
            "PLANTMIND_PRODUCTION_ANOMALY_MODEL_VERSION",
            "PLANTMIND_PRODUCTION_MODEL_VERSION",
        ]

        for key in config_keys:
            value = os.getenv(
                key
            )

            if value:
                return value, key

        return None, None

    def _registry_production_model(
        self,
        *,
        state: ModelRegistryState,
        model_name: str,
    ) -> RegisteredModelVersion | None:
        production_versions = [
            model
            for model in state.model_versions
            if model.model_name == model_name
            and model.deployment_stage == "Production"
        ]

        if not production_versions:
            return None

        return sorted(
            production_versions,
            key=lambda model: model.updated_at,
            reverse=True,
        )[0]

    def _fallback_model(
        self,
        *,
        state: ModelRegistryState,
        model_name: str,
    ) -> RegisteredModelVersion | None:
        candidates = [
            model
            for model in state.model_versions
            if model.model_name == model_name
            and model.deployment_stage != "Archived"
        ]

        if not candidates:
            return None

        stage_priority = {
            "Production": 6,
            "Staging": 5,
            "Validated": 4,
            "Candidate": 3,
            "Development": 2,
            "Archived": 1,
        }

        return sorted(
            candidates,
            key=lambda model: (
                stage_priority[model.deployment_stage],
                model.updated_at,
            ),
            reverse=True,
        )[0]

    def _find_model_version(
        self,
        *,
        state: ModelRegistryState,
        model_name: str,
        model_version: str,
    ) -> RegisteredModelVersion | None:
        for model in state.model_versions:
            if (
                model.model_name == model_name
                and model.model_version == model_version
            ):
                return model

        return None

    def _event(
        self,
        *,
        event_type: str,
        model_name: str,
        model_version: str,
        from_stage: ModelStage | None,
        to_stage: ModelStage | None,
        actor: str,
        reason: str,
    ) -> RegistryAuditEvent:
        return RegistryAuditEvent(
            event_id=f"REG-EVENT-{uuid.uuid4().hex[:12].upper()}",
            event_type=event_type,  # type: ignore[arg-type]
            model_name=model_name,
            model_version=model_version,
            from_stage=from_stage,
            to_stage=to_stage,
            actor=actor,
            reason=reason,
            created_at=self._now(),
        )

    def _now(self) -> str:
        return datetime.now(
            UTC
        ).isoformat()