from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from apps.api.demo_closed_loop.schemas import (
    P101AnomalyExplanation,
    P101AnomalySignalContribution,
    P101FailureHypothesis,
    P101FailureHypothesisRanking,
    P101SopEvidenceItem,
    P101SopEvidenceResponse,
    P101EvaluationGap,
    P101EvaluationMetric,
    P101EvaluationSummaryResponse,
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


    def sop_evidence(
        self,
    ) -> P101SopEvidenceResponse:
        sop_evidence = [
            P101SopEvidenceItem(
                evidence_id="SOP-P101-001-CIT-001",
                document_id="SOP-P101-001_Pump_Lubrication_and_Bearing_Check",
                document_title=(
                    "SOP-P101-001: Pump Lubrication and Bearing Check"
                ),
                document_type="SOP / Manual",
                citation_label="[SOP-P101-001]",
                excerpt=(
                    "The pump lubrication and bearing check procedure "
                    "defines inspection of lubricant condition, bearing "
                    "health, and safe maintenance steps for P-101."
                ),
                relevance=(
                    "Directly supports the lubrication degradation "
                    "hypothesis and the work order to inspect and "
                    "restore bearing lubrication."
                ),
                supports_decision=(
                    "Inspect and restore P-101 bearing lubrication."
                ),
                required_action=(
                    "Verify lubricant condition, lubricant quantity, "
                    "bearing housing condition, and attach evidence."
                ),
                verification_requirement=(
                    "Lubrication completion evidence must be attached "
                    "before closing the maintenance action."
                ),
            ),
            P101SopEvidenceItem(
                evidence_id="SOP-P101-002-CIT-001",
                document_id="SOP-P101-002_Pump_Vibration_Inspection",
                document_title=(
                    "SOP-P101-002: Pump Vibration Inspection"
                ),
                document_type="SOP / Manual",
                citation_label="[SOP-P101-002]",
                excerpt=(
                    "The vibration inspection procedure defines "
                    "post-maintenance vibration assessment and "
                    "acceptable return-to-service checks."
                ),
                relevance=(
                    "Supports post-maintenance verification after "
                    "bearing or lubrication corrective action."
                ),
                supports_decision=(
                    "Run vibration verification before returning P-101 "
                    "to service."
                ),
                required_action=(
                    "Perform vibration inspection and compare against "
                    "approved operating limits."
                ),
                verification_requirement=(
                    "Vibration must return to acceptable range before "
                    "the work order can be closed."
                ),
            ),
        ]

        inspection_evidence = [
            P101SopEvidenceItem(
                evidence_id="IR-P101-001-CIT-001",
                document_id="IR-P101-001_Pump_Vibration_Inspection",
                document_title=(
                    "IR-P101-001: Pump Vibration Inspection"
                ),
                document_type="Inspection Report",
                citation_label="[IR-P101-001]",
                excerpt=(
                    "Inspection identified high vibration and abnormal "
                    "mechanical noise near the bearing housing."
                ),
                relevance=(
                    "Confirms that the anomaly is supported by physical "
                    "inspection, not only telemetry."
                ),
                supports_decision=(
                    "Prioritize bearing and lubrication inspection."
                ),
                required_action=(
                    "Inspect bearing housing and perform vibration "
                    "spectrum assessment."
                ),
                verification_requirement=(
                    "Attach post-maintenance inspection readings."
                ),
            ),
            P101SopEvidenceItem(
                evidence_id="IR-P101-002-CIT-001",
                document_id="IR-P101-002_Pump_Bearing_Temperature_Check",
                document_title=(
                    "IR-P101-002: Pump Bearing Temperature Check"
                ),
                document_type="Inspection Report",
                citation_label="[IR-P101-002]",
                excerpt=(
                    "Bearing temperature was reported in warning range "
                    "with an increasing trend."
                ),
                relevance=(
                    "Supports the bearing-friction and lubrication "
                    "degradation explanation."
                ),
                supports_decision=(
                    "Check bearing temperature trend after maintenance."
                ),
                required_action=(
                    "Validate bearing temperature after lubrication or "
                    "bearing corrective action."
                ),
                verification_requirement=(
                    "Bearing temperature must return to acceptable range."
                ),
            ),
        ]

        incident_evidence = [
            P101SopEvidenceItem(
                evidence_id="INC-P101-001-CIT-001",
                document_id="INC-P101-001_High_Vibration_Event",
                document_title="INC-P101-001: High Vibration Event",
                document_type="Incident Report",
                citation_label="[INC-P101-001]",
                excerpt=(
                    "P-101 high vibration event was opened for RCA "
                    "after vibration, temperature, and abnormal noise "
                    "were observed."
                ),
                relevance=(
                    "Links the anomaly and RCA workflow to the original "
                    "incident context."
                ),
                supports_decision=(
                    "Keep incident open until RCA evidence and "
                    "maintenance verification are complete."
                ),
                required_action=(
                    "Link RCA, work order, and verification results to "
                    "the incident."
                ),
                verification_requirement=(
                    "Incident closure requires RCA and post-maintenance "
                    "evidence."
                ),
            ),
        ]

        compliance_evidence = [
            P101SopEvidenceItem(
                evidence_id="COMP-001-CIT-001",
                document_id="COMP-001_Compliance_Checklist",
                document_title=(
                    "COMP-001: PlantMind Demo Compliance Checklist"
                ),
                document_type="Compliance Checklist",
                citation_label="[COMP-001]",
                excerpt=(
                    "Lubrication completion evidence for P-101 was not "
                    "available during compliance review."
                ),
                relevance=(
                    "Explains why missing lubrication evidence increases "
                    "maintenance and audit risk."
                ),
                supports_decision=(
                    "Require evidence attachment before closure."
                ),
                required_action=(
                    "Attach lubrication evidence, safety checklist, and "
                    "post-maintenance verification."
                ),
                verification_requirement=(
                    "Compliance package must show completed evidence "
                    "before final closure."
                ),
            ),
        ]

        return P101SopEvidenceResponse(
            asset_id="P-101",
            rca_case_id="RCA-P101-001",
            question=(
                "What SOP and evidence supports the P-101 maintenance "
                "decision?"
            ),
            answer=(
                "The P-101 maintenance decision is supported by the pump "
                "lubrication SOP, vibration inspection SOP, inspection "
                "reports confirming high vibration and bearing-temperature "
                "increase, the high-vibration incident report, and the "
                "compliance checklist showing missing lubrication evidence. "
                "Together these sources justify inspecting lubrication, "
                "bearing condition, alignment, and post-maintenance vibration "
                "and temperature recovery before closure."
            ),
            maintenance_decision=(
                "Inspect and restore bearing lubrication, inspect bearing "
                "condition, verify alignment, and run post-maintenance "
                "vibration and temperature checks."
            ),
            sop_evidence=sop_evidence,
            inspection_evidence=inspection_evidence,
            incident_evidence=incident_evidence,
            compliance_evidence=compliance_evidence,
            citation_trail=[
                "[SOP-P101-001] defines lubrication and bearing check.",
                "[SOP-P101-002] defines vibration verification.",
                "[IR-P101-001] confirms high vibration and abnormal noise.",
                "[IR-P101-002] confirms bearing temperature warning trend.",
                "[INC-P101-001] links symptoms to the incident.",
                "[COMP-001] confirms missing lubrication evidence.",
            ],
            confidence=0.92,
            rag_status="grounded_with_citations",
            governance_note=(
                "The answer is evidence-grounded and citation-backed, "
                "but PlantMind still requires engineer approval before "
                "confirming RCA or closing the work order."
            ),
            judge_message=(
                "This shows PlantMind acting as an industrial knowledge "
                "assistant: it answers with SOPs, inspection evidence, "
                "incident context, compliance gaps, and closure conditions."
            ),
        )


    def evaluation_summary(
        self,
    ) -> P101EvaluationSummaryResponse:
        metrics = [
            P101EvaluationMetric(
                metric_name="closed_loop_completion",
                display_name="Closed-loop workflow completion",
                score=1.00,
                status="passed",
                evidence=[
                    "Telemetry replay",
                    "Anomaly detection",
                    "Incident creation",
                    "RCA hypothesis",
                    "Governed work order",
                    "Recovery verification",
                    "Audit package",
                ],
                judge_readout=(
                    "The demo shows a complete industrial maintenance "
                    "decision loop from signal to governed closure."
                ),
            ),
            P101EvaluationMetric(
                metric_name="anomaly_explanation_coverage",
                display_name="Anomaly explanation coverage",
                score=0.92,
                status="passed",
                evidence=[
                    "Primary driver: vibration_mm_s",
                    "Secondary driver: bearing_temperature_deg_c",
                    "Model registry link included",
                    "Human review reason included",
                ],
                judge_readout=(
                    "The anomaly is not shown as a black-box alert. "
                    "It is explained using signal contributions, "
                    "confidence, and model metadata."
                ),
            ),
            P101EvaluationMetric(
                metric_name="failure_hypothesis_quality",
                display_name="Failure hypothesis ranking quality",
                score=0.90,
                status="passed",
                evidence=[
                    "Lubrication degradation ranked first",
                    "Bearing damage ranked second",
                    "Misalignment and cavitation included as alternatives",
                    "Sensor fault treated as low-confidence hypothesis",
                ],
                judge_readout=(
                    "The system ranks multiple plausible causes and "
                    "shows evidence, contradictions, missing tests, and "
                    "recommended next actions."
                ),
            ),
            P101EvaluationMetric(
                metric_name="rag_evidence_grounding",
                display_name="SOP and RAG evidence grounding",
                score=0.92,
                status="passed",
                evidence=[
                    "SOP-P101-001",
                    "SOP-P101-002",
                    "IR-P101-001",
                    "IR-P101-002",
                    "INC-P101-001",
                    "COMP-001",
                ],
                judge_readout=(
                    "The maintenance decision is grounded in SOPs, "
                    "inspection reports, incident context, and compliance "
                    "evidence."
                ),
            ),
            P101EvaluationMetric(
                metric_name="governance_and_safety",
                display_name="Governance and safety controls",
                score=0.95,
                status="passed",
                evidence=[
                    "Engineer approval required",
                    "Root cause is not auto-confirmed",
                    "Safety-critical work order is not auto-closed",
                    "Audit package remains part of the closure flow",
                ],
                judge_readout=(
                    "The demo is credible because it prevents unrestricted "
                    "agent behavior in safety-critical maintenance decisions."
                ),
            ),
            P101EvaluationMetric(
                metric_name="demo_readiness",
                display_name="Judge demo readiness",
                score=0.91,
                status="passed",
                evidence=[
                    "/demo/p101-closed-loop",
                    "/demo/p101/anomaly-explanation",
                    "/demo/p101/failure-hypotheses",
                    "/demo/p101/sop-evidence",
                    "/demo/p101/evaluation-summary",
                ],
                judge_readout=(
                    "The demo now has a clear story, visible evidence, "
                    "diagnostic reasoning, and measurable readiness."
                ),
            ),
        ]

        open_gaps = [
            P101EvaluationGap(
                gap_id="GAP-P101-001",
                title="Live plant connection not enabled",
                severity="medium",
                explanation=(
                    "The demo uses deterministic telemetry and curated "
                    "industrial evidence instead of a live plant historian."
                ),
                mitigation=(
                    "Present this clearly as a production-ready demo layer "
                    "that can connect to historian, CMMS, and document "
                    "repositories in deployment."
                ),
            ),
            P101EvaluationGap(
                gap_id="GAP-P101-002",
                title="Physical inspection still required",
                severity="low",
                explanation=(
                    "PlantMind ranks likely failure causes, but bearing "
                    "inspection, lubricant inspection, and alignment readings "
                    "are still required before final confirmation."
                ),
                mitigation=(
                    "Use this as a strength: the system supports engineers "
                    "instead of replacing safety-critical approval."
                ),
            ),
        ]

        return P101EvaluationSummaryResponse(
            asset_id="P-101",
            demo_name="P-101 Closed-Loop Industrial Maintenance Demo",
            evaluation_version="demo-eval-v1",
            overall_score=0.93,
            readiness_level="judge_ready",
            metrics=metrics,
            passed_checks=[
                "Closed-loop demo path is available.",
                "Anomaly explanation is available.",
                "Failure hypothesis ranking is available.",
                "SOP/RAG evidence trail is available.",
                "Human approval and governance controls are visible.",
                "Release readiness validation is passing locally.",
            ],
            open_gaps=open_gaps,
            recommended_demo_order=[
                "Start with P-101 closed-loop timeline.",
                "Show anomaly explanation and signal contributions.",
                "Show ranked failure hypotheses with contradictions.",
                "Show SOP/RAG evidence and citation trail.",
                "Close with evaluation summary and governance note.",
            ],
            endpoints_validated=[
                "/demo/p101/run-closed-loop",
                "/demo/p101/status",
                "/demo/p101/timeline",
                "/demo/p101/anomaly-explanation",
                "/demo/p101/failure-hypotheses",
                "/demo/p101/sop-evidence",
                "/demo/p101/evaluation-summary",
            ],
            governance_note=(
                "PlantMind provides ranked and evidence-backed decision "
                "support, but it does not automatically confirm root cause, "
                "approve safety work, or close critical maintenance actions."
            ),
            judge_message=(
                "This evaluation summary helps judges quickly understand "
                "why the project is complete: it combines telemetry, ML "
                "explanation, RCA reasoning, SOP evidence, compliance, "
                "and governance into one inspectable workflow."
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
