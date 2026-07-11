"use client";

import { useMemo, useState } from "react";

import { apiPost } from "@/lib/api";

type VerificationOutcome =
  | "successful"
  | "partially_successful"
  | "failed"
  | "insufficient_evidence";

type VerificationMetricStatus = "passed" | "failed" | "missing";

type TelemetrySnapshot = {
  vibration_mm_s?: number | null;
  bearing_temperature_c?: number | null;
  health_score?: number | null;
  anomaly_score?: number | null;
  failure_probability?: number | null;
};

type VerificationCriteria = {
  max_vibration_mm_s: number;
  max_bearing_temperature_c: number;
  min_health_score: number;
  max_anomaly_score: number;
  max_failure_probability: number;
  minimum_passed_metrics_for_partial_success: number;
};

type MetricComparison = {
  metric_name: string;
  pre_value: number | null;
  post_value: number | null;
  target: number;
  status: VerificationMetricStatus;
  explanation: string;
};

type MaintenanceRecoveryReplayRequest = {
  work_order_id: string;
  asset_id: string;
  scenario:
    | "successful_recovery"
    | "partial_recovery"
    | "failed_recovery"
    | "insufficient_evidence";
  verified_by: string;
  verified_at: string;
};

type PostMaintenanceVerificationResult = {
  verification_id: string;
  work_order_id: string;
  asset_id: string;
  verified_by: string;
  verified_at: string;
  outcome: VerificationOutcome;
  pre_maintenance: TelemetrySnapshot;
  post_maintenance: TelemetrySnapshot;
  criteria: VerificationCriteria;
  metric_comparisons: MetricComparison[];
  passed_metric_count: number;
  failed_metric_count: number;
  missing_metric_count: number;
  readings_normalized: boolean;
  can_mark_verified: boolean;
  should_reopen_work_order: boolean;
  explanation: string;
};

type Scenario =
  | "successful_recovery"
  | "partial_recovery"
  | "failed_recovery"
  | "insufficient_evidence";

const scenarioLabels: Record<Scenario, string> = {
  successful_recovery: "Successful recovery",
  partial_recovery: "Partial recovery",
  failed_recovery: "Failed recovery",
  insufficient_evidence: "Insufficient evidence",
};

function label(value: string): string {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function displayValue(value?: number | null): string {
  if (value === null || value === undefined) {
    return "Missing";
  }

  return String(value);
}

function fallbackResult(): PostMaintenanceVerificationResult {
  return {
    verification_id: "PMV-DEMO-SUCCESSFUL",
    work_order_id: "WO-P101-COMPLETE-001",
    asset_id: "P-101",
    verified_by: "maintenance.engineer",
    verified_at: "2026-07-10T10:00:00+00:00",
    outcome: "successful",
    pre_maintenance: {
      vibration_mm_s: 8.8,
      bearing_temperature_c: 94,
      health_score: 42,
      anomaly_score: 0.91,
      failure_probability: 0.82,
    },
    post_maintenance: {
      vibration_mm_s: 2.4,
      bearing_temperature_c: 66,
      health_score: 88,
      anomaly_score: 0.12,
      failure_probability: 0.14,
    },
    criteria: {
      max_vibration_mm_s: 3.5,
      max_bearing_temperature_c: 75,
      min_health_score: 80,
      max_anomaly_score: 0.3,
      max_failure_probability: 0.25,
      minimum_passed_metrics_for_partial_success: 3,
    },
    metric_comparisons: [
      {
        metric_name: "vibration_mm_s",
        pre_value: 8.8,
        post_value: 2.4,
        target: 3.5,
        status: "passed",
        explanation:
          "Vibration normalized from 8.8 mm/s to 2.4 mm/s, within the target threshold.",
      },
      {
        metric_name: "bearing_temperature_c",
        pre_value: 94,
        post_value: 66,
        target: 75,
        status: "passed",
        explanation:
          "Bearing temperature reduced from 94°C to 66°C, within the target threshold.",
      },
      {
        metric_name: "health_score",
        pre_value: 42,
        post_value: 88,
        target: 80,
        status: "passed",
        explanation:
          "Health score improved from 42 to 88 and meets the minimum health target.",
      },
      {
        metric_name: "anomaly_score",
        pre_value: 0.91,
        post_value: 0.12,
        target: 0.3,
        status: "passed",
        explanation:
          "Anomaly score reduced from 0.91 to 0.12 and is within threshold.",
      },
      {
        metric_name: "failure_probability",
        pre_value: 0.82,
        post_value: 0.14,
        target: 0.25,
        status: "passed",
        explanation:
          "Failure probability reduced from 0.82 to 0.14 and is within threshold.",
      },
    ],
    passed_metric_count: 5,
    failed_metric_count: 0,
    missing_metric_count: 0,
    readings_normalized: true,
    can_mark_verified: true,
    should_reopen_work_order: false,
    explanation:
      "Post-maintenance verification passed. The work order can enter Verified.",
  };
}

function outcomeExplanation(outcome: VerificationOutcome): string {
  if (outcome === "successful") {
    return "All verification criteria passed. The work order may enter Verified.";
  }

  if (outcome === "partially_successful") {
    return "Some metrics improved, but verification is not complete. Keep the work order in Verification Pending.";
  }

  if (outcome === "failed") {
    return "Recovery failed. The work order should be reopened to In Progress.";
  }

  return "Evidence is missing. The work order cannot be verified yet.";
}

export function PostMaintenanceVerificationPanel() {
  const [selectedScenario, setSelectedScenario] =
    useState<Scenario>("successful_recovery");
  const [result, setResult] = useState<PostMaintenanceVerificationResult>(() =>
    fallbackResult(),
  );
  const [status, setStatus] = useState(
    "Using local post-maintenance verification preview.",
  );

  const metricSummary = useMemo(() => {
    return [
      {
        label: "Passed",
        value: result.passed_metric_count,
      },
      {
        label: "Failed",
        value: result.failed_metric_count,
      },
      {
        label: "Missing",
        value: result.missing_metric_count,
      },
    ];
  }, [result]);

  async function runBackendReplay(scenario: Scenario) {
    setSelectedScenario(scenario);
    setStatus(`Running ${scenarioLabels[scenario]} replay through backend...`);

    try {
      const backendResult = await apiPost<
        MaintenanceRecoveryReplayRequest,
        PostMaintenanceVerificationResult
      >(
        "/maintenance/work-orders/WO-P101-COMPLETE-001/post-maintenance-verification/replay",
        {
          work_order_id: "WO-P101-COMPLETE-001",
          asset_id: "P-101",
          scenario,
          verified_by: "maintenance.engineer",
          verified_at: new Date().toISOString(),
        },
      );

      setResult(backendResult);
      setStatus(`${scenarioLabels[scenario]} replay completed successfully.`);
    } catch {
      setResult(fallbackResult());
      setStatus(
        "Backend unavailable. Showing local successful recovery verification preview.",
      );
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Post-maintenance verification
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">
              Verify recovery before closing maintenance
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              This compares pre-maintenance telemetry with post-maintenance
              telemetry, health score, anomaly score, failure probability, and
              verification criteria. A work order can enter Verified only after
              successful verification. Failed recovery can reopen the work order.
            </p>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          {(Object.keys(scenarioLabels) as Scenario[]).map((scenario) => (
            <button
              key={scenario}
              type="button"
              onClick={() => runBackendReplay(scenario)}
              className={`rounded-xl px-4 py-2 text-sm font-semibold shadow-sm transition ${
                selectedScenario === scenario
                  ? "bg-slate-950 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {scenarioLabels[scenario]}
            </button>
          ))}
        </div>

        <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          {status}
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Verification result
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            {label(result.outcome)}
          </h2>

          <p className="mt-3 text-sm leading-6 text-slate-600">
            {outcomeExplanation(result.outcome)}
          </p>

          <div className="mt-6 grid gap-3 text-sm text-slate-700">
            <p>
              <span className="font-semibold">Verification:</span>{" "}
              {result.verification_id}
            </p>
            <p>
              <span className="font-semibold">Work order:</span>{" "}
              {result.work_order_id}
            </p>
            <p>
              <span className="font-semibold">Asset:</span> {result.asset_id}
            </p>
            <p>
              <span className="font-semibold">Readings normalized:</span>{" "}
              {result.readings_normalized ? "Yes" : "No"}
            </p>
            <p>
              <span className="font-semibold">Can mark verified:</span>{" "}
              {result.can_mark_verified ? "Yes" : "No"}
            </p>
            <p>
              <span className="font-semibold">Should reopen work order:</span>{" "}
              {result.should_reopen_work_order ? "Yes" : "No"}
            </p>
          </div>

          <div className="mt-6 grid grid-cols-3 gap-3">
            {metricSummary.map((item) => (
              <div
                key={item.label}
                className="rounded-xl bg-slate-50 p-4 text-center"
              >
                <p className="text-2xl font-semibold text-slate-950">
                  {item.value}
                </p>
                <p className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
                  {item.label}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Pre vs post telemetry
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Maintenance recovery replay
          </h2>

          <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Metric</th>
                  <th className="px-4 py-3">Pre</th>
                  <th className="px-4 py-3">Post</th>
                  <th className="px-4 py-3">Target</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {result.metric_comparisons.map((metric) => (
                  <tr key={metric.metric_name}>
                    <td className="px-4 py-3 font-medium text-slate-950">
                      {label(metric.metric_name)}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {displayValue(metric.pre_value)}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {displayValue(metric.post_value)}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {metric.target}
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                        {label(metric.status)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Verification criteria
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Required to enter Verified
          </h2>

          <div className="mt-6 grid gap-3 text-sm text-slate-700">
            <p>
              Vibration must be ≤{" "}
              <span className="font-semibold">
                {result.criteria.max_vibration_mm_s} mm/s
              </span>
            </p>
            <p>
              Bearing temperature must be ≤{" "}
              <span className="font-semibold">
                {result.criteria.max_bearing_temperature_c} °C
              </span>
            </p>
            <p>
              Health score must be ≥{" "}
              <span className="font-semibold">
                {result.criteria.min_health_score}
              </span>
            </p>
            <p>
              Anomaly score must be ≤{" "}
              <span className="font-semibold">
                {result.criteria.max_anomaly_score}
              </span>
            </p>
            <p>
              Failure probability must be ≤{" "}
              <span className="font-semibold">
                {result.criteria.max_failure_probability}
              </span>
            </p>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Decision logic
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Verified gate and reopen rule
          </h2>

          <div className="mt-6 space-y-4">
            <div className="rounded-xl border border-slate-200 p-4">
              <p className="font-semibold text-slate-950">
                Verified transition gate
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Work order can enter Verified only when the verification outcome
                is Successful and a verification reference is attached.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
              <p className="font-semibold text-slate-950">
                Failed recovery reopen
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                If recovery fails, the work order can move from Verification
                Pending back to In Progress for additional maintenance.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
              <p className="font-semibold text-slate-950">
                Insufficient evidence block
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Missing post-maintenance evidence prevents verification and
                keeps the work order from being closed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}