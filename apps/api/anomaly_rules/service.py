from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

from apps.api.anomaly_rules.schemas import (
    AnomalyEvaluationRequest,
    AnomalyEvaluationResponse,
    AnomalyRecord,
    AnomalyRuleDefinition,
    AnomalyRuleType,
    AssetAnomalyHistoryResponse,
    RuleCatalogResponse,
    TelemetryRecordForRules,
)


RULE_VERSION = "telemetry-rules-v1.0.0"


@dataclass(frozen=True)
class _CandidateAlert:
    rule_id: str
    rule_type: AnomalyRuleType
    severity: str
    asset_id: str
    timestamp: str
    sequence: int
    metric: str
    observed_value: float | None
    threshold: float | None
    message: str
    deduplication_key: str
    contributing_records: list[int]


class AnomalyRuleService:
    def __init__(self) -> None:
        self._history_by_asset: dict[str, list[AnomalyRecord]] = {}

    def list_rules(self) -> RuleCatalogResponse:
        rules = self._rules()

        return RuleCatalogResponse(
            rule_version=RULE_VERSION,
            total_rules=len(rules),
            rules=rules,
        )

    def get_asset_history(
        self,
        asset_id: str,
    ) -> AssetAnomalyHistoryResponse:
        anomalies = self._history_by_asset.get(
            asset_id,
            [],
        )

        return AssetAnomalyHistoryResponse(
            asset_id=asset_id,
            rule_version=RULE_VERSION,
            anomaly_count=len(anomalies),
            anomalies=anomalies,
        )

    def evaluate(
        self,
        request: AnomalyEvaluationRequest,
    ) -> AnomalyEvaluationResponse:
        records = sorted(
            request.records,
            key=lambda record: record.sequence,
        )

        candidates: list[_CandidateAlert] = []

        self._evaluate_threshold_breaches(
            records,
            candidates,
        )
        self._evaluate_rate_of_change(
            records,
            candidates,
        )
        self._evaluate_persistence_rules(
            records,
            candidates,
        )
        self._evaluate_missing_signals(
            records,
            candidates,
        )
        self._evaluate_stuck_sensors(
            records,
            candidates,
        )
        self._evaluate_impossible_values(
            records,
            candidates,
        )
        self._evaluate_combined_signal_rules(
            records,
            candidates,
        )

        anomalies: list[AnomalyRecord] = []
        seen_keys: set[str] = set()
        duplicate_count = 0

        for candidate in candidates:
            if (
                request.suppress_duplicates
                and candidate.deduplication_key in seen_keys
            ):
                duplicate_count += 1
                continue

            seen_keys.add(candidate.deduplication_key)
            anomalies.append(
                self._candidate_to_record(
                    candidate
                )
            )

        if anomalies:
            self._history_by_asset.setdefault(
                request.asset_id,
                [],
            ).extend(anomalies)

        return AnomalyEvaluationResponse(
            asset_id=request.asset_id,
            rule_version=RULE_VERSION,
            evaluated_record_count=len(records),
            rules_evaluated=len(self._rules()),
            anomaly_count=len(anomalies),
            duplicate_alerts_suppressed=duplicate_count,
            anomalies=anomalies,
        )

    def _rules(self) -> list[AnomalyRuleDefinition]:
        return [
            AnomalyRuleDefinition(
                rule_id="RULE-VIB-WARNING-THRESHOLD",
                rule_version=RULE_VERSION,
                rule_type="threshold_breach",
                name="Vibration warning threshold",
                severity="warning",
                description="Single-record vibration warning threshold.",
                condition="vibration_mm_s > 4.5",
            ),
            AnomalyRuleDefinition(
                rule_id="RULE-VIB-CRITICAL-THRESHOLD",
                rule_version=RULE_VERSION,
                rule_type="threshold_breach",
                name="Vibration critical threshold",
                severity="critical",
                description="Single-record vibration critical threshold.",
                condition="vibration_mm_s > 7.1",
            ),
            AnomalyRuleDefinition(
                rule_id="RULE-VIB-RATE-OF-CHANGE",
                rule_version=RULE_VERSION,
                rule_type="rate_of_change_breach",
                name="Vibration rate-of-change breach",
                severity="warning",
                description="Detects sudden vibration rise between consecutive records.",
                condition="delta vibration_mm_s >= 1.5",
            ),
            AnomalyRuleDefinition(
                rule_id="RULE-VIB-PERSISTENT-WARNING",
                rule_version=RULE_VERSION,
                rule_type="persistence_rule",
                name="Persistent vibration warning",
                severity="warning",
                description="Vibration remains above warning threshold for 30 seconds.",
                condition="vibration_mm_s > 4.5 for >= 30 seconds",
            ),
            AnomalyRuleDefinition(
                rule_id="RULE-VIB-PERSISTENT-CRITICAL",
                rule_version=RULE_VERSION,
                rule_type="persistence_rule",
                name="Persistent vibration critical",
                severity="critical",
                description="Vibration remains above critical threshold for 10 seconds.",
                condition="vibration_mm_s > 7.1 for >= 10 seconds",
            ),
            AnomalyRuleDefinition(
                rule_id="RULE-MISSING-SIGNAL",
                rule_version=RULE_VERSION,
                rule_type="missing_signal",
                name="Missing signal",
                severity="warning",
                description="Required sensor signal is missing.",
                condition="required metric is null or absent",
            ),
            AnomalyRuleDefinition(
                rule_id="RULE-STUCK-SENSOR",
                rule_version=RULE_VERSION,
                rule_type="stuck_sensor",
                name="Stuck sensor",
                severity="warning",
                description="Signal remains exactly unchanged for a sustained window.",
                condition="same value for 5 consecutive records",
            ),
            AnomalyRuleDefinition(
                rule_id="RULE-IMPOSSIBLE-VALUE",
                rule_version=RULE_VERSION,
                rule_type="impossible_value",
                name="Impossible sensor value",
                severity="critical",
                description="Detects physically impossible telemetry values.",
                condition="negative vibration/current/rpm or extreme bearing temperature",
            ),
            AnomalyRuleDefinition(
                rule_id="RULE-COMBINED-VIB-TEMP",
                rule_version=RULE_VERSION,
                rule_type="combined_signal_rule",
                name="Combined vibration and temperature rule",
                severity="critical",
                description="Detects joint vibration and bearing temperature escalation.",
                condition="vibration_mm_s > 4.5 and bearing_temperature_deg_c > 78",
            ),
        ]

    def _evaluate_threshold_breaches(
        self,
        records: list[TelemetryRecordForRules],
        candidates: list[_CandidateAlert],
    ) -> None:
        warning_added = False
        critical_added = False

        for record in records:
            vibration = record.vibration_mm_s

            if vibration is None:
                continue

            if vibration > 7.1 and not critical_added:
                candidates.append(
                    self._candidate(
                        rule_id="RULE-VIB-CRITICAL-THRESHOLD",
                        rule_type="threshold_breach",
                        severity="critical",
                        record=record,
                        metric="vibration_mm_s",
                        observed_value=vibration,
                        threshold=7.1,
                        message="Vibration exceeded the critical threshold.",
                        deduplication_key=f"{record.asset_id}:threshold:vibration:critical",
                    )
                )
                critical_added = True

            if vibration > 4.5 and not warning_added:
                candidates.append(
                    self._candidate(
                        rule_id="RULE-VIB-WARNING-THRESHOLD",
                        rule_type="threshold_breach",
                        severity="warning",
                        record=record,
                        metric="vibration_mm_s",
                        observed_value=vibration,
                        threshold=4.5,
                        message="Vibration exceeded the warning threshold.",
                        deduplication_key=f"{record.asset_id}:threshold:vibration:warning",
                    )
                )
                warning_added = True

    def _evaluate_rate_of_change(
        self,
        records: list[TelemetryRecordForRules],
        candidates: list[_CandidateAlert],
    ) -> None:
        for previous, current in zip(
            records,
            records[1:],
            strict=False,
        ):
            if (
                previous.vibration_mm_s is None
                or current.vibration_mm_s is None
            ):
                continue

            delta = current.vibration_mm_s - previous.vibration_mm_s

            if delta >= 1.5:
                candidates.append(
                    self._candidate(
                        rule_id="RULE-VIB-RATE-OF-CHANGE",
                        rule_type="rate_of_change_breach",
                        severity="warning",
                        record=current,
                        metric="vibration_mm_s",
                        observed_value=round(delta, 4),
                        threshold=1.5,
                        message="Vibration increased too quickly between consecutive records.",
                        deduplication_key=f"{current.asset_id}:rate:vibration",
                        contributing_records=[
                            previous.sequence,
                            current.sequence,
                        ],
                    )
                )
                return

    def _evaluate_persistence_rules(
        self,
        records: list[TelemetryRecordForRules],
        candidates: list[_CandidateAlert],
    ) -> None:
        self._evaluate_persistent_threshold(
            records=records,
            candidates=candidates,
            rule_id="RULE-VIB-PERSISTENT-WARNING",
            severity="warning",
            threshold=4.5,
            min_duration_seconds=30,
        )

        self._evaluate_persistent_threshold(
            records=records,
            candidates=candidates,
            rule_id="RULE-VIB-PERSISTENT-CRITICAL",
            severity="critical",
            threshold=7.1,
            min_duration_seconds=10,
        )

    def _evaluate_persistent_threshold(
        self,
        *,
        records: list[TelemetryRecordForRules],
        candidates: list[_CandidateAlert],
        rule_id: str,
        severity: str,
        threshold: float,
        min_duration_seconds: int,
    ) -> None:
        window: list[TelemetryRecordForRules] = []

        for record in records:
            vibration = record.vibration_mm_s

            if vibration is None or vibration <= threshold:
                window = []
                continue

            window.append(record)

            if len(window) < 2:
                continue

            duration = self._seconds_between(
                window[0].timestamp,
                window[-1].timestamp,
            )

            if duration >= min_duration_seconds:
                candidates.append(
                    self._candidate(
                        rule_id=rule_id,
                        rule_type="persistence_rule",
                        severity=severity,
                        record=record,
                        metric="vibration_mm_s",
                        observed_value=vibration,
                        threshold=threshold,
                        message=(
                            "Vibration persisted above "
                            f"{threshold} mm/s for at least "
                            f"{min_duration_seconds} seconds."
                        ),
                        deduplication_key=(
                            f"{record.asset_id}:persistence:"
                            f"vibration:{severity}"
                        ),
                        contributing_records=[
                            item.sequence
                            for item in window
                        ],
                    )
                )
                return

    def _evaluate_missing_signals(
        self,
        records: list[TelemetryRecordForRules],
        candidates: list[_CandidateAlert],
    ) -> None:
        required_metrics = [
            "vibration_mm_s",
            "bearing_temperature_deg_c",
            "motor_current_a",
            "rpm",
        ]

        for record in records:
            for metric in required_metrics:
                if getattr(record, metric) is not None:
                    continue

                candidates.append(
                    self._candidate(
                        rule_id="RULE-MISSING-SIGNAL",
                        rule_type="missing_signal",
                        severity="warning",
                        record=record,
                        metric=metric,
                        observed_value=None,
                        threshold=None,
                        message=f"Required telemetry signal is missing: {metric}.",
                        deduplication_key=f"{record.asset_id}:missing:{metric}",
                    )
                )

    def _evaluate_stuck_sensors(
        self,
        records: list[TelemetryRecordForRules],
        candidates: list[_CandidateAlert],
    ) -> None:
        metrics = [
            "vibration_mm_s",
            "bearing_temperature_deg_c",
            "motor_current_a",
        ]

        window_size = 5

        for metric in metrics:
            values: list[float] = []
            sequences: list[int] = []

            for record in records:
                value = getattr(record, metric)

                if value is None:
                    values = []
                    sequences = []
                    continue

                values.append(round(value, 4))
                sequences.append(record.sequence)

                if len(values) > window_size:
                    values.pop(0)
                    sequences.pop(0)

                if (
                    len(values) == window_size
                    and len(set(values)) == 1
                ):
                    candidates.append(
                        self._candidate(
                            rule_id="RULE-STUCK-SENSOR",
                            rule_type="stuck_sensor",
                            severity="warning",
                            record=record,
                            metric=metric,
                            observed_value=value,
                            threshold=None,
                            message=f"Sensor appears stuck for metric: {metric}.",
                            deduplication_key=f"{record.asset_id}:stuck:{metric}",
                            contributing_records=sequences.copy(),
                        )
                    )
                    break

    def _evaluate_impossible_values(
        self,
        records: list[TelemetryRecordForRules],
        candidates: list[_CandidateAlert],
    ) -> None:
        for record in records:
            checks = [
                (
                    "vibration_mm_s",
                    record.vibration_mm_s,
                    lambda value: value < 0,
                    0.0,
                ),
                (
                    "bearing_temperature_deg_c",
                    record.bearing_temperature_deg_c,
                    lambda value: value < -20 or value > 160,
                    160.0,
                ),
                (
                    "motor_current_a",
                    record.motor_current_a,
                    lambda value: value < 0,
                    0.0,
                ),
                (
                    "rpm",
                    record.rpm,
                    lambda value: value <= 0,
                    0.0,
                ),
            ]

            for metric, value, predicate, threshold in checks:
                if value is None or not predicate(value):
                    continue

                candidates.append(
                    self._candidate(
                        rule_id="RULE-IMPOSSIBLE-VALUE",
                        rule_type="impossible_value",
                        severity="critical",
                        record=record,
                        metric=metric,
                        observed_value=value,
                        threshold=threshold,
                        message=f"Impossible telemetry value detected for {metric}.",
                        deduplication_key=f"{record.asset_id}:impossible:{metric}",
                    )
                )

    def _evaluate_combined_signal_rules(
        self,
        records: list[TelemetryRecordForRules],
        candidates: list[_CandidateAlert],
    ) -> None:
        for record in records:
            vibration = record.vibration_mm_s
            temperature = record.bearing_temperature_deg_c

            if vibration is None or temperature is None:
                continue

            if vibration > 4.5 and temperature > 78:
                candidates.append(
                    self._candidate(
                        rule_id="RULE-COMBINED-VIB-TEMP",
                        rule_type="combined_signal_rule",
                        severity="critical",
                        record=record,
                        metric="vibration_mm_s,bearing_temperature_deg_c",
                        observed_value=round(vibration + temperature, 4),
                        threshold=None,
                        message=(
                            "Combined vibration and bearing temperature "
                            "pattern indicates high-risk mechanical degradation."
                        ),
                        deduplication_key=f"{record.asset_id}:combined:vibration-temperature",
                        contributing_records=[record.sequence],
                    )
                )
                return

    def _candidate(
        self,
        *,
        rule_id: str,
        rule_type: AnomalyRuleType,
        severity: str,
        record: TelemetryRecordForRules,
        metric: str,
        observed_value: float | None,
        threshold: float | None,
        message: str,
        deduplication_key: str,
        contributing_records: list[int] | None = None,
    ) -> _CandidateAlert:
        return _CandidateAlert(
            rule_id=rule_id,
            rule_type=rule_type,
            severity=severity,
            asset_id=record.asset_id,
            timestamp=record.timestamp,
            sequence=record.sequence,
            metric=metric,
            observed_value=observed_value,
            threshold=threshold,
            message=message,
            deduplication_key=deduplication_key,
            contributing_records=contributing_records
            or [record.sequence],
        )

    def _candidate_to_record(
        self,
        candidate: _CandidateAlert,
    ) -> AnomalyRecord:
        digest = hashlib.sha256(
            (
                f"{candidate.deduplication_key}:"
                f"{candidate.sequence}:"
                f"{RULE_VERSION}"
            ).encode("utf-8")
        ).hexdigest()[:12]

        return AnomalyRecord(
            anomaly_id=f"ANOM-{digest}",
            rule_id=candidate.rule_id,
            rule_version=RULE_VERSION,
            rule_type=candidate.rule_type,
            severity=candidate.severity,
            asset_id=candidate.asset_id,
            timestamp=candidate.timestamp,
            sequence=candidate.sequence,
            metric=candidate.metric,
            observed_value=candidate.observed_value,
            threshold=candidate.threshold,
            message=candidate.message,
            deduplication_key=candidate.deduplication_key,
            contributing_records=candidate.contributing_records,
        )

    def _seconds_between(
        self,
        start: str,
        end: str,
    ) -> float:
        try:
            start_dt = datetime.fromisoformat(
                start.replace("Z", "+00:00")
            )
            end_dt = datetime.fromisoformat(
                end.replace("Z", "+00:00")
            )

            return max(
                0.0,
                (end_dt - start_dt).total_seconds(),
            )
        except ValueError:
            return 0.0