from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

from apps.api.ml_anomaly.schemas import (
    ContributingFeature,
    MlAnomalyPrediction,
    MlAnomalyPredictionRequest,
    MlAnomalyPredictionResponse,
    MlModelCardResponse,
    MlPredictionHistoryResponse,
    MlTelemetryRecord,
)


MODEL_NAME = "P-101 Multivariate Forecast Residual Model"
MODEL_VERSION = "p101-multivariate-residual-v1.0.0"
FEATURE_VERSION = "p101-window-features-v1.0.0"
THRESHOLD_VERSION = "p101-thresholds-v1.0.0"

WARNING_THRESHOLD = 0.35
CRITICAL_THRESHOLD = 0.75


@dataclass(frozen=True)
class FeatureBaseline:
    baseline: float
    scale: float
    weight: float


FEATURE_BASELINES = {
    "vibration_mm_s": FeatureBaseline(
        baseline=2.25,
        scale=4.85,
        weight=0.35,
    ),
    "bearing_temperature_deg_c": FeatureBaseline(
        baseline=63.5,
        scale=28.0,
        weight=0.30,
    ),
    "motor_current_a": FeatureBaseline(
        baseline=18.6,
        scale=5.5,
        weight=0.20,
    ),
    "rpm": FeatureBaseline(
        baseline=1480.0,
        scale=80.0,
        weight=0.15,
    ),
}


class P101MultivariateAnomalyModel:
    def __init__(self) -> None:
        self._history_by_asset: dict[
            str,
            list[MlAnomalyPrediction],
        ] = {}

    def model_card(self) -> MlModelCardResponse:
        return MlModelCardResponse(
            model_name=MODEL_NAME,
            model_version=MODEL_VERSION,
            feature_version=FEATURE_VERSION,
            threshold_version=THRESHOLD_VERSION,
            asset_id="P-101",
            model_type="deterministic_multivariate_residual",
            training_source="Generated historical replay baseline",
            live_plant_connected=False,
            input_features=[
                "windowed_vibration_mm_s",
                "windowed_bearing_temperature_deg_c",
                "windowed_motor_current_a",
                "windowed_rpm",
            ],
            warning_threshold=WARNING_THRESHOLD,
            critical_threshold=CRITICAL_THRESHOLD,
            reproducible=True,
        )

    def predict(
        self,
        request: MlAnomalyPredictionRequest,
    ) -> MlAnomalyPredictionResponse:
        started_at = time.perf_counter()

        records = sorted(
            request.records,
            key=lambda record: record.sequence,
        )

        predictions: list[MlAnomalyPrediction] = []

        for index, record in enumerate(records):
            window = records[
                max(0, index - request.window_size + 1) :
                index + 1
            ]

            prediction = self._predict_record(
                record=record,
                window=window,
                started_at=started_at,
            )

            predictions.append(prediction)

        if predictions:
            self._history_by_asset.setdefault(
                request.asset_id,
                [],
            ).extend(predictions)

        return MlAnomalyPredictionResponse(
            asset_id=request.asset_id,
            model_version=MODEL_VERSION,
            feature_version=FEATURE_VERSION,
            threshold_version=THRESHOLD_VERSION,
            prediction_count=len(predictions),
            predictions=predictions,
        )

    def prediction_history(
        self,
        asset_id: str,
    ) -> MlPredictionHistoryResponse:
        predictions = self._history_by_asset.get(
            asset_id,
            [],
        )

        return MlPredictionHistoryResponse(
            asset_id=asset_id,
            model_version=MODEL_VERSION,
            prediction_count=len(predictions),
            predictions=predictions[-100:],
        )

    def _predict_record(
        self,
        *,
        record: MlTelemetryRecord,
        window: list[MlTelemetryRecord],
        started_at: float,
    ) -> MlAnomalyPrediction:
        feature_contributions = (
            self._point_residual_features(record)
            + self._window_trend_features(window)
        )

        total_score = round(
            min(
                1.0,
                sum(
                    feature.contribution
                    for feature in feature_contributions
                ),
            ),
            4,
        )

        label = self._label_for_score(total_score)

        ranked_features = sorted(
            feature_contributions,
            key=lambda feature: feature.contribution,
            reverse=True,
        )

        contributing_features = [
            feature
            for feature in ranked_features
            if feature.contribution > 0
        ][:6]

        prediction_latency_ms = round(
            max(
                0.001,
                (time.perf_counter() - started_at) * 1000,
            ),
            4,
        )

        return MlAnomalyPrediction(
            prediction_id=self._prediction_id(
                record=record,
                anomaly_score=total_score,
            ),
            asset_id=record.asset_id,
            sequence=record.sequence,
            prediction_timestamp=record.timestamp,
            model_version=MODEL_VERSION,
            feature_version=FEATURE_VERSION,
            threshold_version=THRESHOLD_VERSION,
            anomaly_score=total_score,
            anomaly_label=label,
            contributing_features=contributing_features,
            prediction_latency_ms=prediction_latency_ms,
        )

    def _point_residual_features(
        self,
        record: MlTelemetryRecord,
    ) -> list[ContributingFeature]:
        return [
            self._feature(
                feature_name="vibration_mm_s",
                feature_value=record.vibration_mm_s,
                baseline=FEATURE_BASELINES["vibration_mm_s"],
                positive_only=True,
            ),
            self._feature(
                feature_name="bearing_temperature_deg_c",
                feature_value=record.bearing_temperature_deg_c,
                baseline=FEATURE_BASELINES[
                    "bearing_temperature_deg_c"
                ],
                positive_only=True,
            ),
            self._feature(
                feature_name="motor_current_a",
                feature_value=record.motor_current_a,
                baseline=FEATURE_BASELINES["motor_current_a"],
                positive_only=True,
            ),
            self._feature(
                feature_name="rpm_deviation",
                feature_value=record.rpm,
                baseline=FEATURE_BASELINES["rpm"],
                positive_only=False,
            ),
        ]

    def _window_trend_features(
        self,
        window: list[MlTelemetryRecord],
    ) -> list[ContributingFeature]:
        if len(window) < 2:
            return []

        first = window[0]
        latest = window[-1]

        vibration_delta = (
            latest.vibration_mm_s - first.vibration_mm_s
        )
        temperature_delta = (
            latest.bearing_temperature_deg_c
            - first.bearing_temperature_deg_c
        )
        current_delta = (
            latest.motor_current_a - first.motor_current_a
        )
        rpm_drop = first.rpm - latest.rpm

        return [
            self._trend_feature(
                feature_name="window_vibration_delta",
                feature_value=vibration_delta,
                baseline_value=0.0,
                scale=5.5,
                weight=0.12,
            ),
            self._trend_feature(
                feature_name="window_temperature_delta",
                feature_value=temperature_delta,
                baseline_value=0.0,
                scale=24.0,
                weight=0.10,
            ),
            self._trend_feature(
                feature_name="window_current_delta",
                feature_value=current_delta,
                baseline_value=0.0,
                scale=4.0,
                weight=0.08,
            ),
            self._trend_feature(
                feature_name="window_rpm_drop",
                feature_value=rpm_drop,
                baseline_value=0.0,
                scale=60.0,
                weight=0.05,
            ),
        ]

    def _feature(
        self,
        *,
        feature_name: str,
        feature_value: float,
        baseline: FeatureBaseline,
        positive_only: bool,
    ) -> ContributingFeature:
        deviation = (
            feature_value - baseline.baseline
        ) / baseline.scale

        if positive_only:
            normalized_deviation = max(
                0.0,
                deviation,
            )
        else:
            normalized_deviation = abs(deviation)

        contribution = round(
            min(
                baseline.weight,
                normalized_deviation * baseline.weight,
            ),
            4,
        )

        return ContributingFeature(
            feature_name=feature_name,
            feature_value=round(feature_value, 4),
            baseline_value=round(baseline.baseline, 4),
            normalized_deviation=round(
                normalized_deviation,
                4,
            ),
            contribution=contribution,
        )

    def _trend_feature(
        self,
        *,
        feature_name: str,
        feature_value: float,
        baseline_value: float,
        scale: float,
        weight: float,
    ) -> ContributingFeature:
        normalized_deviation = max(
            0.0,
            feature_value / scale,
        )

        contribution = round(
            min(
                weight,
                normalized_deviation * weight,
            ),
            4,
        )

        return ContributingFeature(
            feature_name=feature_name,
            feature_value=round(feature_value, 4),
            baseline_value=round(baseline_value, 4),
            normalized_deviation=round(
                normalized_deviation,
                4,
            ),
            contribution=contribution,
        )

    def _label_for_score(
        self,
        score: float,
    ) -> str:
        if score >= CRITICAL_THRESHOLD:
            return "critical"

        if score >= WARNING_THRESHOLD:
            return "warning"

        return "normal"

    def _prediction_id(
        self,
        *,
        record: MlTelemetryRecord,
        anomaly_score: float,
    ) -> str:
        digest = hashlib.sha256(
            (
                f"{record.asset_id}:"
                f"{record.sequence}:"
                f"{record.timestamp}:"
                f"{anomaly_score}:"
                f"{MODEL_VERSION}:"
                f"{FEATURE_VERSION}:"
                f"{THRESHOLD_VERSION}"
            ).encode("utf-8")
        ).hexdigest()[:12]

        return f"MLANOM-{digest}"