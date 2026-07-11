from __future__ import annotations

from apps.api.asset_health.schemas import (
    AssetHealthHistoryResponse,
    AssetHealthInput,
    AssetHealthModelCard,
    AssetHealthReplayRequest,
    AssetHealthReplayResponse,
    AssetHealthScoreRequest,
    AssetHealthScoreResponse,
    HealthFactorContribution,
    HealthScoreDelta,
)


MODEL_VERSION = "asset-health-explainable-v1.0.0"
BASE_SCORE = 100.0
SCORING_METHOD = (
    "Explainable weighted risk deduction from 100. "
    "Every factor exposes input value, risk points, max risk points, "
    "and explanation."
)

FACTOR_WEIGHTS = {
    "sensor_anomaly_score": 22.0,
    "failure_probability": 18.0,
    "open_incident_severity": 15.0,
    "work_order_status": 12.0,
    "compliance_risk": 10.0,
    "asset_criticality": 8.0,
    "recent_failure_history": 8.0,
    "sensor_quality": 7.0,
}

INCIDENT_SEVERITY_POINTS = {
    "none": 0.0,
    "low": 3.0,
    "medium": 7.0,
    "high": 11.0,
    "critical": 15.0,
}

ASSET_CRITICALITY_POINTS = {
    "low": 2.0,
    "medium": 4.0,
    "high": 6.0,
    "critical": 8.0,
}


class ExplainableAssetHealthScorer:
    def __init__(self) -> None:
        self._history_by_asset: dict[
            str,
            list[AssetHealthScoreResponse],
        ] = {}

    def model_card(self) -> AssetHealthModelCard:
        return AssetHealthModelCard(
            model_name="PlantMind Explainable Asset Health Score",
            model_version=MODEL_VERSION,
            scoring_method=SCORING_METHOD,
            base_score=BASE_SCORE,
            factor_weights=FACTOR_WEIGHTS,
            hidden_score=False,
            notes=[
                "The score is not hidden or arbitrary.",
                "Health score = 100 minus visible risk contributions.",
                "Post-maintenance recovery raises the score only when factor risk decreases.",
                "RUL is intentionally not displayed.",
            ],
        )

    def score(
        self,
        request: AssetHealthScoreRequest,
    ) -> AssetHealthScoreResponse:
        previous = self._latest_score(
            request.reading.asset_id,
        )

        score = self._score_reading(
            reading=request.reading,
            previous_score=previous.health_score if previous else None,
        )

        self._history_by_asset.setdefault(
            request.reading.asset_id,
            [],
        ).append(score)

        return score

    def replay(
        self,
        request: AssetHealthReplayRequest,
    ) -> AssetHealthReplayResponse:
        scores: list[AssetHealthScoreResponse] = []
        previous_score: float | None = None

        for reading in sorted(
            request.readings,
            key=lambda item: item.timestamp,
        ):
            normalized_reading = reading.model_copy(
                update={
                    "asset_id": request.asset_id,
                }
            )

            score = self._score_reading(
                reading=normalized_reading,
                previous_score=previous_score,
            )

            scores.append(score)
            previous_score = score.health_score

        if scores:
            self._history_by_asset.setdefault(
                request.asset_id,
                [],
            ).extend(scores)

        return AssetHealthReplayResponse(
            asset_id=request.asset_id,
            model_version=MODEL_VERSION,
            score_count=len(scores),
            scores=scores,
        )

    def history(
        self,
        asset_id: str,
    ) -> AssetHealthHistoryResponse:
        scores = self._history_by_asset.get(
            asset_id,
            [],
        )

        return AssetHealthHistoryResponse(
            asset_id=asset_id,
            model_version=MODEL_VERSION,
            score_count=len(scores),
            scores=scores[-100:],
        )

    def _latest_score(
        self,
        asset_id: str,
    ) -> AssetHealthScoreResponse | None:
        scores = self._history_by_asset.get(
            asset_id,
            [],
        )

        if not scores:
            return None

        return scores[-1]

    def _score_reading(
        self,
        *,
        reading: AssetHealthInput,
        previous_score: float | None,
    ) -> AssetHealthScoreResponse:
        factors = self._factor_contributions(
            reading,
        )

        total_risk_points = round(
            sum(
                factor.risk_points
                for factor in factors
            ),
            4,
        )

        health_score = round(
            max(
                0.0,
                BASE_SCORE - total_risk_points,
            ),
            4,
        )

        return AssetHealthScoreResponse(
            asset_id=reading.asset_id,
            timestamp=reading.timestamp,
            model_version=MODEL_VERSION,
            scoring_method=SCORING_METHOD,
            base_score=BASE_SCORE,
            health_score=health_score,
            health_band=self._health_band(
                health_score,
            ),
            total_risk_points=total_risk_points,
            replay_state=reading.replay_state,
            factor_contributions=factors,
            score_delta=self._score_delta(
                previous_score=previous_score,
                current_score=health_score,
                factors=factors,
            ),
            explanation=(
                f"Health score is {health_score} because total visible "
                f"risk contribution is {total_risk_points} points out of "
                f"100. No hidden factor is applied."
            ),
        )

    def _factor_contributions(
        self,
        reading: AssetHealthInput,
    ) -> list[HealthFactorContribution]:
        return [
            self._sensor_anomaly_factor(
                reading,
            ),
            self._failure_probability_factor(
                reading,
            ),
            self._incident_severity_factor(
                reading,
            ),
            self._work_order_factor(
                reading,
            ),
            self._compliance_factor(
                reading,
            ),
            self._asset_criticality_factor(
                reading,
            ),
            self._recent_failure_factor(
                reading,
            ),
            self._sensor_quality_factor(
                reading,
            ),
        ]

    def _sensor_anomaly_factor(
        self,
        reading: AssetHealthInput,
    ) -> HealthFactorContribution:
        max_points = FACTOR_WEIGHTS["sensor_anomaly_score"]
        risk_points = round(
            reading.sensor_anomaly_score * max_points,
            4,
        )

        return HealthFactorContribution(
            factor_name="sensor_anomaly_score",
            label="Sensor anomaly score",
            input_value=reading.sensor_anomaly_score,
            risk_points=risk_points,
            max_risk_points=max_points,
            contribution_direction=self._direction(
                risk_points,
            ),
            explanation=(
                "Sensor anomaly risk = anomaly score multiplied by "
                f"{max_points} max points."
            ),
        )

    def _failure_probability_factor(
        self,
        reading: AssetHealthInput,
    ) -> HealthFactorContribution:
        max_points = FACTOR_WEIGHTS["failure_probability"]
        risk_points = round(
            reading.failure_probability * max_points,
            4,
        )

        return HealthFactorContribution(
            factor_name="failure_probability",
            label="Failure probability",
            input_value=reading.failure_probability,
            risk_points=risk_points,
            max_risk_points=max_points,
            contribution_direction=self._direction(
                risk_points,
            ),
            explanation=(
                "Failure-mode classifier probability is converted into "
                f"visible risk using {max_points} max points."
            ),
        )

    def _incident_severity_factor(
        self,
        reading: AssetHealthInput,
    ) -> HealthFactorContribution:
        max_points = FACTOR_WEIGHTS["open_incident_severity"]
        risk_points = INCIDENT_SEVERITY_POINTS[
            reading.open_incident_severity
        ]

        return HealthFactorContribution(
            factor_name="open_incident_severity",
            label="Open incident severity",
            input_value=reading.open_incident_severity,
            risk_points=risk_points,
            max_risk_points=max_points,
            contribution_direction=self._direction(
                risk_points,
            ),
            explanation=(
                "Open incident severity maps to fixed visible risk "
                "points: none=0, low=3, medium=7, high=11, critical=15."
            ),
        )

    def _work_order_factor(
        self,
        reading: AssetHealthInput,
    ) -> HealthFactorContribution:
        max_points = FACTOR_WEIGHTS["work_order_status"]
        risk_points = round(
            min(
                max_points,
                reading.open_work_orders * 1.2
                + reading.overdue_work_orders * 4.0,
            ),
            4,
        )

        return HealthFactorContribution(
            factor_name="work_order_status",
            label="Work-order status",
            input_value=(
                f"{reading.open_work_orders} open, "
                f"{reading.overdue_work_orders} overdue"
            ),
            risk_points=risk_points,
            max_risk_points=max_points,
            contribution_direction=self._direction(
                risk_points,
            ),
            explanation=(
                "Work-order risk = 1.2 points per open work order plus "
                "4 points per overdue work order, capped at 12."
            ),
        )

    def _compliance_factor(
        self,
        reading: AssetHealthInput,
    ) -> HealthFactorContribution:
        max_points = FACTOR_WEIGHTS["compliance_risk"]
        risk_points = round(
            reading.compliance_risk_score * max_points,
            4,
        )

        return HealthFactorContribution(
            factor_name="compliance_risk",
            label="Compliance risk",
            input_value=reading.compliance_risk_score,
            risk_points=risk_points,
            max_risk_points=max_points,
            contribution_direction=self._direction(
                risk_points,
            ),
            explanation=(
                "Compliance risk score is multiplied by "
                f"{max_points} max points."
            ),
        )

    def _asset_criticality_factor(
        self,
        reading: AssetHealthInput,
    ) -> HealthFactorContribution:
        max_points = FACTOR_WEIGHTS["asset_criticality"]
        risk_points = ASSET_CRITICALITY_POINTS[
            reading.asset_criticality
        ]

        return HealthFactorContribution(
            factor_name="asset_criticality",
            label="Asset criticality",
            input_value=reading.asset_criticality,
            risk_points=risk_points,
            max_risk_points=max_points,
            contribution_direction=self._direction(
                risk_points,
            ),
            explanation=(
                "Asset criticality is a visible baseline risk: "
                "low=2, medium=4, high=6, critical=8."
            ),
        )

    def _recent_failure_factor(
        self,
        reading: AssetHealthInput,
    ) -> HealthFactorContribution:
        max_points = FACTOR_WEIGHTS["recent_failure_history"]
        risk_points = round(
            min(
                max_points,
                reading.recent_failure_count * 2.5,
            ),
            4,
        )

        return HealthFactorContribution(
            factor_name="recent_failure_history",
            label="Recent failure history",
            input_value=reading.recent_failure_count,
            risk_points=risk_points,
            max_risk_points=max_points,
            contribution_direction=self._direction(
                risk_points,
            ),
            explanation=(
                "Recent failure risk = 2.5 points per recent failure, "
                "capped at 8."
            ),
        )

    def _sensor_quality_factor(
        self,
        reading: AssetHealthInput,
    ) -> HealthFactorContribution:
        max_points = FACTOR_WEIGHTS["sensor_quality"]
        risk_points = round(
            (1.0 - reading.sensor_quality_score) * max_points,
            4,
        )

        return HealthFactorContribution(
            factor_name="sensor_quality",
            label="Sensor quality",
            input_value=reading.sensor_quality_score,
            risk_points=risk_points,
            max_risk_points=max_points,
            contribution_direction=self._direction(
                risk_points,
            ),
            explanation=(
                "Sensor quality risk = missing quality portion multiplied "
                f"by {max_points} max points."
            ),
        )

    def _score_delta(
        self,
        *,
        previous_score: float | None,
        current_score: float,
        factors: list[HealthFactorContribution],
    ) -> HealthScoreDelta:
        if previous_score is None:
            return HealthScoreDelta(
                previous_score=None,
                current_score=current_score,
                delta=0.0,
                direction="initial",
                explanation=(
                    "Initial score. No previous score exists for comparison."
                ),
            )

        delta = round(
            current_score - previous_score,
            4,
        )

        if delta > 0:
            direction = "improved"
            movement = "improved"
        elif delta < 0:
            direction = "declined"
            movement = "declined"
        else:
            direction = "unchanged"
            movement = "did not change"

        largest_factor = max(
            factors,
            key=lambda factor: factor.risk_points,
        )

        return HealthScoreDelta(
            previous_score=previous_score,
            current_score=current_score,
            delta=delta,
            direction=direction,
            explanation=(
                f"Health score {movement} by {abs(delta)} points. "
                f"Largest current risk contributor is "
                f"{largest_factor.label} with "
                f"{largest_factor.risk_points} risk points."
            ),
        )

    def _health_band(
        self,
        score: float,
    ) -> str:
        if score >= 85:
            return "healthy"

        if score >= 70:
            return "watch"

        if score >= 50:
            return "degraded"

        return "critical"

    def _direction(
        self,
        risk_points: float,
    ) -> str:
        if risk_points > 0:
            return "lowers_health"

        return "neutral"