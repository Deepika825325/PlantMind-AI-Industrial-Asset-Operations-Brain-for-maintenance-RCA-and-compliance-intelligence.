from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.ml_anomaly.schemas import (
    MlAnomalyPredictionRequest,
    MlTelemetryRecord,
)
from apps.api.ml_anomaly.service import (
    FEATURE_VERSION,
    MODEL_VERSION,
    THRESHOLD_VERSION,
    P101MultivariateAnomalyModel,
)
from apps.api.routes import ml_anomalies as ml_route


client = TestClient(app)


def _record(
    sequence: int,
    *,
    vibration: float = 2.25,
    temperature: float = 63.5,
    current: float = 18.6,
    rpm: float = 1480.0,
) -> MlTelemetryRecord:
    timestamp = datetime(
        2026,
        7,
        10,
        9,
        0,
        0,
        tzinfo=timezone.utc,
    ) + timedelta(seconds=sequence * 10)

    return MlTelemetryRecord(
        sequence=sequence,
        timestamp=timestamp.isoformat(),
        asset_id="P-101",
        vibration_mm_s=vibration,
        bearing_temperature_deg_c=temperature,
        motor_current_a=current,
        rpm=rpm,
        health_score=96,
        anomaly_score=0.03,
        data_quality="good",
    )


def _healthy_records() -> list[MlTelemetryRecord]:
    return [
        _record(
            sequence=index,
            vibration=2.25 + index * 0.02,
            temperature=63.5 + index * 0.05,
            current=18.6 + index * 0.01,
            rpm=1480.0,
        )
        for index in range(8)
    ]


def _degradation_records() -> list[MlTelemetryRecord]:
    return [
        _record(
            sequence=0,
            vibration=2.3,
            temperature=63.8,
            current=18.7,
            rpm=1480.0,
        ),
        _record(
            sequence=1,
            vibration=3.2,
            temperature=68.0,
            current=19.4,
            rpm=1478.0,
        ),
        _record(
            sequence=2,
            vibration=4.8,
            temperature=75.0,
            current=20.8,
            rpm=1472.0,
        ),
        _record(
            sequence=3,
            vibration=6.5,
            temperature=84.0,
            current=22.1,
            rpm=1464.0,
        ),
        _record(
            sequence=4,
            vibration=8.4,
            temperature=91.0,
            current=24.0,
            rpm=1455.0,
        ),
    ]


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        ml_route,
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
        "user_id": "ml-anomaly-tester",
        "email": "ml-anomaly@plantmind.local",
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
def isolated_ml_model() -> Iterator[P101MultivariateAnomalyModel]:
    original_model = ml_route.ml_anomaly_model
    model = P101MultivariateAnomalyModel()
    ml_route.ml_anomaly_model = model

    try:
        yield model
    finally:
        ml_route.ml_anomaly_model = original_model


def test_model_card_records_versions_and_scope() -> None:
    model = P101MultivariateAnomalyModel()

    card = model.model_card()

    assert card.model_version == MODEL_VERSION
    assert card.feature_version == FEATURE_VERSION
    assert card.threshold_version == THRESHOLD_VERSION
    assert card.model_type == "deterministic_multivariate_residual"
    assert card.asset_id == "P-101"
    assert card.live_plant_connected is False
    assert card.reproducible is True
    assert "windowed_vibration_mm_s" in card.input_features


def test_healthy_replay_produces_low_anomaly_score() -> None:
    model = P101MultivariateAnomalyModel()

    response = model.predict(
        MlAnomalyPredictionRequest(
            asset_id="P-101",
            records=_healthy_records(),
            window_size=6,
        )
    )

    assert response.model_version == MODEL_VERSION
    assert response.feature_version == FEATURE_VERSION
    assert response.threshold_version == THRESHOLD_VERSION
    assert response.prediction_count == 8

    latest = response.predictions[-1]

    assert latest.anomaly_score < 0.35
    assert latest.anomaly_label == "normal"
    assert latest.prediction_latency_ms > 0


def test_degradation_replay_produces_increasing_anomaly_score() -> None:
    model = P101MultivariateAnomalyModel()

    response = model.predict(
        MlAnomalyPredictionRequest(
            asset_id="P-101",
            records=_degradation_records(),
            window_size=5,
        )
    )

    first = response.predictions[0]
    latest = response.predictions[-1]

    assert latest.anomaly_score > first.anomaly_score
    assert latest.anomaly_score >= 0.75
    assert latest.anomaly_label == "critical"


def test_prediction_records_contributing_features_and_versions() -> None:
    model = P101MultivariateAnomalyModel()

    response = model.predict(
        MlAnomalyPredictionRequest(
            asset_id="P-101",
            records=_degradation_records(),
            window_size=5,
        )
    )

    latest = response.predictions[-1]

    feature_names = {
        feature.feature_name
        for feature in latest.contributing_features
    }

    assert latest.model_version == MODEL_VERSION
    assert latest.feature_version == FEATURE_VERSION
    assert latest.threshold_version == THRESHOLD_VERSION
    assert latest.prediction_timestamp.startswith("2026-07-10T09:00:40")
    assert latest.prediction_latency_ms > 0
    assert "vibration_mm_s" in feature_names
    assert "bearing_temperature_deg_c" in feature_names


def test_model_output_is_reproducible_for_same_input() -> None:
    request = MlAnomalyPredictionRequest(
        asset_id="P-101",
        records=_degradation_records(),
        window_size=5,
    )

    first_model = P101MultivariateAnomalyModel()
    second_model = P101MultivariateAnomalyModel()

    first = first_model.predict(request).predictions
    second = second_model.predict(request).predictions

    assert [
        prediction.prediction_id
        for prediction in first
    ] == [
        prediction.prediction_id
        for prediction in second
    ]

    assert [
        prediction.anomaly_score
        for prediction in first
    ] == [
        prediction.anomaly_score
        for prediction in second
    ]

    assert [
        prediction.anomaly_label
        for prediction in first
    ] == [
        prediction.anomaly_label
        for prediction in second
    ]


def test_prediction_history_is_stored_by_asset() -> None:
    model = P101MultivariateAnomalyModel()

    model.predict(
        MlAnomalyPredictionRequest(
            asset_id="P-101",
            records=_healthy_records(),
            window_size=6,
        )
    )

    history = model.prediction_history(
        "P-101"
    )

    assert history.asset_id == "P-101"
    assert history.model_version == MODEL_VERSION
    assert history.prediction_count == 8


def test_ml_anomaly_api_model_predict_and_history() -> None:
    with isolated_ml_model():
        with authorized_user("get_ml_anomaly_model_card"):
            card_response = client.get(
                "/ml-anomalies/model"
            )

        assert card_response.status_code == 200
        assert card_response.json()["model_version"] == MODEL_VERSION

        with authorized_user("predict_ml_anomalies"):
            predict_response = client.post(
                "/ml-anomalies/predict",
                json={
                    "asset_id": "P-101",
                    "window_size": 5,
                    "records": [
                        record.model_dump()
                        for record in _degradation_records()
                    ],
                },
            )

        assert predict_response.status_code == 200
        assert predict_response.json()["prediction_count"] == 5
        assert (
            predict_response.json()["predictions"][-1]["anomaly_label"]
            == "critical"
        )

        with authorized_user("get_asset_ml_predictions"):
            history_response = client.get(
                "/ml-anomalies/assets/P-101/predictions"
            )

        assert history_response.status_code == 200
        assert history_response.json()["prediction_count"] == 5


def test_ml_anomaly_api_requires_authentication() -> None:
    response = client.get(
        "/ml-anomalies/model"
    )

    assert response.status_code == 401