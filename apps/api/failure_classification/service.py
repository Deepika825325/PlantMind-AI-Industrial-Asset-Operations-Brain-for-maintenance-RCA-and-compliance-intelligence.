from __future__ import annotations

from dataclasses import dataclass

from apps.api.failure_classification.schemas import (
    FailureClassificationHistoryResponse,
    FailureClassificationModelCard,
    FailureClassificationRequest,
    FailureClassificationResponse,
    FailureHypothesis,
    FailureMode,
    FailureTelemetryRecord,
    FeatureEvidence,
)


MODEL_VERSION = "failure-classifier-heuristic-v1.0.0"
CONFIDENCE_METHOD = (
    "Heuristic confidence score based on deterministic industrial "
    "signal rules; not statistically calibrated."
)


@dataclass(frozen=True)
class FeatureSnapshot:
    latest_timestamp: str
    vibration: float | None
    temperature: float | None
    current: float | None
    rpm: float | None
    health_score: float | None
    anomaly_score: float | None
    data_quality: str
    vibration_delta: float
    temperature_delta: float
    current_delta: float
    rpm_delta: float
    rpm_drop: float


class FailureModeClassifier:
    def __init__(self) -> None:
        self._history_by_asset: dict[
            str,
            list[FailureClassificationResponse],
        ] = {}

    def model_card(self) -> FailureClassificationModelCard:
        return FailureClassificationModelCard(
            model_name="PlantMind P-101 Failure Mode Classifier",
            model_version=MODEL_VERSION,
            model_type="explainable_heuristic_classifier",
            supported_classes=[
                "healthy",
                "lubrication_degradation",
                "bearing_damage",
                "shaft_misalignment",
                "cavitation",
                "unknown_anomaly",
            ],
            confidence_method=CONFIDENCE_METHOD,
            live_plant_connected=False,
            rul_supported=False,
            notes=[
                "Designed for demo-grade failure-mode ranking.",
                "Does not display remaining useful life.",
                "Confidence is heuristic and clearly labelled.",
            ],
        )

    def classify(
        self,
        request: FailureClassificationRequest,
    ) -> FailureClassificationResponse:
        records = sorted(
            request.records,
            key=lambda record: record.sequence,
        )

        snapshot = self._snapshot(records)
        scores = self._score_modes(snapshot)

        ranked_modes = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        hypotheses = [
            self._hypothesis(
                mode=mode,
                confidence=confidence,
                snapshot=snapshot,
            )
            for mode, confidence in ranked_modes
        ]

        response = FailureClassificationResponse(
            asset_id=request.asset_id,
            model_version=MODEL_VERSION,
            confidence_method=CONFIDENCE_METHOD,
            evaluated_record_count=len(records),
            latest_timestamp=snapshot.latest_timestamp,
            primary_hypothesis=hypotheses[0],
            alternatives=hypotheses[1:4],
        )

        self._history_by_asset.setdefault(
            request.asset_id,
            [],
        ).append(response)

        return response

    def history(
        self,
        asset_id: str,
    ) -> FailureClassificationHistoryResponse:
        classifications = self._history_by_asset.get(
            asset_id,
            [],
        )

        return FailureClassificationHistoryResponse(
            asset_id=asset_id,
            model_version=MODEL_VERSION,
            classification_count=len(classifications),
            classifications=classifications[-50:],
        )

    def _snapshot(
        self,
        records: list[FailureTelemetryRecord],
    ) -> FeatureSnapshot:
        first = records[0]
        latest = records[-1]

        vibration_delta = self._delta(
            latest.vibration_mm_s,
            first.vibration_mm_s,
        )
        temperature_delta = self._delta(
            latest.bearing_temperature_deg_c,
            first.bearing_temperature_deg_c,
        )
        current_delta = self._delta(
            latest.motor_current_a,
            first.motor_current_a,
        )
        rpm_delta = self._delta(
            latest.rpm,
            first.rpm,
        )

        return FeatureSnapshot(
            latest_timestamp=latest.timestamp,
            vibration=latest.vibration_mm_s,
            temperature=latest.bearing_temperature_deg_c,
            current=latest.motor_current_a,
            rpm=latest.rpm,
            health_score=latest.health_score,
            anomaly_score=latest.anomaly_score,
            data_quality=latest.data_quality,
            vibration_delta=vibration_delta,
            temperature_delta=temperature_delta,
            current_delta=current_delta,
            rpm_delta=rpm_delta,
            rpm_drop=max(0.0, -rpm_delta),
        )

    def _score_modes(
        self,
        snapshot: FeatureSnapshot,
    ) -> dict[FailureMode, float]:
        vibration = snapshot.vibration or 0.0
        temperature = snapshot.temperature or 0.0
        current = snapshot.current or 0.0
        rpm_drop = snapshot.rpm_drop
        rpm_rise = max(0.0, snapshot.rpm_delta)
        anomaly = snapshot.anomaly_score or 0.0

        healthy = 0.94
        healthy -= 0.25 if vibration > 4.5 else 0.0
        healthy -= 0.25 if temperature > 78 else 0.0
        healthy -= 0.15 if current > 22 else 0.0
        healthy -= 0.20 if anomaly > 0.35 else 0.0
        healthy -= 0.15 if snapshot.data_quality != "good" else 0.0

        lubrication = 0.08
        lubrication += 0.28 if temperature > 78 else 0.0
        lubrication += 0.18 if vibration > 4.5 else 0.0
        lubrication += 0.14 if snapshot.temperature_delta > 8 else 0.0
        lubrication += 0.10 if snapshot.vibration_delta > 1.5 else 0.0
        lubrication += 0.08 if current > 21 else 0.0

        bearing = 0.07
        bearing += 0.35 if vibration > 7.1 else 0.0
        bearing += 0.20 if temperature > 82 else 0.0
        bearing += 0.15 if snapshot.vibration_delta > 2.5 else 0.0
        bearing += 0.10 if anomaly > 0.65 else 0.0

        misalignment = 0.06
        misalignment += 0.24 if vibration > 5.0 else 0.0
        misalignment += 0.22 if current > 22 else 0.0
        misalignment += 0.18 if rpm_drop > 12 else 0.0
        misalignment += 0.10 if temperature < 82 else 0.0

        cavitation = 0.05
        cavitation += 0.22 if vibration > 4.2 else 0.0
        cavitation += 0.18 if rpm_rise > 3 else 0.0
        cavitation += 0.14 if temperature < 78 else 0.0
        cavitation += 0.10 if current < 22 else 0.0
        cavitation += 0.08 if snapshot.vibration_delta > 1.0 else 0.0

        known_max = max(
            lubrication,
            bearing,
            misalignment,
            cavitation,
        )

        unknown = 0.05
        if anomaly >= 0.55 and known_max < 0.45:
            unknown = 0.78
        if snapshot.data_quality not in {"good", "stuck_sensor"} and known_max < 0.45:
            unknown = max(unknown, 0.72)
        if current > 30 and vibration < 4.0 and temperature < 75:
            unknown = max(unknown, 0.74)

        return {
            "healthy": self._clamp(healthy),
            "lubrication_degradation": self._clamp(lubrication),
            "bearing_damage": self._clamp(bearing),
            "shaft_misalignment": self._clamp(misalignment),
            "cavitation": self._clamp(cavitation),
            "unknown_anomaly": self._clamp(unknown),
        }

    def _hypothesis(
        self,
        *,
        mode: FailureMode,
        confidence: float,
        snapshot: FeatureSnapshot,
    ) -> FailureHypothesis:
        return FailureHypothesis(
            failure_mode=mode,
            label=self._label(mode),
            confidence=round(confidence, 4),
            supporting_features=self._supporting_features(
                mode,
                snapshot,
            ),
            contradictory_features=self._contradictory_features(
                mode,
                snapshot,
            ),
        )

    def _supporting_features(
        self,
        mode: FailureMode,
        snapshot: FeatureSnapshot,
    ) -> list[FeatureEvidence]:
        features: list[FeatureEvidence] = []

        def add(
            name: str,
            value: float | str | None,
            expected: str,
            explanation: str,
        ) -> None:
            features.append(
                FeatureEvidence(
                    feature_name=name,
                    feature_value=value,
                    expected_pattern=expected,
                    explanation=explanation,
                )
            )

        vibration = snapshot.vibration or 0.0
        temperature = snapshot.temperature or 0.0
        current = snapshot.current or 0.0
        anomaly = snapshot.anomaly_score or 0.0

        if mode == "healthy":
            if vibration <= 4.5:
                add("vibration_mm_s", vibration, "<= 4.5", "Vibration remains in the healthy operating band.")
            if temperature <= 78:
                add("bearing_temperature_deg_c", temperature, "<= 78", "Bearing temperature does not indicate overheating.")
            if anomaly < 0.35:
                add("anomaly_score", anomaly, "< 0.35", "ML anomaly score is low.")

        elif mode == "lubrication_degradation":
            if temperature > 78:
                add("bearing_temperature_deg_c", temperature, "> 78", "Elevated bearing temperature supports lubrication degradation.")
            if snapshot.temperature_delta > 8:
                add("window_temperature_delta", snapshot.temperature_delta, "> 8", "Temperature is increasing across the window.")
            if vibration > 4.5:
                add("vibration_mm_s", vibration, "> 4.5", "Vibration is above warning level.")

        elif mode == "bearing_damage":
            if vibration > 7.1:
                add("vibration_mm_s", vibration, "> 7.1", "Critical vibration strongly supports bearing damage.")
            if temperature > 82:
                add("bearing_temperature_deg_c", temperature, "> 82", "High bearing temperature supports bearing distress.")
            if snapshot.vibration_delta > 2.5:
                add("window_vibration_delta", snapshot.vibration_delta, "> 2.5", "Vibration is escalating quickly.")

        elif mode == "shaft_misalignment":
            if current > 22:
                add("motor_current_a", current, "> 22", "Elevated motor current is consistent with misalignment load.")
            if snapshot.rpm_drop > 12:
                add("rpm_drop", snapshot.rpm_drop, "> 12", "RPM drop supports mechanical drag or alignment issue.")
            if vibration > 5:
                add("vibration_mm_s", vibration, "> 5", "High vibration supports misalignment.")

        elif mode == "cavitation":
            if vibration > 4.2:
                add("vibration_mm_s", vibration, "> 4.2", "Moderate vibration rise can indicate cavitation.")
            if snapshot.rpm_delta > 3:
                add("rpm_delta", snapshot.rpm_delta, "> 3", "RPM rise with vibration can support cavitation-like instability.")
            if temperature < 78:
                add("bearing_temperature_deg_c", temperature, "< 78", "Temperature is not high enough for bearing/lubrication dominance.")

        elif mode == "unknown_anomaly":
            if anomaly >= 0.55:
                add("anomaly_score", anomaly, ">= 0.55", "Anomaly score is high but known failure signatures are weak.")
            if snapshot.data_quality != "good":
                add("data_quality", snapshot.data_quality, "not good", "Data quality issue may indicate unknown or sensor-side anomaly.")
            if current > 30:
                add("motor_current_a", current, "> 30", "Motor current is abnormal without a matching known signature.")

        return features

    def _contradictory_features(
        self,
        mode: FailureMode,
        snapshot: FeatureSnapshot,
    ) -> list[FeatureEvidence]:
        features: list[FeatureEvidence] = []

        def add(
            name: str,
            value: float | str | None,
            expected: str,
            explanation: str,
        ) -> None:
            features.append(
                FeatureEvidence(
                    feature_name=name,
                    feature_value=value,
                    expected_pattern=expected,
                    explanation=explanation,
                )
            )

        vibration = snapshot.vibration or 0.0
        temperature = snapshot.temperature or 0.0
        current = snapshot.current or 0.0

        if mode in {"lubrication_degradation", "bearing_damage"}:
            if temperature <= 78:
                add("bearing_temperature_deg_c", temperature, "> 78", "Temperature is not elevated enough for a strong bearing/lubrication hypothesis.")
            if vibration <= 4.5:
                add("vibration_mm_s", vibration, "> 4.5", "Vibration is not above warning level.")

        if mode == "shaft_misalignment":
            if current <= 22:
                add("motor_current_a", current, "> 22", "Motor current does not show strong alignment load.")
            if snapshot.rpm_drop <= 12:
                add("rpm_drop", snapshot.rpm_drop, "> 12", "RPM drop is not strong.")

        if mode == "cavitation":
            if temperature >= 78:
                add("bearing_temperature_deg_c", temperature, "< 78", "High temperature makes bearing/lubrication more likely than cavitation.")
            if snapshot.rpm_delta <= 3:
                add("rpm_delta", snapshot.rpm_delta, "> 3", "RPM rise is not strong.")

        if mode == "healthy":
            if vibration > 4.5:
                add("vibration_mm_s", vibration, "<= 4.5", "Vibration is above healthy warning level.")
            if temperature > 78:
                add("bearing_temperature_deg_c", temperature, "<= 78", "Bearing temperature is elevated.")

        return features

    def _label(
        self,
        mode: FailureMode,
    ) -> str:
        labels = {
            "healthy": "Healthy",
            "lubrication_degradation": "Lubrication degradation",
            "bearing_damage": "Bearing damage",
            "shaft_misalignment": "Shaft misalignment",
            "cavitation": "Cavitation",
            "unknown_anomaly": "Unknown anomaly",
        }

        return labels[mode]

    def _delta(
        self,
        latest: float | None,
        first: float | None,
    ) -> float:
        if latest is None or first is None:
            return 0.0

        return round(latest - first, 4)

    def _clamp(
        self,
        value: float,
    ) -> float:
        return round(
            max(
                0.0,
                min(0.95, value),
            ),
            4,
        )