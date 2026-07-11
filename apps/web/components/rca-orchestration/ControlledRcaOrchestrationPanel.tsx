"use client";

import { useMemo, useState } from "react";

import { apiPost } from "@/lib/api";

type WorkflowStepName =
  | "load_incident"
  | "retrieve_telemetry"
  | "retrieve_evidence"
  | "retrieve_approved_documents"
  | "retrieve_similar_cases"
  | "generate_candidate_causes"
  | "rank_causes"
  | "identify_contradictions"
  | "identify_missing_tests"
  | "draft_rca"
  | "request_engineer_approval";

type EvidenceDirection = "supporting" | "contradictory" | "context" | "missing";

type ApprovalStatus = "approval_required" | "approved" | "rejected";

type ControlledRcaRequest = {
  incident_id: string;
  asset_id: string;
  rca_case_id: string;
  requested_by: string;
  include_similar_cases: boolean;
};

type WorkflowStepResult = {
  step_name: WorkflowStepName;
  status: "completed" | "blocked";
  explanation: string;
};

type RcaEvidenceItem = {
  evidence_id: string;
  evidence_type:
    | "telemetry"
    | "incident"
    | "inspection"
    | "maintenance"
    | "document"
    | "similar_case"
    | "operator_report"
    | "compliance";
  title: string;
  summary: string;
  source: string;
  timestamp?: string | null;
  direction: EvidenceDirection;
  reliability: "low" | "medium" | "high";
};

type CandidateRootCause = {
  cause_id: string;
  title: string;
  description: string;
  risk_level: "low" | "medium" | "high" | "critical";
  rank: number;
  confidence: number;
  supporting_evidence_ids: string[];
  contradictory_evidence_ids: string[];
  missing_test_ids: string[];
  explanation: string;
};

type MissingTestRecommendation = {
  test_id: string;
  title: string;
  reason: string;
  priority: "low" | "medium" | "high" | "critical";
  required_before_confirmation: boolean;
};

type RcaDraft = {
  rca_case_id: string;
  asset_id: string;
  incident_id: string;
  title: string;
  problem_statement: string;
  draft_summary: string;
  top_candidate_cause_id: string | null;
  recommendations: string[];
  approval_status: ApprovalStatus;
  engineer_approval_required: boolean;
  auto_confirmation_blocked: boolean;
  safety_closure_blocked: boolean;
  critical_work_order_approval_blocked: boolean;
};

type ControlledRcaResponse = {
  workflow_version: string;
  rca_case_id: string;
  incident_id: string;
  asset_id: string;
  steps: WorkflowStepResult[];
  telemetry_evidence: RcaEvidenceItem[];
  supporting_evidence: RcaEvidenceItem[];
  contradictory_evidence: RcaEvidenceItem[];
  contextual_evidence: RcaEvidenceItem[];
  candidate_causes: CandidateRootCause[];
  missing_tests: MissingTestRecommendation[];
  draft: RcaDraft;
  guardrails: string[];
};

function label(value: string): string {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function fallbackResponse(): ControlledRcaResponse {
  return {
    workflow_version: "controlled-rca-orchestration-v1.0.0",
    rca_case_id: "RCA-P101-001",
    incident_id: "INC-P-101-DEMO",
    asset_id: "P-101",
    steps: [
      {
        step_name: "load_incident",
        status: "completed",
        explanation: "Loaded incident INC-P-101-DEMO for asset P-101.",
      },
      {
        step_name: "retrieve_telemetry",
        status: "completed",
        explanation:
          "Retrieved P-101 vibration, bearing temperature, motor current, and anomaly-score telemetry.",
      },
      {
        step_name: "retrieve_evidence",
        status: "completed",
        explanation:
          "Retrieved inspection, operator, maintenance, and compliance evidence.",
      },
      {
        step_name: "retrieve_approved_documents",
        status: "completed",
        explanation: "Retrieved approved SOPs only. Draft documents are excluded.",
      },
      {
        step_name: "retrieve_similar_cases",
        status: "completed",
        explanation: "Retrieved similar P-101 vibration and bearing temperature case.",
      },
      {
        step_name: "generate_candidate_causes",
        status: "completed",
        explanation: "Generated deterministic candidate causes.",
      },
      {
        step_name: "rank_causes",
        status: "completed",
        explanation: "Ranked causes using visible evidence and contradictions.",
      },
      {
        step_name: "identify_contradictions",
        status: "completed",
        explanation: "Identified contradictory evidence for each candidate.",
      },
      {
        step_name: "identify_missing_tests",
        status: "completed",
        explanation: "Identified tests required before confirmation.",
      },
      {
        step_name: "draft_rca",
        status: "completed",
        explanation: "Drafted RCA. No root cause was confirmed automatically.",
      },
      {
        step_name: "request_engineer_approval",
        status: "completed",
        explanation: "Engineer approval is required before confirmation.",
      },
    ],
    telemetry_evidence: [
      {
        evidence_id: "TEL-P101-NEW-001",
        evidence_type: "telemetry",
        title: "P-101 vibration crossed critical threshold",
        summary:
          "Replay telemetry shows vibration increasing from normal range to critical range before the incident.",
        source: "telemetry_replay:P101-VIB-001",
        timestamp: "2026-07-10T09:00:30+00:00",
        direction: "supporting",
        reliability: "high",
      },
      {
        evidence_id: "TEL-P101-NEW-002",
        evidence_type: "telemetry",
        title: "P-101 bearing temperature increased with vibration",
        summary:
          "Bearing temperature rose with vibration, supporting bearing or lubrication-related degradation.",
        source: "telemetry_replay:P101-BTEMP-001",
        timestamp: "2026-07-10T09:00:30+00:00",
        direction: "supporting",
        reliability: "high",
      },
      {
        evidence_id: "TEL-P101-NEW-003",
        evidence_type: "telemetry",
        title: "Motor current did not spike proportionally",
        summary:
          "Motor current stayed comparatively stable, making severe electrical overload less likely.",
        source: "telemetry_replay:P101-CURRENT-001",
        timestamp: "2026-07-10T09:00:30+00:00",
        direction: "contradictory",
        reliability: "medium",
      },
    ],
    supporting_evidence: [
      {
        evidence_id: "INC-P101-NEW-001",
        evidence_type: "incident",
        title: "Grouped P-101 vibration and temperature incident",
        summary:
          "Incident management grouped related P-101 anomalies into one incident linked to RCA-P101-001.",
        source: "INC-P-101-DEMO",
        timestamp: "2026-07-10T09:00:30+00:00",
        direction: "supporting",
        reliability: "high",
      },
      {
        evidence_id: "IR-P101-001",
        evidence_type: "inspection",
        title: "Drive-end abnormal noise inspection finding",
        summary:
          "Inspection evidence reports abnormal drive-end noise consistent with bearing degradation.",
        source: "inspection_report:IR-P101-001",
        timestamp: "2026-07-10T09:05:00+00:00",
        direction: "supporting",
        reliability: "high",
      },
    ],
    contradictory_evidence: [
      {
        evidence_id: "CONTRA-P101-001",
        evidence_type: "maintenance",
        title: "No confirmed lubrication sample yet",
        summary:
          "Lubrication degradation is plausible, but no lubrication quality test has confirmed it.",
        source: "maintenance_gap:P101-LUBE-SAMPLE",
        direction: "contradictory",
        reliability: "medium",
      },
      {
        evidence_id: "CONTRA-P101-002",
        evidence_type: "telemetry",
        title: "Flow did not collapse during the event",
        summary:
          "Flow stayed within usable range, making severe cavitation less likely.",
        source: "telemetry_replay:P101-FLOW-001",
        timestamp: "2026-07-10T09:00:30+00:00",
        direction: "contradictory",
        reliability: "medium",
      },
    ],
    contextual_evidence: [
      {
        evidence_id: "SIMILAR-P101-001",
        evidence_type: "similar_case",
        title: "Previous P-101 vibration and bearing temperature case",
        summary:
          "Similar case ranked bearing inspection and lubrication verification as first-line checks.",
        source: "similar_case:RCA-P101-PRIOR-001",
        direction: "context",
        reliability: "medium",
      },
    ],
    candidate_causes: [
      {
        cause_id: "CAUSE-P101-BEARING-DAMAGE",
        title: "Bearing damage",
        description:
          "Most likely candidate because vibration and bearing temperature increased together with abnormal drive-end noise.",
        risk_level: "critical",
        rank: 1,
        confidence: 0.78,
        supporting_evidence_ids: [
          "TEL-P101-NEW-001",
          "TEL-P101-NEW-002",
          "IR-P101-001",
          "INC-P101-NEW-001",
        ],
        contradictory_evidence_ids: ["CONTRA-P101-001"],
        missing_test_ids: [
          "TEST-P101-BEARING-INSPECTION",
          "TEST-P101-LUBE-SAMPLE",
        ],
        explanation:
          "Ranked first, but confirmation is blocked until bearing inspection and lubrication evidence are completed.",
      },
      {
        cause_id: "CAUSE-P101-LUBRICATION-DEGRADATION",
        title: "Lubrication degradation",
        description:
          "Plausible because bearing temperature rose with vibration and lubrication evidence is incomplete.",
        risk_level: "high",
        rank: 2,
        confidence: 0.69,
        supporting_evidence_ids: ["TEL-P101-NEW-002"],
        contradictory_evidence_ids: ["CONTRA-P101-001"],
        missing_test_ids: ["TEST-P101-LUBE-SAMPLE"],
        explanation:
          "Ranked second because missing lubrication evidence keeps it plausible but unconfirmed.",
      },
    ],
    missing_tests: [
      {
        test_id: "TEST-P101-BEARING-INSPECTION",
        title: "Inspect drive-end bearing condition",
        reason:
          "Required to distinguish bearing damage from lubrication degradation.",
        priority: "critical",
        required_before_confirmation: true,
      },
      {
        test_id: "TEST-P101-LUBE-SAMPLE",
        title: "Verify lubrication condition",
        reason:
          "Lubrication degradation cannot be confirmed without lubrication evidence.",
        priority: "high",
        required_before_confirmation: true,
      },
      {
        test_id: "TEST-P101-ALIGNMENT",
        title: "Verify shaft alignment",
        reason:
          "Shaft misalignment remains an alternative until alignment is checked.",
        priority: "medium",
        required_before_confirmation: true,
      },
    ],
    draft: {
      rca_case_id: "RCA-P101-001",
      asset_id: "P-101",
      incident_id: "INC-P-101-DEMO",
      title: "Draft RCA for P-101 high vibration and bearing temperature event",
      problem_statement:
        "P-101 experienced grouped critical vibration, elevated bearing temperature, and abnormal drive-end noise.",
      draft_summary:
        "Bearing damage is ranked first and lubrication degradation is ranked second. This is a draft only and cannot be confirmed until engineer approval.",
      top_candidate_cause_id: "CAUSE-P101-BEARING-DAMAGE",
      recommendations: [
        "Inspect drive-end bearing condition.",
        "Verify lubrication condition and evidence completeness.",
        "Perform shaft alignment check.",
        "Attach post-maintenance vibration verification before closure.",
      ],
      approval_status: "approval_required",
      engineer_approval_required: true,
      auto_confirmation_blocked: true,
      safety_closure_blocked: true,
      critical_work_order_approval_blocked: true,
    },
    guardrails: [
      "The workflow can draft, rank, retrieve, and recommend.",
      "The workflow cannot confirm root cause automatically.",
      "The workflow cannot close a safety incident.",
      "The workflow cannot approve a critical work order.",
      "Engineer approval is required before RCA confirmation.",
    ],
  };
}

function EvidenceCard({ evidence }: { evidence: RcaEvidenceItem }) {
  return (
    <div className="rounded-xl border border-slate-200 p-4">
      <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="font-semibold text-slate-950">{evidence.title}</p>
          <p className="mt-1 text-xs text-slate-500">
            {evidence.evidence_id} · {label(evidence.evidence_type)} ·{" "}
            {label(evidence.direction)}
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          {label(evidence.reliability)}
        </span>
      </div>

      <p className="mt-3 text-sm leading-6 text-slate-600">
        {evidence.summary}
      </p>

      <p className="mt-3 text-xs text-slate-500">
        Source: {evidence.source}
      </p>
    </div>
  );
}

export function ControlledRcaOrchestrationPanel() {
  const [response, setResponse] = useState<ControlledRcaResponse>(() =>
    fallbackResponse(),
  );
  const [status, setStatus] = useState(
    "Using local controlled RCA orchestration preview.",
  );

  const orderedCauses = useMemo(() => {
    return [...response.candidate_causes].sort(
      (left, right) => left.rank - right.rank,
    );
  }, [response.candidate_causes]);

  async function runBackendWorkflow() {
    setStatus("Running controlled RCA orchestration through backend...");

    try {
      const backendResponse = await apiPost<
        ControlledRcaRequest,
        ControlledRcaResponse
      >(
        "/rca-orchestration/run",
        {
          incident_id: "INC-P-101-DEMO",
          asset_id: "P-101",
          rca_case_id: "RCA-P101-001",
          requested_by: "maintenance_engineer",
          include_similar_cases: true,
        },
      );

      setResponse(backendResponse);
      setStatus("Backend controlled RCA orchestration completed successfully.");
    } catch {
      setResponse(fallbackResponse());
      setStatus(
        "Backend unavailable. Showing local controlled RCA orchestration preview.",
      );
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Controlled RCA Orchestration
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">
              Evidence-backed RCA draft for RCA-P101-001
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              This is a deterministic RCA workflow. It can retrieve evidence,
              rank causes, identify contradictions, identify missing tests,
              draft RCA, and request engineer approval. It cannot confirm root
              cause automatically or close safety-critical work.
            </p>
          </div>

          <button
            type="button"
            onClick={runBackendWorkflow}
            className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
          >
            Run backend workflow
          </button>
        </div>

        <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          {status}
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Draft status
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">
              {response.draft.title}
            </h2>

            <div className="mt-6 grid gap-3 text-sm text-slate-700">
              <p>
                <span className="font-semibold">RCA case:</span>{" "}
                {response.rca_case_id}
              </p>
              <p>
                <span className="font-semibold">Incident:</span>{" "}
                {response.incident_id}
              </p>
              <p>
                <span className="font-semibold">Asset:</span>{" "}
                {response.asset_id}
              </p>
              <p>
                <span className="font-semibold">Approval:</span>{" "}
                {label(response.draft.approval_status)}
              </p>
              <p>
                <span className="font-semibold">Top candidate:</span>{" "}
                {response.draft.top_candidate_cause_id}
              </p>
            </div>

            <p className="mt-6 rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
              {response.draft.draft_summary}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Guardrails
            </p>
            <div className="mt-4 space-y-3">
              {response.guardrails.map((guardrail) => (
                <p
                  key={guardrail}
                  className="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-700"
                >
                  {guardrail}
                </p>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Deterministic workflow
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            No unrestricted autonomous agent
          </h2>

          <div className="mt-6 space-y-3">
            {response.steps.map((step, index) => (
              <div
                key={step.step_name}
                className="rounded-xl border border-slate-200 p-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <p className="font-semibold text-slate-950">
                    {index + 1}. {label(step.step_name)}
                  </p>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                    {label(step.status)}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {step.explanation}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            New telemetry evidence
          </p>
          <div className="mt-4 space-y-4">
            {response.telemetry_evidence.map((evidence) => (
              <EvidenceCard key={evidence.evidence_id} evidence={evidence} />
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Supporting evidence
          </p>
          <div className="mt-4 space-y-4">
            {response.supporting_evidence.map((evidence) => (
              <EvidenceCard key={evidence.evidence_id} evidence={evidence} />
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Contradictory evidence
          </p>
          <div className="mt-4 space-y-4">
            {response.contradictory_evidence.map((evidence) => (
              <EvidenceCard key={evidence.evidence_id} evidence={evidence} />
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Ranked candidate causes
          </p>

          <div className="mt-4 space-y-4">
            {orderedCauses.map((cause) => (
              <div
                key={cause.cause_id}
                className="rounded-xl border border-slate-200 p-4"
              >
                <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p className="font-semibold text-slate-950">
                      #{cause.rank} {cause.title}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {cause.cause_id} · {label(cause.risk_level)} ·{" "}
                      {(cause.confidence * 100).toFixed(0)}% heuristic confidence
                    </p>
                  </div>
                </div>

                <p className="mt-3 text-sm leading-6 text-slate-600">
                  {cause.explanation}
                </p>

                <div className="mt-4 grid gap-3 text-xs text-slate-600 md:grid-cols-3">
                  <p>
                    <span className="font-semibold">Supporting:</span>{" "}
                    {cause.supporting_evidence_ids.length}
                  </p>
                  <p>
                    <span className="font-semibold">Contradictory:</span>{" "}
                    {cause.contradictory_evidence_ids.length}
                  </p>
                  <p>
                    <span className="font-semibold">Missing tests:</span>{" "}
                    {cause.missing_test_ids.length}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Missing tests
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Required before confirmation
          </h2>

          <div className="mt-4 space-y-4">
            {response.missing_tests.map((test) => (
              <div
                key={test.test_id}
                className="rounded-xl border border-slate-200 p-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <p className="font-semibold text-slate-950">{test.title}</p>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                    {label(test.priority)}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {test.reason}
                </p>
                <p className="mt-3 text-xs font-medium text-slate-500">
                  Confirmation blocked:{" "}
                  {test.required_before_confirmation ? "Yes" : "No"}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}