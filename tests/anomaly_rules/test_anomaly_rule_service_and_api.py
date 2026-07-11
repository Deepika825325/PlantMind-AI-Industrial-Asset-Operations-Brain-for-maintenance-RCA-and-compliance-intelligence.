from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi.testclient import TestClient

from apps.api.anomaly_rules.schemas import (
    AnomalyEvaluationRequest,
    TelemetryRecordForRules,
)
from apps.api.anomaly_rules.service import (
    RULE_VERSION,
    AnomalyRuleService,
)
from apps.api.main import app
from apps.api.routes import anomalies as anomaly_route


client = TestClient(app)


def _record(
    sequence: int,
    *,
    vibration: float | None = 2.2,
    temperature: float | None = 63.0,
    current: float | None = 18.5,
    rpm: float | None = 1480.0,
) -> TelemetryRecordForRules:
    timestamp = datetime(
        2026,
        7,
        10,
        9,
        0,
        0,
        tzinfo=timezone.utc,
    ) + timedelta(seconds=sequence * 10)

    return TelemetryRecordForRules(
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


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        anomaly_route,
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
        "user_id": "anomaly-tester",
        "email": "anomaly@plantmind.local",
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
def isolated_anomaly_service() -> Iterator[AnomalyRuleService]:
    original_service = anomaly_route.anomaly_rule_service
    service = AnomalyRuleService()
    anomaly_route.anomaly_rule_service = service

    try:
        yield service
    finally:
        anomaly_route.anomaly_rule_service = original_service


def _evaluate(
    records: list[TelemetryRecordForRules],
) -> set[str]:
    service = AnomalyRuleService()

    response = service.evaluate(
        AnomalyEvaluationRequest(
            asset_id="P-101",
            records=records,
        )
    )

    assert response.rule_version == RULE_VERSION

    return {
        anomaly.rule_id
        for anomaly in response.anomalies
    }


def test_rule_catalog_contains_required_day19_rules() -> None:
    service = AnomalyRuleService()

    catalog = service.list_rules()

    rule_types = {
        rule.rule_type
        for rule in catalog.rules
    }

    assert catalog.rule_version == RULE_VERSION
    assert "threshold_breach" in rule_types
    assert "rate_of_change_breach" in rule_types
    assert "persistence_rule" in rule_types
    assert "missing_signal" in rule_types
    assert "stuck_sensor" in rule_types
    assert "impossible_value" in rule_types
    assert "combined_signal_rule" in rule_types


def test_threshold_breach_rules_produce_anomaly_records() -> None:
    rule_ids = _evaluate(
        [
            _record(0, vibration=2.2),
            _record(1, vibration=5.0),
            _record(2, vibration=7.8),
        ]
    )

    assert "RULE-VIB-WARNING-THRESHOLD" in rule_ids
    assert "RULE-VIB-CRITICAL-THRESHOLD" in rule_ids


def test_rate_of_change_rule_detects_sudden_vibration_rise() -> None:
    rule_ids = _evaluate(
        [
            _record(0, vibration=2.2),
            _record(1, vibration=4.1),
        ]
    )

    assert "RULE-VIB-RATE-OF-CHANGE" in rule_ids


def test_persistence_rules_detect_warning_and_critical_windows() -> None:
    rule_ids = _evaluate(
        [
            _record(0, vibration=7.5),
            _record(1, vibration=7.6),
            _record(2, vibration=7.7),
            _record(3, vibration=7.8),
        ]
    )

    assert "RULE-VIB-PERSISTENT-WARNING" in rule_ids
    assert "RULE-VIB-PERSISTENT-CRITICAL" in rule_ids


def test_missing_signal_rule_detects_missing_motor_current() -> None:
    rule_ids = _evaluate(
        [
            _record(0, current=None),
            _record(1, current=None),
        ]
    )

    assert "RULE-MISSING-SIGNAL" in rule_ids


def test_stuck_sensor_rule_detects_flat_signal_window() -> None:
    rule_ids = _evaluate(
        [
            _record(index, vibration=3.3)
            for index in range(5)
        ]
    )

    assert "RULE-STUCK-SENSOR" in rule_ids


def test_impossible_value_rule_detects_physical_impossibility() -> None:
    rule_ids = _evaluate(
        [
            _record(0, vibration=-1.0),
            _record(1, rpm=0.0),
        ]
    )

    assert "RULE-IMPOSSIBLE-VALUE" in rule_ids


def test_combined_vibration_temperature_rule_detects_joint_risk() -> None:
    rule_ids = _evaluate(
        [
            _record(
                0,
                vibration=5.2,
                temperature=82.0,
            ),
        ]
    )

    assert "RULE-COMBINED-VIB-TEMP" in rule_ids


def test_duplicate_alerts_are_suppressed() -> None:
    service = AnomalyRuleService()

    response = service.evaluate(
        AnomalyEvaluationRequest(
            asset_id="P-101",
            records=[
                _record(0, vibration=5.2),
                _record(1, vibration=5.3),
                _record(2, vibration=5.4),
                _record(3, vibration=5.5),
            ],
        )
    )

    warning_threshold_alerts = [
        anomaly
        for anomaly in response.anomalies
        if anomaly.rule_id == "RULE-VIB-WARNING-THRESHOLD"
    ]

    assert len(warning_threshold_alerts) == 1
    assert response.duplicate_alerts_suppressed >= 0


def test_rule_version_is_recorded_on_every_anomaly() -> None:
    service = AnomalyRuleService()

    response = service.evaluate(
        AnomalyEvaluationRequest(
            asset_id="P-101",
            records=[
                _record(0, vibration=7.8),
                _record(1, vibration=7.9),
            ],
        )
    )

    assert response.anomalies

    for anomaly in response.anomalies:
        assert anomaly.rule_version == RULE_VERSION


def test_anomaly_api_evaluate_rules_and_history() -> None:
    with isolated_anomaly_service():
        with authorized_user("evaluate_anomaly_rules"):
            evaluate_response = client.post(
                "/anomalies/evaluate",
                json={
                    "asset_id": "P-101",
                    "records": [
                        _record(0, vibration=7.8).model_dump(),
                        _record(1, vibration=7.9).model_dump(),
                    ],
                },
            )

        assert evaluate_response.status_code == 200
        assert evaluate_response.json()["anomaly_count"] > 0

        with authorized_user("get_asset_anomaly_history"):
            history_response = client.get(
                "/anomalies/assets/P-101"
            )

        assert history_response.status_code == 200
        assert history_response.json()["anomaly_count"] > 0

        with authorized_user("list_anomaly_rules"):
            rules_response = client.get(
                "/anomalies/rules"
            )

        assert rules_response.status_code == 200
        assert rules_response.json()["rule_version"] == RULE_VERSION


def test_anomaly_api_requires_authentication() -> None:
    response = client.get(
        "/anomalies/rules"
    )

    assert response.status_code == 401