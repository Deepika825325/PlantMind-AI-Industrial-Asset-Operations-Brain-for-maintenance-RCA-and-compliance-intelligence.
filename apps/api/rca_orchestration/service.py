from __future__ import annotations

from apps.api.rca_orchestration.schemas import (
    CandidateRootCause,
    ControlledRcaHistoryResponse,
    ControlledRcaRequest,
    ControlledRcaResponse,
    MissingTestRecommendation,
    RcaApprovalRequest,
    RcaApprovalResponse,
    RcaDraft,
    RcaEvidenceItem,
    WorkflowStepResult,
)


WORKFLOW_VERSION = "controlled-rca-orchestration-v1.0.0"


class ControlledRcaOrchestrationService:
    def __init__(self) -> None:
        self._history_by_case: dict[
            str,
            list[ControlledRcaResponse],
        ] = {}
        self._approval_status_by_case: dict[
            str,
            str,
        ] = {}

    def run(
        self,
        request: ControlledRcaRequest,
    ) -> ControlledRcaResponse:
        steps = self._workflow_steps(
            request,
        )

        telemetry_evidence = self._telemetry_evidence(
            request,
        )
        supporting_evidence = self._supporting_evidence(
            request,
        )
        contradictory_evidence = self._contradictory_evidence(
            request,
        )
        contextual_evidence = self._contextual_evidence(
            request,
        )
        missing_tests = self._missing_tests(
            request,
        )

        candidate_causes = self._candidate_causes(
            telemetry_evidence=telemetry_evidence,
            supporting_evidence=supporting_evidence,
            contradictory_evidence=contradictory_evidence,
            missing_tests=missing_tests,
        )

        draft = self._draft_rca(
            request=request,
            candidate_causes=candidate_causes,
        )

        response = ControlledRcaResponse(
            workflow_version=WORKFLOW_VERSION,
            rca_case_id=request.rca_case_id,
            incident_id=request.incident_id,
            asset_id=request.asset_id,
            steps=steps,
            telemetry_evidence=telemetry_evidence,
            supporting_evidence=supporting_evidence,
            contradictory_evidence=contradictory_evidence,
            contextual_evidence=contextual_evidence,
            candidate_causes=candidate_causes,
            missing_tests=missing_tests,
            draft=draft,
            guardrails=[
                "The workflow can draft, rank, retrieve, and recommend.",
                "The workflow cannot confirm root cause automatically.",
                "The workflow cannot close a safety incident.",
                "The workflow cannot approve a critical work order.",
                "Engineer approval is required before RCA confirmation.",
            ],
        )

        self._history_by_case.setdefault(
            request.rca_case_id,
            [],
        ).append(response)

        return response

    def approve(
        self,
        request: RcaApprovalRequest,
    ) -> RcaApprovalResponse:
        if request.decision == "approved":
            status = "approved"
            confirmation_allowed = True
            explanation = (
                "Engineer approval recorded. RCA confirmation may proceed "
                "through the governed approval path."
            )
        else:
            status = "rejected"
            confirmation_allowed = False
            explanation = (
                "Engineer rejected the draft. RCA confirmation remains blocked."
            )

        self._approval_status_by_case[
            request.rca_case_id
        ] = status

        return RcaApprovalResponse(
            rca_case_id=request.rca_case_id,
            approval_status=status,
            approved_by=request.approved_by,
            approved_at=request.approved_at,
            note=request.note,
            confirmation_allowed=confirmation_allowed,
            explanation=explanation,
        )

    def history(
        self,
        rca_case_id: str,
    ) -> ControlledRcaHistoryResponse:
        runs = self._history_by_case.get(
            rca_case_id,
            [],
        )

        return ControlledRcaHistoryResponse(
            rca_case_id=rca_case_id,
            total_runs=len(runs),
            runs=runs[-20:],
        )

    def _workflow_steps(
        self,
        request: ControlledRcaRequest,
    ) -> list[WorkflowStepResult]:
        return [
            WorkflowStepResult(
                step_name="load_incident",
                status="completed",
                explanation=(
                    f"Loaded incident {request.incident_id} for asset "
                    f"{request.asset_id}."
                ),
            ),
            WorkflowStepResult(
                step_name="retrieve_telemetry",
                status="completed",
                explanation=(
                    "Retrieved P-101 vibration, bearing temperature, motor "
                    "current, and anomaly-score telemetry around the incident."
                ),
            ),
            WorkflowStepResult(
                step_name="retrieve_evidence",
                status="completed",
                explanation=(
                    "Retrieved inspection, operator, maintenance, and "
                    "compliance evidence connected to the incident."
                ),
            ),
            WorkflowStepResult(
                step_name="retrieve_approved_documents",
                status="completed",
                explanation=(
                    "Retrieved approved SOP and maintenance guidance only. "
                    "Draft documents are excluded."
                ),
            ),
            WorkflowStepResult(
                step_name="retrieve_similar_cases",
                status="completed",
                explanation=(
                    "Retrieved similar P-101 bearing-temperature and vibration "
                    "case history for comparison."
                ),
            ),
            WorkflowStepResult(
                step_name="generate_candidate_causes",
                status="completed",
                explanation=(
                    "Generated deterministic candidate causes from telemetry "
                    "and evidence patterns."
                ),
            ),
            WorkflowStepResult(
                step_name="rank_causes",
                status="completed",
                explanation=(
                    "Ranked candidate causes using visible evidence counts, "
                    "contradictions, and missing tests."
                ),
            ),
            WorkflowStepResult(
                step_name="identify_contradictions",
                status="completed",
                explanation=(
                    "Identified evidence that weakens or contradicts each "
                    "candidate cause."
                ),
            ),
            WorkflowStepResult(
                step_name="identify_missing_tests",
                status="completed",
                explanation=(
                    "Identified required checks before any root cause can be "
                    "confirmed."
                ),
            ),
            WorkflowStepResult(
                step_name="draft_rca",
                status="completed",
                explanation=(
                    "Drafted RCA summary with candidate causes and recommended "
                    "next actions."
                ),
            ),
            WorkflowStepResult(
                step_name="request_engineer_approval",
                status="completed",
                explanation=(
                    "RCA remains in approval_required state. Engineer approval "
                    "is mandatory before confirmation."
                ),
            ),
        ]

    def _telemetry_evidence(
        self,
        request: ControlledRcaRequest,
    ) -> list[RcaEvidenceItem]:
        return [
            RcaEvidenceItem(
                evidence_id="TEL-P101-NEW-001",
                evidence_type="telemetry",
                title="P-101 vibration crossed critical threshold",
                summary=(
                    "Replay telemetry shows vibration increasing from normal "
                    "range to critical range before the incident."
                ),
                source="telemetry_replay:P101-VIB-001",
                timestamp="2026-07-10T09:00:30+00:00",
                direction="supporting",
                reliability="high",
            ),
            RcaEvidenceItem(
                evidence_id="TEL-P101-NEW-002",
                evidence_type="telemetry",
                title="P-101 bearing temperature increased with vibration",
                summary=(
                    "Bearing temperature rose together with vibration, which "
                    "supports bearing or lubrication-related degradation."
                ),
                source="telemetry_replay:P101-BTEMP-001",
                timestamp="2026-07-10T09:00:30+00:00",
                direction="supporting",
                reliability="high",
            ),
            RcaEvidenceItem(
                evidence_id="TEL-P101-NEW-003",
                evidence_type="telemetry",
                title="Motor current did not spike proportionally",
                summary=(
                    "Motor current remained comparatively stable, which makes "
                    "severe electrical overload less likely."
                ),
                source="telemetry_replay:P101-CURRENT-001",
                timestamp="2026-07-10T09:00:30+00:00",
                direction="contradictory",
                reliability="medium",
            ),
        ]

    def _supporting_evidence(
        self,
        request: ControlledRcaRequest,
    ) -> list[RcaEvidenceItem]:
        return [
            RcaEvidenceItem(
                evidence_id="INC-P101-NEW-001",
                evidence_type="incident",
                title="Grouped P-101 vibration and temperature incident",
                summary=(
                    "Incident management grouped multiple related P-101 "
                    "anomalies into one incident linked to the RCA case."
                ),
                source=request.incident_id,
                timestamp="2026-07-10T09:00:30+00:00",
                direction="supporting",
                reliability="high",
            ),
            RcaEvidenceItem(
                evidence_id="IR-P101-001",
                evidence_type="inspection",
                title="Drive-end abnormal noise inspection finding",
                summary=(
                    "Inspection evidence reports abnormal drive-end noise "
                    "consistent with bearing degradation."
                ),
                source="inspection_report:IR-P101-001",
                timestamp="2026-07-10T09:05:00+00:00",
                direction="supporting",
                reliability="high",
            ),
            RcaEvidenceItem(
                evidence_id="SOP-P101-001",
                evidence_type="document",
                title="Approved P-101 bearing inspection SOP",
                summary=(
                    "Approved SOP requires bearing inspection, lubrication "
                    "verification, and post-maintenance vibration testing."
                ),
                source="approved_document:SOP-P101-001",
                direction="supporting",
                reliability="high",
            ),
        ]

    def _contradictory_evidence(
        self,
        request: ControlledRcaRequest,
    ) -> list[RcaEvidenceItem]:
        return [
            RcaEvidenceItem(
                evidence_id="CONTRA-P101-001",
                evidence_type="maintenance",
                title="No confirmed lubrication sample yet",
                summary=(
                    "Lubrication degradation is plausible, but no oil sample "
                    "or lubrication quality test has confirmed it."
                ),
                source="maintenance_gap:P101-LUBE-SAMPLE",
                direction="contradictory",
                reliability="medium",
            ),
            RcaEvidenceItem(
                evidence_id="CONTRA-P101-002",
                evidence_type="telemetry",
                title="Flow did not collapse during the event",
                summary=(
                    "Flow stayed within usable range, making severe cavitation "
                    "less likely than bearing or lubrication degradation."
                ),
                source="telemetry_replay:P101-FLOW-001",
                timestamp="2026-07-10T09:00:30+00:00",
                direction="contradictory",
                reliability="medium",
            ),
        ]

    def _contextual_evidence(
        self,
        request: ControlledRcaRequest,
    ) -> list[RcaEvidenceItem]:
        return [
            RcaEvidenceItem(
                evidence_id="SIMILAR-P101-001",
                evidence_type="similar_case",
                title="Previous P-101 vibration and bearing temperature case",
                summary=(
                    "A similar prior case ranked bearing inspection and "
                    "lubrication verification as first-line checks."
                ),
                source="similar_case:RCA-P101-PRIOR-001",
                direction="context",
                reliability="medium",
            ),
            RcaEvidenceItem(
                evidence_id="COMP-P101-001",
                evidence_type="compliance",
                title="Missing post-maintenance verification risk",
                summary=(
                    "Compliance rules require verification evidence before "
                    "maintenance-related RCA closure."
                ),
                source="compliance_rule:C002",
                direction="context",
                reliability="high",
            ),
        ]

    def _missing_tests(
        self,
        request: ControlledRcaRequest,
    ) -> list[MissingTestRecommendation]:
        return [
            MissingTestRecommendation(
                test_id="TEST-P101-BEARING-INSPECTION",
                title="Inspect drive-end bearing condition",
                reason=(
                    "Required to distinguish bearing damage from lubrication "
                    "degradation."
                ),
                priority="critical",
                required_before_confirmation=True,
            ),
            MissingTestRecommendation(
                test_id="TEST-P101-LUBE-SAMPLE",
                title="Verify lubrication condition",
                reason=(
                    "Lubrication degradation cannot be confirmed without "
                    "lubrication evidence."
                ),
                priority="high",
                required_before_confirmation=True,
            ),
            MissingTestRecommendation(
                test_id="TEST-P101-ALIGNMENT",
                title="Verify shaft alignment",
                reason=(
                    "Shaft misalignment remains an alternative cause until "
                    "alignment is checked."
                ),
                priority="medium",
                required_before_confirmation=True,
            ),
        ]

    def _candidate_causes(
        self,
        *,
        telemetry_evidence: list[RcaEvidenceItem],
        supporting_evidence: list[RcaEvidenceItem],
        contradictory_evidence: list[RcaEvidenceItem],
        missing_tests: list[MissingTestRecommendation],
    ) -> list[CandidateRootCause]:
        return [
            CandidateRootCause(
                cause_id="CAUSE-P101-BEARING-DAMAGE",
                title="Bearing damage",
                description=(
                    "Most likely candidate because vibration and bearing "
                    "temperature increased together and inspection evidence "
                    "mentions abnormal drive-end noise."
                ),
                risk_level="critical",
                rank=1,
                confidence=0.78,
                supporting_evidence_ids=[
                    "TEL-P101-NEW-001",
                    "TEL-P101-NEW-002",
                    "IR-P101-001",
                    "INC-P101-NEW-001",
                ],
                contradictory_evidence_ids=[
                    "CONTRA-P101-001",
                ],
                missing_test_ids=[
                    "TEST-P101-BEARING-INSPECTION",
                    "TEST-P101-LUBE-SAMPLE",
                ],
                explanation=(
                    "Ranked first due to strong telemetry and inspection "
                    "support, but confirmation is blocked until bearing "
                    "inspection and lubrication evidence are completed."
                ),
            ),
            CandidateRootCause(
                cause_id="CAUSE-P101-LUBRICATION-DEGRADATION",
                title="Lubrication degradation",
                description=(
                    "Plausible because bearing temperature rose with vibration "
                    "and lubrication evidence is currently incomplete."
                ),
                risk_level="high",
                rank=2,
                confidence=0.69,
                supporting_evidence_ids=[
                    "TEL-P101-NEW-002",
                    "SOP-P101-001",
                    "CONTRA-P101-001",
                ],
                contradictory_evidence_ids=[
                    "CONTRA-P101-001",
                ],
                missing_test_ids=[
                    "TEST-P101-LUBE-SAMPLE",
                ],
                explanation=(
                    "Ranked second because missing lubrication evidence keeps "
                    "it plausible but not confirmed."
                ),
            ),
            CandidateRootCause(
                cause_id="CAUSE-P101-SHAFT-MISALIGNMENT",
                title="Shaft misalignment",
                description=(
                    "Possible contributor to elevated vibration, but current "
                    "evidence is weaker than bearing-related causes."
                ),
                risk_level="medium",
                rank=3,
                confidence=0.42,
                supporting_evidence_ids=[
                    "TEL-P101-NEW-001",
                ],
                contradictory_evidence_ids=[
                    "TEL-P101-NEW-003",
                ],
                missing_test_ids=[
                    "TEST-P101-ALIGNMENT",
                ],
                explanation=(
                    "Kept as an alternative until alignment verification is "
                    "completed."
                ),
            ),
            CandidateRootCause(
                cause_id="CAUSE-P101-CAVITATION",
                title="Cavitation",
                description=(
                    "Less likely because the current evidence does not show "
                    "a major flow collapse."
                ),
                risk_level="low",
                rank=4,
                confidence=0.22,
                supporting_evidence_ids=[],
                contradictory_evidence_ids=[
                    "CONTRA-P101-002",
                ],
                missing_test_ids=[],
                explanation=(
                    "Ranked low because flow evidence contradicts severe "
                    "cavitation."
                ),
            ),
        ]

    def _draft_rca(
        self,
        *,
        request: ControlledRcaRequest,
        candidate_causes: list[CandidateRootCause],
    ) -> RcaDraft:
        top_candidate = candidate_causes[0] if candidate_causes else None

        return RcaDraft(
            rca_case_id=request.rca_case_id,
            asset_id=request.asset_id,
            incident_id=request.incident_id,
            title="Draft RCA for P-101 high vibration and bearing temperature event",
            problem_statement=(
                "P-101 experienced a grouped incident involving critical "
                "vibration, elevated bearing temperature, and abnormal "
                "drive-end noise."
            ),
            draft_summary=(
                "The controlled workflow ranks bearing damage as the leading "
                "candidate and lubrication degradation as a close alternative. "
                "The RCA is a draft only and cannot be confirmed until an "
                "engineer reviews the evidence and required tests are completed."
            ),
            top_candidate_cause_id=top_candidate.cause_id
            if top_candidate
            else None,
            recommendations=[
                "Inspect drive-end bearing condition.",
                "Verify lubrication condition and evidence completeness.",
                "Perform shaft alignment check.",
                "Attach post-maintenance vibration verification before closure.",
            ],
            approval_status="approval_required",
            engineer_approval_required=True,
            auto_confirmation_blocked=True,
            safety_closure_blocked=True,
            critical_work_order_approval_blocked=True,
        )