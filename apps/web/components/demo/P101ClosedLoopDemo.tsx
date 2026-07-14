"use client";

import { P101AnomalyExplanationPanel } from "@/components/demo/P101AnomalyExplanationPanel";
import {
  useMemo,
  useState,
} from "react";

type StepStatus =
  | "pending"
  | "passed"
  | "failed";

type DemoStep = {
  step_id: string;
  title: string;
  status: StepStatus;
  description: string;
  evidence_used: string[];
  ai_confidence: number | null;
  human_approval_required: boolean;
  linked_endpoint: string;
  timestamp: string | null;
};

type DemoState = {
  demo_id: string;
  asset_id: string;
  asset_name: string;
  status: "not_started" | "running" | "completed";
  current_step: number;
  total_steps: number;
  completed_steps: number;
  summary: string;
  judge_message: string;
  steps: DemoStep[];
};

type RunResponse = {
  state: DemoState;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

const INITIAL_DEMO_STATE: DemoState = {
  demo_id: "p101-closed-loop-demo",
  asset_id: "P-101",
  asset_name: "Cooling Water Circulation Pump",
  status: "not_started",
  current_step: 0,
  total_steps: 7,
  completed_steps: 0,
  summary:
    "P-101 closed-loop demo connects telemetry degradation, anomaly detection, incident grouping, evidence-backed RCA, governed maintenance, recovery verification, and audit-ready compliance.",
  judge_message:
    "This demo shows PlantMind as a closed-loop industrial maintenance intelligence system, not only a prediction dashboard or RAG chatbot.",
  steps: [
    {
      step_id: "step-01-telemetry-replay",
      title: "Start P-101 degradation replay",
      status: "pending",
      description:
        "Replay starts from healthy P-101 telemetry and introduces rising vibration and bearing temperature.",
      evidence_used: [],
      ai_confidence: null,
      human_approval_required: false,
      linked_endpoint: "/telemetry/assets/P-101/summary",
      timestamp: null,
    },
    {
      step_id: "step-02-anomaly-detection",
      title: "Detect anomaly",
      status: "pending",
      description:
        "The anomaly model flags persistent vibration and bearing-temperature deviation from the healthy baseline.",
      evidence_used: [],
      ai_confidence: null,
      human_approval_required: false,
      linked_endpoint:
        "/mlops/model-registry/production/plantmind-p101-anomaly-detector",
      timestamp: null,
    },
    {
      step_id: "step-03-incident-created",
      title: "Create grouped incident",
      status: "pending",
      description:
        "PlantMind groups repeated abnormal signals into one maintenance incident instead of creating alert noise.",
      evidence_used: [],
      ai_confidence: null,
      human_approval_required: true,
      linked_endpoint: "/incidents?asset_id=P-101",
      timestamp: null,
    },
    {
      step_id: "step-04-rca-hypothesis",
      title: "Generate RCA hypothesis",
      status: "pending",
      description:
        "Evidence-backed RCA ranks lubrication degradation and bearing damage as likely failure hypotheses while keeping engineer approval mandatory.",
      evidence_used: [],
      ai_confidence: null,
      human_approval_required: true,
      linked_endpoint:
        "/rca-orchestration/cases/RCA-P101-001/history",
      timestamp: null,
    },
    {
      step_id: "step-05-work-order",
      title: "Create governed work order",
      status: "pending",
      description:
        "The RCA output links to a governed maintenance work order with required procedure, safety checks, and evidence.",
      evidence_used: [],
      ai_confidence: null,
      human_approval_required: true,
      linked_endpoint:
        "/maintenance/work-orders/MWO-P101-001/lifecycle",
      timestamp: null,
    },
    {
      step_id: "step-06-recovery-verification",
      title: "Verify recovery",
      status: "pending",
      description:
        "The work order cannot close until post-maintenance verification confirms that vibration and temperature returned to acceptable ranges.",
      evidence_used: [],
      ai_confidence: null,
      human_approval_required: true,
      linked_endpoint:
        "/maintenance/work-orders/MWO-P101-001/post-maintenance-verification/history",
      timestamp: null,
    },
    {
      step_id: "step-07-audit-package",
      title: "Generate audit-ready compliance package",
      status: "pending",
      description:
        "PlantMind packages RCA evidence, maintenance actions, verification status, and missing-evidence checks into an audit-ready compliance view.",
      evidence_used: [],
      ai_confidence: null,
      human_approval_required: false,
      linked_endpoint:
        "/compliance/audit-packages/assets/P-101",
      timestamp: null,
    },
  ],
};

async function fetchJson<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      `Request failed: ${response.status}`
    );
  }

  return response.json() as Promise<T>;
}

function badgeClass(status: StepStatus): string {
  if (status === "passed") {
    return "border-emerald-700 bg-emerald-950/50 text-emerald-300";
  }

  if (status === "failed") {
    return "border-red-700 bg-red-950/50 text-red-300";
  }

  return "border-slate-700 bg-slate-900 text-slate-300";
}

function confidenceLabel(
  value: number | null
): string {
  if (value === null) {
    return "Pending";
  }

  return `${Math.round(value * 100)}%`;
}

export function P101ClosedLoopDemo() {
  const [
    state,
    setState,
  ] = useState<DemoState>(INITIAL_DEMO_STATE);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  const progress = useMemo(() => {
    if (state.total_steps === 0) {
      return 0;
    }

    return Math.round(
      (state.completed_steps / state.total_steps) *
        100
    );
  }, [state]);

  async function runDemo() {
    setLoading(true);
    setError(null);

    try {
      const payload =
        await fetchJson<RunResponse>(
          "/demo/p101/run-closed-loop",
          {
            method: "POST",
          }
        );

      setState(payload.state);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Unable to run demo."
      );
    } finally {
      setLoading(false);
    }
  }

  async function resetDemo() {
    setLoading(true);
    setError(null);

    try {
      const payload =
        await fetchJson<DemoState>(
          "/demo/p101/reset",
          {
            method: "POST",
          }
        );

      setState(payload);
    } catch (caughtError) {
      setState(INITIAL_DEMO_STATE);
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Unable to reset demo."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="border-b border-slate-800">
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            PlantMind Nexus Demo
          </p>

          <div className="mt-4 grid gap-6 lg:grid-cols-[1.4fr_0.6fr]">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight sm:text-5xl">
                P-101 Closed-Loop Industrial Maintenance Intelligence
              </h1>

              <p className="mt-4 max-w-3xl text-base leading-7 text-slate-400">
                From telemetry degradation to anomaly detection,
                incident grouping, evidence-backed RCA, governed
                maintenance, recovery verification, and audit-ready
                compliance.
              </p>
            </div>

            <div className="rounded-2xl border border-cyan-900/70 bg-cyan-950/20 p-5">
              <p className="text-sm text-slate-400">
                Demo progress
              </p>

              <p className="mt-2 text-4xl font-semibold text-cyan-300">
                {progress}%
              </p>

              <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-2 rounded-full bg-cyan-400"
                  style={{
                    width: `${progress}%`,
                  }}
                />
              </div>

              <p className="mt-3 text-sm text-slate-400">
                {state.completed_steps}/{state.total_steps} steps completed
              </p>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => void runDemo()}
              disabled={loading}
              className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-300 disabled:opacity-50"
            >
              Start P-101 Demo
            </button>

            <button
              type="button"
              onClick={() => void resetDemo()}
              disabled={loading}
              className="rounded-full border border-slate-700 px-5 py-3 text-sm font-semibold text-slate-200 hover:bg-slate-900 disabled:opacity-50"
            >
              Reset Demo
            </button>
          </div>

          {error ? (
            <div className="mt-6 rounded-2xl border border-red-800 bg-red-950/40 p-4 text-sm text-red-200">
              Backend unavailable. Showing deterministic demo mode. {error}
            </div>
          ) : null}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
              Demo asset
            </p>

            <h2 className="mt-3 text-2xl font-semibold">
              {state.asset_id} ? {state.asset_name}
            </h2>

            <p className="mt-4 text-sm leading-6 text-slate-400">
              {state.summary}
            </p>
          </div>

          <div className="rounded-2xl border border-emerald-900/70 bg-emerald-950/20 p-6">
            <p className="text-sm uppercase tracking-[0.2em] text-emerald-400">
              Judge message
            </p>

            <p className="mt-3 text-base leading-7 text-emerald-100">
              {state.judge_message}
            </p>
          </div>
        </div>

        <P101AnomalyExplanationPanel />

        <div className="mt-8 grid gap-4">
          {state.steps.map((step, index) => (
            <article
              key={step.step_id}
              className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
            >
              <div className="flex flex-col gap-4 lg:flex-row lg:justify-between">
                <div>
                  <div className="flex flex-wrap gap-3">
                    <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs font-semibold text-slate-300">
                      Step {index + 1}
                    </span>

                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase ${badgeClass(
                        step.status
                      )}`}
                    >
                      {step.status}
                    </span>

                    <span className="rounded-full border border-purple-800 bg-purple-950/40 px-3 py-1 text-xs font-semibold text-purple-200">
                      AI confidence: {confidenceLabel(step.ai_confidence)}
                    </span>
                  </div>

                  <h3 className="mt-4 text-xl font-semibold">
                    {step.title}
                  </h3>

                  <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-400">
                    {step.description}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 text-sm">
                  <p className="text-slate-500">
                    Human approval
                  </p>

                  <p className="mt-1 font-semibold text-slate-100">
                    {step.human_approval_required
                      ? "Required"
                      : "Not required"}
                  </p>
                </div>
              </div>

              <div className="mt-5 grid gap-4 lg:grid-cols-2">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    Evidence used
                  </p>

                  <div className="mt-3 flex flex-wrap gap-2">
                    {step.evidence_used.length ? (
                      step.evidence_used.map((evidence) => (
                        <span
                          key={evidence}
                          className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-300"
                        >
                          {evidence}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-slate-500">
                        Pending until demo run
                      </span>
                    )}
                  </div>
                </div>

                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    Linked endpoint
                  </p>

                  <code className="mt-3 block break-all rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-cyan-300">
                    {step.linked_endpoint}
                  </code>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
