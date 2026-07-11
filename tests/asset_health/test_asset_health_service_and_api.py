from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi.testclient import TestClient

from apps.api.asset_health.schemas import (
    AssetHealthInput,
    AssetHealthReplayRequest,
    AssetHealthScoreRequest,
)
from apps.api.asset_health.service import (
    BASE_SCORE,
    FACTOR_WEIGHTS,
    MODEL_VERSION,
    SCORING_METHOD,
    ExplainableAssetHealthScorer,
)
from apps.api.main import app
from apps.api.routes import asset_health as asset_health_route


client = TestClient(app)


def _timestamp(index: int) -> str:
    return (
        datetime(
            2026,
            7,
            10,
            9,
            0,
            0,
            tzinfo=timezone.utc,
        )
        + timedelta(seconds=index * 10)
    ).isoformat()


def _healthy_reading(index: int = 0) -> AssetHealthInput:
    return AssetHealthInput(
        asset_id="P-101",
        timestamp=_timestamp(index),
        sensor_anomaly_score=0.05,
        failure_probability=0.05,
        open_incident_severity="none",
        open_work_orders=0,
        overdue_work_orders=0,
        compliance_risk_score=0.10,
        asset_criticality="high",
        recent_failure_count=0,
        sensor_quality_score=0.98,
        replay_state="normal_operation",
    )


def _degradation_reading(index: int = 1) -> AssetHealthInput:
    return AssetHealthInput(
        asset_id="P-101",
        timestamp=_timestamp(index),
        sensor_anomaly_score=0.82,
        failure_probability=0.75,
        open_incident_severity="high",
        open_work_orders=4,
        overdue_work_orders=2,
        compliance_risk_score=0.70,
        asset_criticality="high",
        recent_failure_count=2,
        sensor_quality_score=0.85,
        replay_state="bearing_degradation",
    )


def _recovery_reading(index: int = 2) -> AssetHealthInput:
    return AssetHealthInput(
        asset_id="P-101",
        timestamp=_timestamp(index),
        sensor_anomaly_score=0.12,
        failure_probability=0.18,
        open_incident_severity="low",
        open_work_orders=1,
        overdue_work_orders=0,
        compliance_risk_score=0.20,
        asset_criticality="high",
        recent_failure_count=1,
        sensor_quality_score=0.96,
        replay_state="maintenance_recovery",
    )


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        asset_health_route,
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
        "user_id": "asset-health-tester",
        "email": "asset-health@plantmind.local",
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
def isolated_scorer() -> Iterator[ExplainableAssetHealthScorer]:
    original_scorer = asset_health_route.asset_health_scorer
    scorer = ExplainableAssetHealthScorer()
    asset_health_route.asset_health_scorer = scorer

    try:
        yield scorer
    finally:
        asset_health_route.asset_health_scorer = original_scorer


def test_model_card_exposes_visible_factor_weights() -> None:
    scorer = ExplainableAssetHealthScorer()

    card = scorer.model_card()

    assert card.model_version == MODEL_VERSION
    assert card.scoring_method == SCORING_METHOD
    assert card.base_score == BASE_SCORE
    assert card.hidden_score is False
    assert card.factor_weights == FACTOR_WEIGHTS
    assert set(card.factor_weights.keys()) == {
        "sensor_anomaly_score",
        "failure_probability",
        "open_incident_severity",
        "work_order_status",
        "compliance_risk",
        "asset_criticality",
        "recent_failure_history",
        "sensor_quality",
    }


def test_health_score_has_all_factor_contributions() -> None:
    scorer = ExplainableAssetHealthScorer()

    response = scorer.score(
        AssetHealthScoreRequest(
            reading=_healthy_reading()
        )
    )

    factor_names = {
        factor.factor_name
        for factor in response.factor_contributions
    }

    assert response.model_version == MODEL_VERSION
    assert response.base_score == 100.0
    assert response.health_score > 85
    assert response.health_band == "healthy"
    assert len(response.factor_contributions) == 8
    assert factor_names == set(FACTOR_WEIGHTS.keys())
    assert "No hidden factor" in response.explanation


def test_total_risk_points_match_visible_contributions() -> None:
    scorer = ExplainableAssetHealthScorer()

    response = scorer.score(
        AssetHealthScoreRequest(
            reading=_degradation_reading()
        )
    )

    visible_risk = round(
        sum(
            factor.risk_points
            for factor in response.factor_contributions
        ),
        4,
    )

    assert response.total_risk_points == visible_risk
    assert response.health_score == round(
        100.0 - visible_risk,
        4,
    )

    for factor in response.factor_contributions:
        assert factor.explanation
        assert factor.max_risk_points == FACTOR_WEIGHTS[factor.factor_name]


def test_health_score_declines_during_degradation_replay() -> None:
    scorer = ExplainableAssetHealthScorer()

    response = scorer.replay(
        AssetHealthReplayRequest(
            asset_id="P-101",
            readings=[
                _healthy_reading(0),
                _degradation_reading(1),
            ],
        )
    )

    healthy = response.scores[0]
    degraded = response.scores[1]

    assert healthy.health_score > degraded.health_score
    assert degraded.health_band in {
        "degraded",
        "critical",
    }
    assert degraded.score_delta.direction == "declined"
    assert degraded.score_delta.explanation


def test_post_maintenance_recovery_raises_health_score() -> None:
    scorer = ExplainableAssetHealthScorer()

    response = scorer.replay(
        AssetHealthReplayRequest(
            asset_id="P-101",
            readings=[
                _healthy_reading(0),
                _degradation_reading(1),
                _recovery_reading(2),
            ],
        )
    )

    degraded = response.scores[1]
    recovered = response.scores[2]

    assert recovered.replay_state == "maintenance_recovery"
    assert recovered.health_score > degraded.health_score
    assert recovered.score_delta.direction == "improved"
    assert recovered.score_delta.explanation


def test_every_score_change_has_explanation() -> None:
    scorer = ExplainableAssetHealthScorer()

    response = scorer.replay(
        AssetHealthReplayRequest(
            asset_id="P-101",
            readings=[
                _healthy_reading(0),
                _degradation_reading(1),
                _recovery_reading(2),
            ],
        )
    )

    assert response.score_count == 3

    for score in response.scores:
        assert score.explanation
        assert score.score_delta.explanation
        assert score.factor_contributions


def test_history_is_stored_by_asset() -> None:
    scorer = ExplainableAssetHealthScorer()

    scorer.score(
        AssetHealthScoreRequest(
            reading=_healthy_reading()
        )
    )

    history = scorer.history(
        "P-101"
    )

    assert history.asset_id == "P-101"
    assert history.model_version == MODEL_VERSION
    assert history.score_count == 1


def test_asset_health_api_model_score_replay_and_history() -> None:
    with isolated_scorer():
        with authorized_user("get_asset_health_model"):
            model_response = client.get(
                "/asset-health/model"
            )

        assert model_response.status_code == 200
        assert model_response.json()["model_version"] == MODEL_VERSION
        assert model_response.json()["hidden_score"] is False

        with authorized_user("score_asset_health"):
            score_response = client.post(
                "/asset-health/score",
                json={
                    "reading": _healthy_reading().model_dump(),
                },
            )

        assert score_response.status_code == 200
        assert score_response.json()["health_band"] == "healthy"
        assert len(score_response.json()["factor_contributions"]) == 8

        with authorized_user("score_asset_health_replay"):
            replay_response = client.post(
                "/asset-health/replay",
                json={
                    "asset_id": "P-101",
                    "readings": [
                        _healthy_reading(0).model_dump(),
                        _degradation_reading(1).model_dump(),
                        _recovery_reading(2).model_dump(),
                    ],
                },
            )

        assert replay_response.status_code == 200
        assert replay_response.json()["score_count"] == 3
        assert (
            replay_response.json()["scores"][2]["score_delta"]["direction"]
            == "improved"
        )

        with authorized_user("get_asset_health_history"):
            history_response = client.get(
                "/asset-health/assets/P-101/history"
            )

        assert history_response.status_code == 200
        assert history_response.json()["score_count"] == 4


def test_asset_health_api_requires_authentication() -> None:
    response = client.get(
        "/asset-health/model"
    )

    assert response.status_code == 401