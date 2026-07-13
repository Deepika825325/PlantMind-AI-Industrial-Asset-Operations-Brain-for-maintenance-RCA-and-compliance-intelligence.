from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.model_registry.schemas import (
    RestoreProductionRequest,
    TransitionModelStageRequest,
)
from apps.api.model_registry.service import (
    DEFAULT_ANOMALY_MODEL_NAME,
    ModelRegistryService,
)
from apps.api.routes import model_registry as model_registry_route


client = TestClient(app)


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        model_registry_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_user(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "model-registry-tester",
        "email": "model-registry@plantmind.local",
        "role": "maintenance_engineer",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_model_registry_service(
    registry_path: Path,
) -> Iterator[ModelRegistryService]:
    original_service = model_registry_route.model_registry_service

    service = ModelRegistryService(
        registry_path=registry_path
    )

    model_registry_route.model_registry_service = service

    try:
        yield service
    finally:
        model_registry_route.model_registry_service = original_service


def test_anomaly_model_is_registered_with_evaluation_metrics(
    tmp_path: Path,
) -> None:
    service = ModelRegistryService(
        registry_path=tmp_path / "model_registry.json"
    )

    versions = service.list_versions(
        DEFAULT_ANOMALY_MODEL_NAME
    )

    assert versions
    assert {
        version.model_version
        for version in versions
    } >= {
        "v0.3.11",
        "v0.3.10",
    }

    production = service.get_production_model(
        DEFAULT_ANOMALY_MODEL_NAME
    )

    assert production.selected_version == "v0.3.11"
    assert production.selection_source == "registry_stage"
    assert production.model.deployment_stage == "Production"
    assert production.model.dataset_version == "telemetry-demo-v1"
    assert production.model.feature_version == "p101-multivariate-features-v1"
    assert production.model.artifact_location.endswith(
        "v0.3.11/model.pkl"
    )

    assert production.model.metrics["precision"] >= 0.9
    assert production.model.metrics["recall"] >= 0.9
    assert production.model.metrics["f1_score"] >= 0.9
    assert "roc_auc" in production.model.metrics
    assert "model_latency_ms" in production.model.metrics


def test_production_model_can_be_changed_by_configuration(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    monkeypatch.setenv(
        "PLANTMIND_PRODUCTION_ANOMALY_MODEL_VERSION",
        "v0.3.10",
    )

    service = ModelRegistryService(
        registry_path=tmp_path / "model_registry.json"
    )

    production = service.get_production_model(
        DEFAULT_ANOMALY_MODEL_NAME
    )

    assert production.selected_version == "v0.3.10"
    assert production.selection_source == "environment_config"
    assert production.configuration_key == (
        "PLANTMIND_PRODUCTION_ANOMALY_MODEL_VERSION"
    )
    assert production.model.model_version == "v0.3.10"


def test_previous_production_version_can_be_restored(
    tmp_path: Path,
) -> None:
    service = ModelRegistryService(
        registry_path=tmp_path / "model_registry.json"
    )

    promoted = service.transition_stage(
        TransitionModelStageRequest(
            model_name=DEFAULT_ANOMALY_MODEL_NAME,
            model_version="v0.3.10",
            target_stage="Production",
            approval="approved",
            approved_by="maintenance_lead",
            actor="mlops_engineer",
            reason="Promote previous model for rollback test.",
        )
    )

    assert promoted.deployment_stage == "Production"
    assert promoted.rollback_target == "v0.3.11"

    current = service.get_production_model(
        DEFAULT_ANOMALY_MODEL_NAME
    )

    assert current.selected_version == "v0.3.10"

    restored = service.restore_previous_production_model(
        RestoreProductionRequest(
            model_name=DEFAULT_ANOMALY_MODEL_NAME,
            actor="mlops_engineer",
            reason="Restore previous production model.",
        )
    )

    assert restored.selected_version == "v0.3.11"
    assert restored.model.deployment_stage == "Production"
    assert restored.model.rollback_target == "v0.3.10"


def test_model_registry_records_audit_events(
    tmp_path: Path,
) -> None:
    service = ModelRegistryService(
        registry_path=tmp_path / "model_registry.json"
    )

    before = service.audit_events(
        DEFAULT_ANOMALY_MODEL_NAME
    )

    service.transition_stage(
        TransitionModelStageRequest(
            model_name=DEFAULT_ANOMALY_MODEL_NAME,
            model_version="v0.3.10",
            target_stage="Staging",
            approval="approved",
            approved_by="maintenance_lead",
            actor="mlops_engineer",
            reason="Move validated rollback candidate into staging.",
        )
    )

    after = service.audit_events(
        DEFAULT_ANOMALY_MODEL_NAME
    )

    assert len(after) == len(before) + 1
    assert after[0].event_type == "stage_transitioned"
    assert after[0].model_version == "v0.3.10"


def test_model_registry_api_returns_production_model(
    tmp_path: Path,
) -> None:
    with isolated_model_registry_service(
        tmp_path / "model_registry.json"
    ):
        with authorized_user(
            "get_production_model"
        ):
            response = client.get(
                "/mlops/model-registry/production/"
                "plantmind-p101-anomaly-detector"
            )

    assert response.status_code == 200

    payload = response.json()

    assert payload["model_name"] == "plantmind-p101-anomaly-detector"
    assert payload["selected_version"] == "v0.3.11"
    assert payload["model"]["metrics"]["f1_score"] >= 0.9
    assert payload["model"]["deployment_stage"] == "Production"


def test_model_registry_api_can_transition_and_restore_model(
    tmp_path: Path,
) -> None:
    with isolated_model_registry_service(
        tmp_path / "model_registry.json"
    ):
        with authorized_user(
            "transition_model_stage"
        ):
            transition_response = client.post(
                "/mlops/model-registry/transition-stage",
                json={
                    "model_name": "plantmind-p101-anomaly-detector",
                    "model_version": "v0.3.10",
                    "target_stage": "Production",
                    "approval": "approved",
                    "approved_by": "maintenance_lead",
                    "actor": "mlops_engineer",
                    "reason": "Promote rollback candidate.",
                },
            )

        with authorized_user(
            "restore_production_model"
        ):
            restore_response = client.post(
                "/mlops/model-registry/restore-production",
                json={
                    "model_name": "plantmind-p101-anomaly-detector",
                    "actor": "mlops_engineer",
                    "reason": "Restore previous production model.",
                },
            )

    assert transition_response.status_code == 200
    assert transition_response.json()["deployment_stage"] == "Production"
    assert transition_response.json()["rollback_target"] == "v0.3.11"

    assert restore_response.status_code == 200
    assert restore_response.json()["selected_version"] == "v0.3.11"


def test_model_registry_overview_lists_mlops_stages(
    tmp_path: Path,
) -> None:
    service = ModelRegistryService(
        registry_path=tmp_path / "model_registry.json"
    )

    overview = service.overview()

    assert overview.stages == [
        "Development",
        "Candidate",
        "Validated",
        "Staging",
        "Production",
        "Archived",
    ]
    assert overview.registered_model_count >= 1
    assert overview.model_version_count >= 2
    assert DEFAULT_ANOMALY_MODEL_NAME in overview.model_names