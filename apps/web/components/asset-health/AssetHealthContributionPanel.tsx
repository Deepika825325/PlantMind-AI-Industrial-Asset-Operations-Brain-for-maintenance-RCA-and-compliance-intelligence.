"use client";

import { useMemo, useState } from "react";

import { apiPost } from "@/lib/api";

type ReplayState =
  | "normal_operation"
  | "bearing_degradation"
  | "shaft_misalignment"
  | "cavitation"
  | "sensor_failure"
  | "maintenance_recovery";

type HealthBand = "healthy" | "watch" | "degraded" | "critical";

type HealthFactorContribution = {
  factor_name: string;
  label: string;
  input_value: number | string;
  risk_points: number;
  max_risk_points: number;
  contribution_direction: "lowers_health" | "raises_health" | "neutral";
  explanation: string;
};

type HealthScoreDelta = {
  previous_score: number | null;
  current_score: number;
  delta: number;
  direction: "improved" | "declined" | "unchanged" | "initial";
  explanation: string;
};

type AssetHealthScore = {
  asset_id: string;
  timestamp: string;
  model_version: string;
  scoring_method: string;
  base_score: number;
  health_score: number;
  health_band: HealthBand;
  total_risk_points: number;
  replay_state: ReplayState | null;
  factor_contributions: HealthFactorContribution[];
  score_delta: HealthScoreDelta;
  explanation: string;
};

type AssetHealthReplayResponse = {
  asset_id: string;
  model_version: string;
  score_count: number;
  scores: AssetHealthScore[];
};

type AssetHealthInput = {
  asset_id: string;
  timestamp: string;
  sensor_anomaly_score: number;
  failure_probability: number;
  open_incident_severity: "none" | "low" | "medium" | "high" | "critical";
  open_work_orders: number;
  overdue_work_orders: number;
  compliance_risk_score: number;
  asset_criticality: "low" | "medium" | "high" | "critical";
  recent_failure_count: number;
  sensor_quality_score: number;
  replay_state: ReplayState;
};

const baseTime = new Date("2026-07-10T09:00:00.000Z");

function timestamp(index: number): string {
  return new Date(baseTime.getTime() + index * 10_000).toISOString();
}

function replayReadings(): AssetHealthInput[] {
  return [
    {
      asset_id: "P-101",
      timestamp: timestamp(0),
      sensor_anomaly_score: 0.05,
      failure_probability: 0.05,
      open_incident_severity: "none",
      open_work_orders: 0,
      overdue_work_orders: 0,
      compliance_risk_score: 0.1,
      asset_criticality: "high",
      recent_failure_count: 0,
      sensor_quality_score: 0.98,
      replay_state: "normal_operation",
    },
    {
      asset_id: "P-101",
      timestamp: timestamp(1),
      sensor_anomaly_score: 0.82,
      failure_probability: 0.75,
      open_incident_severity: "high",
      open_work_orders: 4,
      overdue_work_orders: 2,
      compliance_risk_score: 0.7,
      asset_criticality: "high",
      recent_failure_count: 2,
      sensor_quality_score: 0.85,
      replay_state: "bearing_degradation",
    },
    {
      asset_id: "P-101",
      timestamp: timestamp(2),
      sensor_anomaly_score: 0.12,
      failure_probability: 0.18,
      open_incident_severity: "low",
      open_work_orders: 1,
      overdue_work_orders: 0,
      compliance_risk_score: 0.2,
      asset_criticality: "high",
      recent_failure_count: 1,
      sensor_quality_score: 0.96,
      replay_state: "maintenance_recovery",
    },
  ];
}

function localScore(reading: AssetHealthInput, previousScore: number | null): AssetHealthScore {
  const weights = {
    sensor_anomaly_score: 22,
    failure_probability: 18,
    open_incident_severity: 15,
    work_order_status: 12,
    compliance_risk: 10,
    asset_criticality: 8,
    recent_failure_history: 8,
    sensor_quality: 7,
  };

  const incidentPoints = {
    none: 0,
    low: 3,
    medium: 7,
    high: 11,
    critical: 15,
  }[reading.open_incident_severity];

  const criticalityPoints = {
    low: 2,
    medium: 4,
    high: 6,
    critical: 8,
  }[reading.asset_criticality];

  const factors: HealthFactorContribution[] = [
    {
      factor_name: "sensor_anomaly_score",
      label: "Sensor anomaly score",
      input_value: reading.sensor_anomaly_score,
      risk_points: Number((reading.sensor_anomaly_score * weights.sensor_anomaly_score).toFixed(4)),
      max_risk_points: weights.sensor_anomaly_score,
      contribution_direction: "lowers_health",
      explanation: "Sensor anomaly risk is directly visible and deducted from the base score.",
    },
    {
      factor_name: "failure_probability",
      label: "Failure probability",
      input_value: reading.failure_probability,
      risk_points: Number((reading.failure_probability * weights.failure_probability).toFixed(4)),
      max_risk_points: weights.failure_probability,
      contribution_direction: "lowers_health",
      explanation: "Failure classification confidence is converted into visible risk points.",
    },
    {
      factor_name: "open_incident_severity",
      label: "Open incident severity",
      input_value: reading.open_incident_severity,
      risk_points: incidentPoints,
      max_risk_points: weights.open_incident_severity,
      contribution_direction: incidentPoints > 0 ? "lowers_health" : "neutral",
      explanation: "Open incident severity adds fixed visible risk points.",
    },
    {
      factor_name: "work_order_status",
      label: "Work-order status",
      input_value: `${reading.open_work_orders} open, ${reading.overdue_work_orders} overdue`,
      risk_points: Math.min(
        weights.work_order_status,
        Number((reading.open_work_orders * 1.2 + reading.overdue_work_orders * 4).toFixed(4)),
      ),
      max_risk_points: weights.work_order_status,
      contribution_direction: "lowers_health",
      explanation: "Open and overdue work orders reduce the health score.",
    },
    {
      factor_name: "compliance_risk",
      label: "Compliance risk",
      input_value: reading.compliance_risk_score,
      risk_points: Number((reading.compliance_risk_score * weights.compliance_risk).toFixed(4)),
      max_risk_points: weights.compliance_risk,
      contribution_direction: "lowers_health",
      explanation: "Compliance risk is exposed as a visible score contribution.",
    },
    {
      factor_name: "asset_criticality",
      label: "Asset criticality",
      input_value: reading.asset_criticality,
      risk_points: criticalityPoints,
      max_risk_points: weights.asset_criticality,
      contribution_direction: "lowers_health",
      explanation: "Critical assets keep a visible baseline risk.",
    },
    {
      factor_name: "recent_failure_history",
      label: "Recent failure history",
      input_value: reading.recent_failure_count,
      risk_points: Math.min(weights.recent_failure_history, reading.recent_failure_count * 2.5),
      max_risk_points: weights.recent_failure_history,
      contribution_direction: reading.recent_failure_count > 0 ? "lowers_health" : "neutral",
      explanation: "Recent failures reduce confidence in asset health.",
    },
    {
      factor_name: "sensor_quality",
      label: "Sensor quality",
      input_value: reading.sensor_quality_score,
      risk_points: Number(((1 - reading.sensor_quality_score) * weights.sensor_quality).toFixed(4)),
      max_risk_points: weights.sensor_quality,
      contribution_direction: reading.sensor_quality_score < 1 ? "lowers_health" : "neutral",
      explanation: "Lower sensor quality creates visible uncertainty risk.",
    },
  ];

  const totalRisk = Number(
    factors.reduce((sum, factor) => sum + factor.risk_points, 0).toFixed(4),
  );
  const healthScore = Number(Math.max(0, 100 - totalRisk).toFixed(4));
  const delta = previousScore === null ? 0 : Number((healthScore - previousScore).toFixed(4));

  const direction =
    previousScore === null
      ? "initial"
      : delta > 0
        ? "improved"
        : delta < 0
          ? "declined"
          : "unchanged";

  const band: HealthBand =
    healthScore >= 85
      ? "healthy"
      : healthScore >= 70
        ? "watch"
        : healthScore >= 50
          ? "degraded"
          : "critical";

  return {
    asset_id: reading.asset_id,
    timestamp: reading.timestamp,
    model_version: "asset-health-explainable-v1.0.0",
    scoring_method: "Local UI fallback mirrors backend explainable visible risk deduction.",
    base_score: 100,
    health_score: healthScore,
    health_band: band,
    total_risk_points: totalRisk,
    replay_state: reading.replay_state,
    factor_contributions: factors,
    score_delta: {
      previous_score: previousScore,
      current_score: healthScore,
      delta,
      direction,
      explanation:
        previousScore === null
          ? "Initial score. No previous score exists for comparison."
          : `Health score ${direction} by ${Math.abs(delta)} points.`,
    },
    explanation: `Health score is ${healthScore} because visible risk contribution is ${totalRisk}. No hidden factor is applied.`,
  };
}

function fallbackReplay(): AssetHealthReplayResponse {
  const readings = replayReadings();
  const scores: AssetHealthScore[] = [];

  readings.forEach((reading) => {
    const previousScore = scores.length > 0 ? scores[scores.length - 1].health_score : null;
    scores.push(localScore(reading, previousScore));
  });

  return {
    asset_id: "P-101",
    model_version: "asset-health-explainable-v1.0.0",
    score_count: scores.length,
    scores,
  };
}

function formatState(state: ReplayState | null): string {
  if (!state) {
    return "Unknown state";
  }

  return state
    .split("_")
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(" ");
}

function bandLabel(score: AssetHealthScore): string {
  return `${score.health_score.toFixed(1)} / 100 · ${score.health_band.toUpperCase()}`;
}

export function AssetHealthContributionPanel() {
  const [response, setResponse] = useState<AssetHealthReplayResponse>(() => fallbackReplay());
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [status, setStatus] = useState("Using local replay preview.");

  const selectedScore = response.scores[selectedIndex] ?? response.scores[0];

  const sortedFactors = useMemo(() => {
    return [...selectedScore.factor_contributions].sort(
      (left, right) => right.risk_points - left.risk_points,
    );
  }, [selectedScore]);

  async function runBackendReplay() {
    setStatus("Scoring replay through backend...");

    try {
      const backendResponse = await apiPost<
        {
          asset_id: string;
          readings: AssetHealthInput[];
        },
        AssetHealthReplayResponse
      >(
        "/asset-health/replay",
        {
          asset_id: "P-101",
          readings: replayReadings(),
        },
      );

      setResponse(backendResponse);
      setSelectedIndex(0);
      setStatus("Backend replay scored successfully.");
    } catch {
      setResponse(fallbackReplay());
      setSelectedIndex(0);
      setStatus("Backend unavailable. Showing local explainable replay preview.");
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Explainable Asset Health
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">
              P-101 health score with visible factor contribution
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              The score combines sensor anomaly score, failure probability,
              incident severity, work-order status, compliance risk, asset
              criticality, recent failure history, and sensor quality. Every
              change is explained. No hidden arbitrary score is applied.
            </p>
          </div>

          <button
            type="button"
            onClick={runBackendReplay}
            className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
          >
            Run backend replay
          </button>
        </div>

        <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          {status}
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {response.scores.map((score, index) => (
          <button
            key={`${score.timestamp}-${score.replay_state}`}
            type="button"
            onClick={() => setSelectedIndex(index)}
            className={`rounded-2xl border p-5 text-left shadow-sm transition ${
              selectedIndex === index
                ? "border-slate-950 bg-slate-950 text-white"
                : "border-slate-200 bg-white text-slate-950 hover:border-slate-400"
            }`}
          >
            <p className="text-sm font-medium opacity-80">
              {formatState(score.replay_state)}
            </p>
            <p className="mt-3 text-3xl font-semibold">
              {score.health_score.toFixed(1)}
            </p>
            <p className="mt-1 text-sm opacity-80">
              {score.health_band.toUpperCase()}
            </p>
            <p className="mt-4 text-xs opacity-80">
              {score.score_delta.explanation}
            </p>
          </button>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Current state
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            {formatState(selectedScore.replay_state)}
          </h2>
          <p className="mt-3 text-4xl font-semibold text-slate-950">
            {bandLabel(selectedScore)}
          </p>

          <div className="mt-6 space-y-3 text-sm text-slate-700">
            <p>
              <span className="font-semibold">Total visible risk:</span>{" "}
              {selectedScore.total_risk_points.toFixed(1)} points
            </p>
            <p>
              <span className="font-semibold">Model:</span>{" "}
              {selectedScore.model_version}
            </p>
            <p>
              <span className="font-semibold">Delta:</span>{" "}
              {selectedScore.score_delta.direction}{" "}
              {selectedScore.score_delta.delta.toFixed(1)} points
            </p>
          </div>

          <p className="mt-6 rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
            {selectedScore.explanation}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
                Contribution breakdown
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-950">
                Every factor is visible
              </h2>
            </div>
            <p className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              8 factors
            </p>
          </div>

          <div className="mt-6 space-y-4">
            {sortedFactors.map((factor) => {
              const width = Math.min(
                100,
                Math.round((factor.risk_points / factor.max_risk_points) * 100),
              );

              return (
                <div
                  key={factor.factor_name}
                  className="rounded-xl border border-slate-200 p-4"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold text-slate-950">
                        {factor.label}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        Input: {String(factor.input_value)}
                      </p>
                    </div>
                    <p className="text-sm font-semibold text-slate-950">
                      -{factor.risk_points.toFixed(1)}
                    </p>
                  </div>

                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-slate-950"
                      style={{ width: `${width}%` }}
                    />
                  </div>

                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    {factor.explanation}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}