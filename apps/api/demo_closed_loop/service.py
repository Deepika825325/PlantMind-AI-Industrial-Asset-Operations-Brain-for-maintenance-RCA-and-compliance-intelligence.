from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from apps.api.demo_closed_loop.schemas import (
    P101AnomalyExplanation,
    P101AnomalySignalContribution,
    P101FailureHypothesis,
    P101FailureHypothesisRanking,
    P101ClosedLoopRunResponse,
    P101ClosedLoopState,
    P101ClosedLoopTimelineResponse,
    P101DemoStep,
)


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


class P101ClosedLoopDemoService:
    def __init__(self) -> None:
        self._state = self._build_state(
            status="not_started",
            completed=False,
        )

    def reset(self) -> P101ClosedLoopState:
        self._state = self._build_state(
            status="not_started",
            completed=False,
        )

        return deepcopy(
            self._state
        )

    def run_closed_loop(
        self,
    ) -> P101ClosedLoopRunResponse:
        self._state = self._build_state(
            status="completed",
            completed=True,
        )

        return P101ClosedLoopRunResponse(
            state=deepcopy(
                self._state
            )
        )

    def status(self) -> P101ClosedLoopState:
        return deepcopy(
            self._state
        )

    def timeline(
        self,
    ) -> P101ClosedLoopTimelineResponse:
        return P101ClosedLoopTimelineResponse(
            demo_id=self._state.demo_id,
            asset_id=self._state.asset_id,
            timeline=deepcopy(
                self._state.steps
            ),
        )

    def anomaly_explanation(
        self,
    ) -> P101AnomalyExplanation:
        return P101AnomalyExplanation(
            asset_id="P-101",
            model_name="plantmind-p101-anomaly-detector",
            model_version="v0.3.11",
            dataset_version="telemetry-demo-v1",
            feature_version="p101-multivariate-features-v1",
            anomaly_label="critical",
            anomaly_score=0.87,
            confidence=0.91,
            explanation_summary=(
                "P-101 was flagged because vibration and "
                "bearing temperature increased together over "
                "the degradation replay window. The combined "
                "multivariate residual exceeded the production "
                "threshold and matched the known high-vibration "
                "bearing-temperature RCA pattern."
            ),
            primary_driver="vibration_mm_s",
            baseline_window=(
                "Healthy P-101 operating window before degradation"
            ),
            observation_window=(
                "Latest degradation replay window"
            ),
            signal_contributions=[
                P101AnomalySignalContribution(
                    signal_name="vibration_mm_s",
                    display_name="Vibration",
                    baseline_value=2.4,
                    observed_value=8.4,
                    unit="mm/s",
                    deviation_percent=250.0,
                    contribution_weight=0.42,
                    explanation=(
                        "Vibration moved from normal range to "
                        "a severe mechanical-degradation range, "
                        "making it the strongest anomaly driver."
                    ),
                ),
                P101AnomalySignalContribution(
                    signal_name="bearing_temperature_deg_c",
                    display_name="Bearing temperature",
                    baseline_value=64.0,
                    observed_value=91.0,
                    unit="deg C",
                    deviation_percent=42.2,
                    contribution_weight=0.31,
                    explanation=(
                        "Bearing temperature rose together with "
                        "vibration, strengthening the bearing "
                        "wear or lubrication-degradation hypothesis."
                    ),
                ),
                P101AnomalySignalContribution(
                    signal_name="motor_current_a",
                    display_name="Motor current",
                    baseline_value=18.7,
                    observed_value=24.0,
                    unit="A",
                    deviation_percent=28.3,
                    contribution_weight=0.17,
                    explanation=(
                        "Motor current increased moderately, "
                        "suggesting higher mechanical load rather "
                        "than an isolated sensor spike."
                    ),
                ),
                P101AnomalySignalContribution(
                    signal_name="rpm",
                    display_name="RPM",
                    baseline_value=1480.0,
                    observed_value=1455.0,
                    unit="rpm",
                    deviation_percent=-1.7,
                    contribution_weight=0.10,
                    explanation=(
                        "RPM dipped slightly while vibration and "
                        "current increased, supporting a "
                        "mechanical-load interpretation."
                    ),
                ),
            ],
            supporting_evidence_ids=[
                "P101-EV-001",
                "P101-EV-002",
                "P101-EV-003",
                "RCA-P101-001",
            ],
            model_registry_endpoint=(
                "/mlops/model-registry/production/"
                "plantmind-p101-anomaly-detector"
            ),
            telemetry_endpoint="/telemetry/assets/P-101/summary",
            human_review_required=True,
            human_review_reason=(
                "The model can flag degradation and explain "
                "dominant signals, but maintenance approval "
                "still requires engineer review of RCA evidence, "
                "safety procedure, and post-maintenance checks."
            ),
            judge_message=(
                "This converts anomaly detection from a black-box "
                "score into a maintenance explanation connected "
                "to evidence, RCA, model versioning, and human "
                "governance."
            ),
        )

    def failure_hypotheses(
        self,
    ) -> P101FailureHypothesisRanking:
        hypotheses = [
            P101FailureHypothesis(
                rank=1,
                failure_mode="lubrication_degradation",
                display_name="Lubrication degradation",
                probability=0.37,
                confidence_label="High",
                supporting_signals=[
                    "Missing lubrication evidence",
                    "Bearing temperature rise",
                    "Vibration escalation",
                    "Abnormal mechanical noise",
                ],
                supporting_evidence_ids=[
                    "P101-EV-001",
                    "P101-EV-002",
                    "P101-EV-003",
                ],
                contradictory_evidence=[
                    "No lubricant laboratory analysis is currently available.",
                ],
                missing_tests=[
                    "Lubricant condition inspection",
                    "Lubricant quantity verification",
                    "Bearing housing inspection",
                ],
                recommended_next_action=(
                    "Inspect and restore bearing lubrication before "
                    "confirming the RCA."
                ),
                human_approval_required=True,
                decision_reason=(
                    "Lubrication evidence is missing before the "
                    "temperature and vibration escalation. This makes "
                    "lubrication degradation the strongest explainable "
                    "maintenance hypothesis."
                ),
            ),
            P101FailureHypothesis(
                rank=2,
                failure_mode="bearing_damage",
                display_name="Bearing wear or damage",
                probability=0.29,
                confidence_label="High",
                supporting_signals=[
                    "High vibration",
                    "Bearing temperature rise",
                    "Abnormal mechanical noise near bearing housing",
                ],
                supporting_evidence_ids=[
                    "P101-EV-002",
                    "P101-EV-003",
                    "P101-EV-004",
                ],
                contradictory_evidence=[
                    "Direct bearing inspection result is not yet attached.",
                ],
                missing_tests=[
                    "Bearing clearance check",
                    "Bearing visual inspection",
                    "Vibration spectrum analysis",
                ],
                recommended_next_action=(
                    "Inspect bearing condition and attach inspection "
                    "evidence to the RCA case."
                ),
                human_approval_required=True,
                decision_reason=(
                    "The signal pattern is consistent with bearing "
                    "wear, but confirmation requires physical inspection."
                ),
            ),
            P101FailureHypothesis(
                rank=3,
                failure_mode="shaft_misalignment",
                display_name="Shaft misalignment",
                probability=0.18,
                confidence_label="Medium",
                supporting_signals=[
                    "High vibration",
                    "Slight RPM drop",
                    "Motor current increase",
                ],
                supporting_evidence_ids=[
                    "P101-EV-003",
                    "P101-EV-004",
                ],
                contradictory_evidence=[
                    "Alignment measurements have not yet been recorded.",
                    "Temperature rise points more strongly to bearing friction.",
                ],
                missing_tests=[
                    "Shaft alignment measurement",
                    "Coupling inspection",
                ],
                recommended_next_action=(
                    "Perform shaft alignment assessment before "
                    "returning P-101 to service."
                ),
                human_approval_required=True,
                decision_reason=(
                    "Misalignment can explain vibration and current rise, "
                    "but current evidence supports lubrication and bearing "
                    "issues more strongly."
                ),
            ),
            P101FailureHypothesis(
                rank=4,
                failure_mode="cavitation_or_hydraulic_instability",
                display_name="Cavitation or hydraulic instability",
                probability=0.11,
                confidence_label="Low-Medium",
                supporting_signals=[
                    "Vibration",
                    "Mechanical noise",
                ],
                supporting_evidence_ids=[
                    "P101-EV-003",
                ],
                contradictory_evidence=[
                    "No confirmed suction-pressure anomaly is available.",
                    "Bearing temperature increase is more consistent with mechanical friction.",
                ],
                missing_tests=[
                    "Suction pressure trend review",
                    "Flow instability check",
                    "Pump operating point verification",
                ],
                recommended_next_action=(
                    "Check suction pressure and operating point only "
                    "after bearing and lubrication checks are initiated."
                ),
                human_approval_required=True,
                decision_reason=(
                    "Hydraulic instability remains possible, but evidence "
                    "is weaker than lubrication and bearing hypotheses."
                ),
            ),
            P101FailureHypothesis(
                rank=5,
                failure_mode="sensor_fault",
                display_name="Sensor fault or data-quality issue",
                probability=0.05,
                confidence_label="Low",
                supporting_signals=[
                    "Telemetry-driven anomaly score",
                ],
                supporting_evidence_ids=[
                    "P101-EV-002",
                ],
                contradictory_evidence=[
                    "Independent inspection confirmed abnormal vibration and noise.",
                    "Multiple signals changed together instead of one isolated sensor.",
                ],
                missing_tests=[
                    "Sensor calibration check",
                    "Cross-check with handheld vibration reading",
                ],
                recommended_next_action=(
                    "Perform calibration check, but do not treat this as "
                    "the primary cause unless physical checks contradict "
                    "the mechanical evidence."
                ),
                human_approval_required=True,
                decision_reason=(
                    "A pure sensor fault is unlikely because inspection "
                    "evidence confirms physical symptoms."
                ),
            ),
        ]

        return P101FailureHypothesisRanking(
            asset_id="P-101",
            rca_case_id="RCA-P101-001",
            primary_hypothesis="lubrication_degradation",
            hypotheses=hypotheses,
            linked_rca_evidence_ids=[
                "P101-EV-001",
                "P101-EV-002",
                "P101-EV-003",
                "P101-EV-004",
                "RCA-P101-001",
            ],
            governance_note=(
                "PlantMind ranks failure hypotheses and recommends "
                "next tests, but it does not automatically confirm the "
                "root cause or close the safety-critical work order."
            ),
            judge_message=(
                "This shows the system moving beyond anomaly detection "
                "into evidence-backed diagnostic reasoning with "
                "contradictions, missing tests, and human approval."
            ),
        )


    def _build_state(
        self,
        *,
        status: str,
        completed: bool,
    ) -> P101ClosedLoopState:
        timestamp = (
            _utc_now()
            if completed
            else None
        )

        steps = [
            P101DemoStep(
                step_id="step-01-telemetry-replay",
                title="Start P-101 degradation replay",
                status="passed" if completed else "pending",
                description=(
                    "Replay starts from healthy P-101 "
                    "telemetry and introduces rising "
                    "vibration and bearing temperature."
                ),
                evidence_used=[
                    "P101-EV-001",
                    "P101-EV-002",
                ]
                if completed
                else [],
                ai_confidence=0.91 if completed else None,
                human_approval_required=False,
                linked_endpoint="/telemetry/assets/P-101/summary",
                timestamp=timestamp,
            ),
            P101DemoStep(
                step_id="step-02-anomaly-detection",
                title="Detect anomaly",
                status="passed" if completed else "pending",
                description=(
                    "The anomaly model flags persistent "
                    "vibration and bearing-temperature "
                    "deviation from the healthy baseline."
                ),
                evidence_used=[
                    "plantmind-p101-anomaly-detector:v0.3.11",
                    "telemetry-demo-v1",
                    "p101-multivariate-features-v1",
                ]
                if completed
                else [],
                ai_confidence=0.87 if completed else None,
                human_approval_required=False,
                linked_endpoint="/mlops/model-registry/production/plantmind-p101-anomaly-detector",
                timestamp=timestamp,
            ),
            P101DemoStep(
                step_id="step-03-incident-created",
                title="Create grouped incident",
                status="passed" if completed else "pending",
                description=(
                    "PlantMind groups repeated abnormal "
                    "signals into one maintenance incident "
                    "instead of creating alert noise."
                ),
                evidence_used=[
                    "INC-P101-001",
                    "P101-EV-001",
                    "P101-EV-002",
                ]
                if completed
                else [],
                ai_confidence=0.84 if completed else None,
                human_approval_required=True,
                linked_endpoint="/incidents?asset_id=P-101",
                timestamp=timestamp,
            ),
            P101DemoStep(
                step_id="step-04-rca-hypothesis",
                title="Generate RCA hypothesis",
                status="passed" if completed else "pending",
                description=(
                    "Evidence-backed RCA ranks lubrication "
                    "degradation and bearing damage as likely "
                    "failure hypotheses while keeping engineer "
                    "approval mandatory."
                ),
                evidence_used=[
                    "RCA-P101-001",
                    "P101-EV-001",
                    "P101-EV-002",
                    "P101-EV-003",
                    "P101-EV-004",
                ]
                if completed
                else [],
                ai_confidence=0.78 if completed else None,
                human_approval_required=True,
                linked_endpoint="/rca-orchestration/cases/RCA-P101-001/history",
                timestamp=timestamp,
            ),
            P101DemoStep(
                step_id="step-05-work-order",
                title="Create governed work order",
                status="passed" if completed else "pending",
                description=(
                    "The RCA output links to a governed "
                    "maintenance work order with required "
                    "procedure, safety checks, and evidence."
                ),
                evidence_used=[
                    "MWO-P101-001",
                    "RCA-P101-001",
                ]
                if completed
                else [],
                ai_confidence=0.82 if completed else None,
                human_approval_required=True,
                linked_endpoint="/maintenance/work-orders/MWO-P101-001/lifecycle",
                timestamp=timestamp,
            ),
            P101DemoStep(
                step_id="step-06-recovery-verification",
                title="Verify recovery",
                status="passed" if completed else "pending",
                description=(
                    "The work order cannot close until "
                    "post-maintenance verification confirms "
                    "that vibration and temperature returned "
                    "to acceptable ranges."
                ),
                evidence_used=[
                    "post-maintenance-recovery-replay",
                    "P101-verification-criteria",
                ]
                if completed
                else [],
                ai_confidence=0.9 if completed else None,
                human_approval_required=True,
                linked_endpoint="/maintenance/work-orders/MWO-P101-001/post-maintenance-verification/history",
                timestamp=timestamp,
            ),
            P101DemoStep(
                step_id="step-07-audit-package",
                title="Generate audit-ready compliance package",
                status="passed" if completed else "pending",
                description=(
                    "PlantMind packages RCA evidence, "
                    "maintenance actions, verification "
                    "status, and missing-evidence checks "
                    "into an audit-ready compliance view."
                ),
                evidence_used=[
                    "compliance-audit-package:P-101",
                    "C001-C008",
                ]
                if completed
                else [],
                ai_confidence=0.88 if completed else None,
                human_approval_required=False,
                linked_endpoint="/compliance/audit-packages/assets/P-101",
                timestamp=timestamp,
            ),
        ]

        completed_steps = (
            len(steps)
            if completed
            else 0
        )

        return P101ClosedLoopState(
            demo_id="p101-closed-loop-demo",
            asset_id="P-101",
            asset_name="Cooling Water Circulation Pump",
            status=status,
            current_step=completed_steps,
            total_steps=len(steps),
            completed_steps=completed_steps,
            summary=(
                "P-101 closed-loop demo connects "
                "telemetry degradation, anomaly detection, "
                "incident grouping, evidence-backed RCA, "
                "governed maintenance, recovery verification, "
                "and audit-ready compliance."
            ),
            judge_message=(
                "This demo shows PlantMind as a closed-loop "
                "industrial maintenance intelligence system, "
                "not only a prediction dashboard or RAG chatbot."
            ),
            steps=steps,
        )
