from __future__ import annotations

import hashlib

from apps.api.post_maintenance_verification.schemas import (
    MaintenanceRecoveryReplayRequest,
    MetricComparison,
    PostMaintenanceVerificationHistoryResponse,
    PostMaintenanceVerificationRequest,
    PostMaintenanceVerificationResult,
    TelemetrySnapshot,
    VerificationCriteria,
    VerificationCriteriaResponse,
)


class PostMaintenanceVerificationService:
    def __init__(self) -> None:
        self._history_by_work_order: dict[
            str,
            list[PostMaintenanceVerificationResult],
        ] = {}

    def criteria(
        self,
    ) -> VerificationCriteriaResponse:
        return VerificationCriteriaResponse(
            default_criteria=VerificationCriteria(),
            verification_rule=(
                "Successful verification requires vibration, bearing temperature, "
                "health score, anomaly score, and failure probability to satisfy "
                "the configured criteria."
            ),
            verified_transition_rule=(
                "A work order may enter Verified only when post-maintenance "
                "verification outcome is successful."
            ),
            failed_recovery_rule=(
                "A failed recovery can reopen the work order by moving it from "
                "Verification Pending back to In Progress."
            ),
        )

    def replay_recovery(
        self,
        request: MaintenanceRecoveryReplayRequest,
    ) -> PostMaintenanceVerificationResult:
        pre_maintenance = TelemetrySnapshot(
            vibration_mm_s=8.8,
            bearing_temperature_c=94.0,
            health_score=42.0,
            anomaly_score=0.91,
            failure_probability=0.82,
        )

        if request.scenario == "successful_recovery":
            post_maintenance = TelemetrySnapshot(
                vibration_mm_s=2.4,
                bearing_temperature_c=66.0,
                health_score=88.0,
                anomaly_score=0.12,
                failure_probability=0.14,
            )
        elif request.scenario == "partial_recovery":
            post_maintenance = TelemetrySnapshot(
                vibration_mm_s=3.2,
                bearing_temperature_c=79.0,
                health_score=82.0,
                anomaly_score=0.28,
                failure_probability=0.31,
            )
        elif request.scenario == "failed_recovery":
            post_maintenance = TelemetrySnapshot(
                vibration_mm_s=7.4,
                bearing_temperature_c=90.0,
                health_score=49.0,
                anomaly_score=0.77,
                failure_probability=0.69,
            )
        else:
            post_maintenance = TelemetrySnapshot(
                vibration_mm_s=2.6,
                bearing_temperature_c=None,
                health_score=None,
                anomaly_score=0.18,
                failure_probability=None,
            )

        return self.verify(
            PostMaintenanceVerificationRequest(
                work_order_id=request.work_order_id,
                asset_id=request.asset_id,
                verified_by=request.verified_by,
                verified_at=request.verified_at,
                pre_maintenance=pre_maintenance,
                post_maintenance=post_maintenance,
                criteria=VerificationCriteria(),
            )
        )

    def verify(
        self,
        request: PostMaintenanceVerificationRequest,
    ) -> PostMaintenanceVerificationResult:
        verification_id = request.verification_id or self._verification_id(
            request
        )

        comparisons = self._compare_metrics(
            request
        )

        passed = sum(
            1
            for comparison in comparisons
            if comparison.status == "passed"
        )
        failed = sum(
            1
            for comparison in comparisons
            if comparison.status == "failed"
        )
        missing = sum(
            1
            for comparison in comparisons
            if comparison.status == "missing"
        )

        outcome = self._outcome(
            passed=passed,
            failed=failed,
            missing=missing,
            criteria=request.criteria,
        )

        readings_normalized = (
            request.post_maintenance.vibration_mm_s is not None
            and request.post_maintenance.bearing_temperature_c is not None
            and request.post_maintenance.health_score is not None
            and request.post_maintenance.anomaly_score is not None
            and request.post_maintenance.failure_probability is not None
            and request.post_maintenance.vibration_mm_s
            <= request.criteria.max_vibration_mm_s
            and request.post_maintenance.bearing_temperature_c
            <= request.criteria.max_bearing_temperature_c
            and request.post_maintenance.health_score
            >= request.criteria.min_health_score
            and request.post_maintenance.anomaly_score
            <= request.criteria.max_anomaly_score
            and request.post_maintenance.failure_probability
            <= request.criteria.max_failure_probability
        )

        result = PostMaintenanceVerificationResult(
            verification_id=verification_id,
            work_order_id=request.work_order_id,
            asset_id=request.asset_id,
            verified_by=request.verified_by,
            verified_at=request.verified_at,
            outcome=outcome,
            pre_maintenance=request.pre_maintenance,
            post_maintenance=request.post_maintenance,
            criteria=request.criteria,
            metric_comparisons=comparisons,
            passed_metric_count=passed,
            failed_metric_count=failed,
            missing_metric_count=missing,
            readings_normalized=readings_normalized,
            can_mark_verified=outcome == "successful",
            should_reopen_work_order=outcome == "failed",
            explanation=self._explanation(
                outcome=outcome,
                passed=passed,
                failed=failed,
                missing=missing,
            ),
        )

        self._history_by_work_order.setdefault(
            request.work_order_id,
            [],
        ).append(result)

        return result

    def history(
        self,
        work_order_id: str,
    ) -> PostMaintenanceVerificationHistoryResponse:
        verifications = self._history_by_work_order.get(
            work_order_id,
            [],
        )

        return PostMaintenanceVerificationHistoryResponse(
            work_order_id=work_order_id,
            total_verifications=len(verifications),
            verifications=verifications[-20:],
        )

    def latest(
        self,
        work_order_id: str,
    ) -> PostMaintenanceVerificationResult | None:
        history = self._history_by_work_order.get(
            work_order_id,
            [],
        )

        if not history:
            return None

        return history[-1]

    def _compare_metrics(
        self,
        request: PostMaintenanceVerificationRequest,
    ) -> list[MetricComparison]:
        pre = request.pre_maintenance
        post = request.post_maintenance
        criteria = request.criteria

        return [
            self._max_metric(
                metric_name="vibration_mm_s",
                pre_value=pre.vibration_mm_s,
                post_value=post.vibration_mm_s,
                target=criteria.max_vibration_mm_s,
                unit="mm/s",
            ),
            self._max_metric(
                metric_name="bearing_temperature_c",
                pre_value=pre.bearing_temperature_c,
                post_value=post.bearing_temperature_c,
                target=criteria.max_bearing_temperature_c,
                unit="°C",
            ),
            self._min_metric(
                metric_name="health_score",
                pre_value=pre.health_score,
                post_value=post.health_score,
                target=criteria.min_health_score,
            ),
            self._max_metric(
                metric_name="anomaly_score",
                pre_value=pre.anomaly_score,
                post_value=post.anomaly_score,
                target=criteria.max_anomaly_score,
                unit="score",
            ),
            self._max_metric(
                metric_name="failure_probability",
                pre_value=pre.failure_probability,
                post_value=post.failure_probability,
                target=criteria.max_failure_probability,
                unit="probability",
            ),
        ]

    def _max_metric(
        self,
        *,
        metric_name: str,
        pre_value: float | None,
        post_value: float | None,
        target: float,
        unit: str,
    ) -> MetricComparison:
        if post_value is None:
            return MetricComparison(
                metric_name=metric_name,
                pre_value=pre_value,
                post_value=post_value,
                target=target,
                status="missing",
                explanation=(
                    f"{metric_name} is missing from post-maintenance evidence."
                ),
            )

        if post_value <= target:
            status = "passed"
            explanation = (
                f"{metric_name} normalized to {post_value} {unit}, "
                f"within target <= {target}."
            )
        else:
            status = "failed"
            explanation = (
                f"{metric_name} remains {post_value} {unit}, "
                f"above target <= {target}."
            )

        return MetricComparison(
            metric_name=metric_name,
            pre_value=pre_value,
            post_value=post_value,
            target=target,
            status=status,
            explanation=explanation,
        )

    def _min_metric(
        self,
        *,
        metric_name: str,
        pre_value: float | None,
        post_value: float | None,
        target: float,
    ) -> MetricComparison:
        if post_value is None:
            return MetricComparison(
                metric_name=metric_name,
                pre_value=pre_value,
                post_value=post_value,
                target=target,
                status="missing",
                explanation=(
                    f"{metric_name} is missing from post-maintenance evidence."
                ),
            )

        if post_value >= target:
            status = "passed"
            explanation = (
                f"{metric_name} improved to {post_value}, "
                f"meeting target >= {target}."
            )
        else:
            status = "failed"
            explanation = (
                f"{metric_name} is {post_value}, below target >= {target}."
            )

        return MetricComparison(
            metric_name=metric_name,
            pre_value=pre_value,
            post_value=post_value,
            target=target,
            status=status,
            explanation=explanation,
        )

    def _outcome(
        self,
        *,
        passed: int,
        failed: int,
        missing: int,
        criteria: VerificationCriteria,
    ) -> str:
        if missing > 0:
            return "insufficient_evidence"

        if failed == 0:
            return "successful"

        if passed >= criteria.minimum_passed_metrics_for_partial_success:
            return "partially_successful"

        return "failed"

    def _explanation(
        self,
        *,
        outcome: str,
        passed: int,
        failed: int,
        missing: int,
    ) -> str:
        if outcome == "successful":
            return (
                "Post-maintenance verification passed. Telemetry normalized, "
                "health improved, anomaly score reduced, and failure probability "
                "is within threshold."
            )

        if outcome == "partially_successful":
            return (
                f"Post-maintenance verification is partially successful: "
                f"{passed} passed, {failed} failed, {missing} missing. "
                "The work order should not be marked verified yet."
            )

        if outcome == "failed":
            return (
                f"Post-maintenance verification failed: {passed} passed, "
                f"{failed} failed, {missing} missing. Reopen the work order."
            )

        return (
            f"Post-maintenance verification has insufficient evidence: "
            f"{passed} passed, {failed} failed, {missing} missing."
        )

    def _verification_id(
        self,
        request: PostMaintenanceVerificationRequest,
    ) -> str:
        digest = hashlib.sha256(
            (
                f"{request.work_order_id}:"
                f"{request.asset_id}:"
                f"{request.verified_at}:"
                f"{request.verified_by}"
            ).encode(
                "utf-8"
            )
        ).hexdigest()[:12]

        return f"PMV-{digest}"