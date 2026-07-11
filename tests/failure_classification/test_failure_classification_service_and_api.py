from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi.testclient import TestClient

from apps.api.failure_classification.schemas import (
    FailureClassificationRequest,
    FailureTelemetryRecord,
)
from apps.api.failure_classification.service import (
    CONFIDENCE_METHOD,
    MODEL_VERSION,
    FailureModeClassifier,
)
from apps.api.main import app
from apps.api.routes import failure_classification as failure_route


client = TestClient(app)


def _record(
    sequence: int,
    *,
    vibration: float = 2.2,
    temperature: float = 63.0,
    current: float = 18.5,
    rpm: float = 1480.0,
    health: float = 96.0,
    anomaly: float = 0.03,
    data_quality: str = "good",
    scenario: str | None = None,
) -> FailureTelemetryRecord:
    timestamp = datetime(
        2026,
        7,
        10,
        9,
        0,
        0,
        tzinfo=timezone.utc,
    ) + timedelta(seconds=sequence * 10)

    return FailureTelemetryRecord(
        sequence=sequence,
        timestamp=timestamp.isoformat(),
        asset_id="P-101",
        vibration_mm_s=vibration,
        bearing_temperature_deg_c=temperature,
        motor_current_a=current,
        rpm=rpm,
        health_score=health,
        anomaly_score=anomaly,
        data_quality=data_quality,
        scenario=scenario,
    )


def _healthy_records() -> list[FailureTelemetryRecord]:
    return [
        _record(
            sequence=index,
            vibration=2.2 + index * 0.02,
            temperature=63.0 + index * 0.05,
            current=18.5,
            rpm=1480.0,
            anomaly=0.03,
            scenario="normal_operation",
        )
        for index in range(5)
    ]


def _bearing_degradation_records() -> list[FailureTelemetryRecord]:
    return [
        _record(
            sequence=0,
            vibration=2.4,
            temperature=64.0,
            current=18.8,
            rpm=1480.0,
            anomaly=0.05,
            scenario="bearing_degradation",
        ),
        _record(
            sequence=1,
            vibration=4.9,
            temperature=78.5,
            current=21.2,
            rpm=1476.0,
            anomaly=0.42,
            scenario="bearing_degradation",
        ),
        _record(
            sequence=2,
            vibration=8.2,
            temperature=90.0,
            current=23.8,
            rpm=1468.0,
            anomaly=0.82,
            scenario="bearing_degradation",
        ),
    ]


def _lubrication_records() -> list[FailureTelemetryRecord]:
    return [
        _record(
            sequence=0,
            vibration=2.4,
            temperature=63.5,
            current=18.8,
            rpm=1480.0,
            anomaly=0.04,
            scenario="lubrication_degradation",
        ),
        _record(
            sequence=1,
            vibration=4.8,
            temperature=79.0,
            current=20.8,
            rpm=1479.0,
            anomaly=0.40,
            scenario="lubrication_degradation",
        ),
        _record(
            sequence=2,
            vibration=5.5,
            temperature=88.0,
            current=21.7,
            rpm=1477.0,
            anomaly=0.52,
            scenario="lubrication_degradation",
        ),
    ]


def _misalignment_records() -> list[FailureTelemetryRecord]:
    return [
        _record(
            sequence=0,
            vibration=2.5,
            temperature=64.0,
            current=18.5,
            rpm=1480.0,
            anomaly=0.05,
            scenario="shaft_misalignment",
        ),
        _record(
            sequence=1,
            vibration=5.4,
            temperature=71.0,
            current=23.1,
            rpm=1460.0,
            anomaly=0.48,
            scenario="shaft_misalignment",
        ),
        _record(
            sequence=2,
            vibration=6.1,
            temperature=74.0,
            current=24.2,
            rpm=1450.0,
            anomaly=0.56,
            scenario="shaft_misalignment",
        ),
    ]


def _cavitation_records() -> list[FailureTelemetryRecord]:
    return [
        _record(
            sequence=0,
            vibration=2.3,
            temperature=64.0,
            current=18.4,
            rpm=1480.0,
            anomaly=0.04,
            scenario="cavitation",
        ),
        _record(
            sequence=1,
            vibration=4.5,
            temperature=70.0,
            current=20.0,
            rpm=1484.0,
            anomaly=0.36,
            scenario="cavitation",
        ),
        _record(
            sequence=2,
            vibration=5.0,
            temperature=73.0,
            current=20.9,
            rpm=1488.0,
            anomaly=0.46,
            scenario="cavitation",
        ),
    ]


def _unknown_records() -> list[FailureTelemetryRecord]:
    return [
        _record(
            sequence=0,
            vibration=2.7,
            temperature=65.0,
            current=18.8,
            rpm=1480.0,
            anomaly=0.04,
            scenario="unknown_anomaly",
        ),
        _record(
            sequence=1,
            vibration=3.1,
            temperature=70.0,
            current=32.5,
            rpm=1482.0,
            anomaly=0.80,
            data_quality="unknown_pattern",
            scenario="unknown_anomaly",
        ),
    ]


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        failure_route,
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
        "user_id": "failure-classification-tester",
        "email": "failure@plantmind.local",
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
def isolated_classifier() -> Iterator[FailureModeClassifier]:
    original_classifier = failure_route.failure_classifier
    classifier = FailureModeClassifier()
    failure_route.failure_classifier = classifier

    try:
        yield classifier
    finally:
        failure_route.failure_classifier = original_classifier


def _classify(
    records: list[FailureTelemetryRecord],
):
    classifier = FailureModeClassifier()

    return classifier.classify(
        FailureClassificationRequest(
            asset_id="P-101",
            records=records,
        )
    )


def test_model_card_lists_classes_and_no_rul() -> None:
    classifier = FailureModeClassifier()

    card = classifier.model_card()

    assert card.model_version == MODEL_VERSION
    assert card.model_type == "explainable_heuristic_classifier"
    assert card.confidence_method == CONFIDENCE_METHOD
    assert card.live_plant_connected is False
    assert card.rul_supported is False
    assert "healthy" in card.supported_classes
    assert "lubrication_degradation" in card.supported_classes
    assert "bearing_damage" in card.supported_classes
    assert "shaft_misalignment" in card.supported_classes
    assert "cavitation" in card.supported_classes
    assert "unknown_anomaly" in card.supported_classes


def test_healthy_records_classify_as_healthy() -> None:
    response = _classify(
        _healthy_records()
    )

    assert response.model_version == MODEL_VERSION
    assert response.confidence_method == CONFIDENCE_METHOD
    assert response.primary_hypothesis.failure_mode == "healthy"
    assert response.primary_hypothesis.confidence >= 0.75
    assert response.primary_hypothesis.supporting_features


def test_bearing_scenario_ranks_bearing_or_lubrication_highly() -> None:
    response = _classify(
        _bearing_degradation_records()
    )

    ranked_modes = [
        response.primary_hypothesis.failure_mode,
        *[
            alternative.failure_mode
            for alternative in response.alternatives
        ],
    ]

    assert ranked_modes[0] in {
        "bearing_damage",
        "lubrication_degradation",
    }
    assert "bearing_damage" in ranked_modes[:2]
    assert "lubrication_degradation" in ranked_modes[:2]
    assert response.primary_hypothesis.supporting_features
    assert response.primary_hypothesis.contradictory_features == []


def test_lubrication_scenario_ranks_lubrication_highly() -> None:
    response = _classify(
        _lubrication_records()
    )

    assert (
        response.primary_hypothesis.failure_mode
        == "lubrication_degradation"
    )
    assert response.primary_hypothesis.confidence >= 0.55

    feature_names = {
        feature.feature_name
        for feature in response.primary_hypothesis.supporting_features
    }

    assert "bearing_temperature_deg_c" in feature_names
    assert "window_temperature_delta" in feature_names


def test_misalignment_scenario_classifies_as_shaft_misalignment() -> None:
    response = _classify(
        _misalignment_records()
    )

    assert (
        response.primary_hypothesis.failure_mode
        == "shaft_misalignment"
    )

    feature_names = {
        feature.feature_name
        for feature in response.primary_hypothesis.supporting_features
    }

    assert "motor_current_a" in feature_names
    assert "rpm_drop" in feature_names


def test_cavitation_scenario_classifies_as_cavitation() -> None:
    response = _classify(
        _cavitation_records()
    )

    assert response.primary_hypothesis.failure_mode == "cavitation"

    feature_names = {
        feature.feature_name
        for feature in response.primary_hypothesis.supporting_features
    }

    assert "rpm_delta" in feature_names
    assert "bearing_temperature_deg_c" in feature_names


def test_unknown_patterns_fallback_to_unknown_anomaly() -> None:
    response = _classify(
        _unknown_records()
    )

    assert (
        response.primary_hypothesis.failure_mode
        == "unknown_anomaly"
    )
    assert response.primary_hypothesis.confidence >= 0.70
    assert response.primary_hypothesis.supporting_features


def test_response_returns_primary_alternatives_features_and_model_version() -> None:
    response = _classify(
        _bearing_degradation_records()
    )

    assert response.model_version == MODEL_VERSION
    assert response.evaluated_record_count == 3
    assert response.latest_timestamp.endswith("+00:00")
    assert response.primary_hypothesis.confidence > 0
    assert len(response.alternatives) == 3
    assert response.primary_hypothesis.supporting_features


def test_failure_classification_history_is_stored() -> None:
    classifier = FailureModeClassifier()

    classifier.classify(
        FailureClassificationRequest(
            asset_id="P-101",
            records=_healthy_records(),
        )
    )

    history = classifier.history(
        "P-101"
    )

    assert history.asset_id == "P-101"
    assert history.model_version == MODEL_VERSION
    assert history.classification_count == 1


def test_failure_classification_api_model_classify_and_history() -> None:
    with isolated_classifier():
        with authorized_user("get_failure_classification_model"):
            model_response = client.get(
                "/failure-classification/model"
            )

        assert model_response.status_code == 200
        assert model_response.json()["model_version"] == MODEL_VERSION
        assert model_response.json()["rul_supported"] is False

        with authorized_user("classify_failure_mode"):
            classify_response = client.post(
                "/failure-classification/classify",
                json={
                    "asset_id": "P-101",
                    "records": [
                        record.model_dump()
                        for record in _bearing_degradation_records()
                    ],
                },
            )

        assert classify_response.status_code == 200
        assert (
            classify_response.json()["primary_hypothesis"]["failure_mode"]
            in {
                "bearing_damage",
                "lubrication_degradation",
            }
        )

        with authorized_user("get_failure_classification_history"):
            history_response = client.get(
                "/failure-classification/assets/P-101/history"
            )

        assert history_response.status_code == 200
        assert history_response.json()["classification_count"] == 1


def test_failure_classification_api_requires_authentication() -> None:
    response = client.get(
        "/failure-classification/model"
    )

    assert response.status_code == 401