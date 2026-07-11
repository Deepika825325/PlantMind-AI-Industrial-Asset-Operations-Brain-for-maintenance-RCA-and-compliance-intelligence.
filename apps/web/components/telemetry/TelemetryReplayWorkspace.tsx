"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  apiGet,
  apiPost,
} from "@/lib/api";

type SimulationScenario =
  | "normal_operation"
  | "bearing_degradation"
  | "shaft_misalignment"
  | "cavitation"
  | "sensor_failure"
  | "maintenance_recovery";

type SimulationStatus =
  | "created"
  | "running"
  | "paused"
  | "completed";

type SimulationRecord = {
  sequence: number;
  timestamp: string;
  asset_id: string;
  vibration_mm_s: number;
  bearing_temperature_deg_c: number;
  motor_current_a: number;
  rpm: number;
  health_score: number;
  anomaly_score: number;
  data_quality: string;
  scenario: SimulationScenario;
};

type SimulationResponse = {
  simulation_id: string;
  mode: string;
  source: string;
  live_plant_connected: boolean;
  scenario: SimulationScenario;
  asset_id: string;
  status: SimulationStatus;
  speed_multiplier: number;
  cursor: number;
  total_records: number;
  emitted_count: number;
  latest_record: SimulationRecord | null;
  emitted_records: SimulationRecord[];
};

type MetricKey =
  | "vibration_mm_s"
  | "bearing_temperature_deg_c"
  | "motor_current_a"
  | "health_score"
  | "anomaly_score";

type MetricDefinition = {
  key: MetricKey;
  label: string;
  unit: string;
  min: number;
  max: number;
};

type TelemetryReplayWorkspaceProps = {
  title?: string;
  description?: string;
  defaultAssetId?: string;
  compact?: boolean;
};

const scenarioOptions: {
  value: SimulationScenario;
  label: string;
}[] = [
  {
    value: "normal_operation",
    label: "Normal operation",
  },
  {
    value: "bearing_degradation",
    label: "Bearing degradation",
  },
  {
    value: "shaft_misalignment",
    label: "Shaft misalignment",
  },
  {
    value: "cavitation",
    label: "Cavitation",
  },
  {
    value: "sensor_failure",
    label: "Sensor failure",
  },
  {
    value: "maintenance_recovery",
    label: "Maintenance recovery",
  },
];

const metricDefinitions: MetricDefinition[] = [
  {
    key: "vibration_mm_s",
    label: "Vibration",
    unit: "mm/s",
    min: 0,
    max: 10,
  },
  {
    key: "bearing_temperature_deg_c",
    label: "Bearing temperature",
    unit: "deg C",
    min: 40,
    max: 100,
  },
  {
    key: "motor_current_a",
    label: "Motor current",
    unit: "A",
    min: 10,
    max: 30,
  },
  {
    key: "health_score",
    label: "Health-score trend",
    unit: "%",
    min: 0,
    max: 100,
  },
  {
    key: "anomaly_score",
    label: "Anomaly-score trend",
    unit: "",
    min: 0,
    max: 1,
  },
];

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }

  return "Telemetry replay action failed.";
}

function formatScenario(value: SimulationScenario) {
  return scenarioOptions.find(
    (scenario) => scenario.value === value
  )?.label ?? value;
}

function formatTimestamp(value: string | null) {
  if (!value) {
    return "No replay timestamp yet";
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString();
}

function formatValue(
  value: number,
  metric: MetricDefinition
) {
  if (metric.key === "anomaly_score") {
    return value.toFixed(3);
  }

  if (metric.key === "health_score") {
    return value.toFixed(1);
  }

  return value.toFixed(2);
}

function clamp(
  value: number,
  min: number,
  max: number
) {
  return Math.min(
    Math.max(value, min),
    max
  );
}

function getMetricValue(
  record: SimulationRecord,
  metric: MetricDefinition
) {
  return record[metric.key];
}

function createHealthyBaselineRecord(
  assetId: string,
  scenario: SimulationScenario
): SimulationRecord {
  return {
    sequence: 0,
    timestamp: "2026-07-10T09:00:00+00:00",
    asset_id: assetId,
    vibration_mm_s: 2.2,
    bearing_temperature_deg_c: 63,
    motor_current_a: 18.5,
    rpm: 1480,
    health_score: 96,
    anomaly_score: 0.03,
    data_quality: "good",
    scenario,
  };
}

function Sparkline({
  records,
  metric,
}: {
  records: SimulationRecord[];
  metric: MetricDefinition;
}) {
  const points = records
    .map((record, index) => {
      const x =
        records.length === 1
          ? 0
          : (index / (records.length - 1)) * 100;

      const rawValue = getMetricValue(
        record,
        metric
      );

      const normalized = clamp(
        (rawValue - metric.min) /
          (metric.max - metric.min),
        0,
        1
      );

      const y = 80 - normalized * 70;

      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  return (
    <svg
      viewBox="0 0 100 90"
      className="mt-4 h-28 w-full overflow-visible"
      role="img"
      aria-label={`${metric.label} replay chart`}
    >
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-cyan-300"
      />

      <line
        x1="0"
        y1="80"
        x2="100"
        y2="80"
        stroke="currentColor"
        strokeWidth="1"
        className="text-slate-700"
      />
    </svg>
  );
}

function StatusBadge({
  status,
}: {
  status: SimulationStatus;
}) {
  const className =
    status === "running"
      ? "border-emerald-500/40 bg-emerald-950/60 text-emerald-300"
      : status === "paused"
        ? "border-amber-500/40 bg-amber-950/60 text-amber-300"
        : status === "completed"
          ? "border-blue-500/40 bg-blue-950/60 text-blue-300"
          : "border-slate-700 bg-slate-950 text-slate-300";

  return (
    <span
      className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${className}`}
    >
      {status}
    </span>
  );
}

export default function TelemetryReplayWorkspace({
  title = "Telemetry replay console",
  description = "Replay deterministic timestamped telemetry records without connecting to a live plant.",
  defaultAssetId = "P-101",
  compact = false,
}: TelemetryReplayWorkspaceProps) {
  const [assetId, setAssetId] = useState(
    defaultAssetId
  );
  const [scenario, setScenario] =
    useState<SimulationScenario>(
      "normal_operation"
    );
  const [recordCount, setRecordCount] = useState(90);
  const [speedMultiplier, setSpeedMultiplier] =
    useState(1);
  const [simulation, setSimulation] =
    useState<SimulationResponse | null>(null);
  const [loadingAction, setLoadingAction] =
    useState<string | null>(null);
  const [error, setError] = useState("");

  const baselineRecord = useMemo(
    () =>
      createHealthyBaselineRecord(
        assetId,
        scenario
      ),
    [assetId, scenario]
  );

  const displayRecords =
    simulation?.emitted_records &&
    simulation.emitted_records.length > 0
      ? simulation.emitted_records
      : [baselineRecord];

  const latestRecord =
    simulation?.latest_record ?? baselineRecord;

  const refreshSimulation = useCallback(async () => {
    if (!simulation) {
      return;
    }

    try {
      const result =
        await apiGet<SimulationResponse>(
          `/simulations/${encodeURIComponent(
            simulation.simulation_id
          )}`
        );

      setSimulation(result);
      setError("");
    } catch (refreshError) {
      setError(getErrorMessage(refreshError));
    }
  }, [simulation]);

  useEffect(() => {
    if (simulation?.status !== "running") {
      return undefined;
    }

    const intervalId = window.setInterval(
      () => {
        void refreshSimulation();
      },
      1000
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, [
    refreshSimulation,
    simulation?.status,
  ]);

  async function createSimulation() {
    setLoadingAction("create");
    setError("");

    try {
      const result = await apiPost<
        {
          scenario: SimulationScenario;
          asset_id: string;
          record_count: number;
        },
        SimulationResponse
      >(
        "/simulations",
        {
          scenario,
          asset_id: assetId.trim() || "P-101",
          record_count: recordCount,
        }
      );

      setSimulation(result);
      setSpeedMultiplier(result.speed_multiplier);
    } catch (createError) {
      setError(getErrorMessage(createError));
    } finally {
      setLoadingAction(null);
    }
  }

  async function postSimulationAction(
    action: "start" | "pause" | "resume" | "reset"
  ) {
    if (!simulation) {
      return;
    }

    setLoadingAction(action);
    setError("");

    try {
      const result = await apiPost<
        Record<string, never>,
        SimulationResponse
      >(
        `/simulations/${encodeURIComponent(
          simulation.simulation_id
        )}/${action}`,
        {}
      );

      setSimulation(result);

      if (action === "reset") {
        setSpeedMultiplier(1);
      }
    } catch (actionError) {
      setError(getErrorMessage(actionError));
    } finally {
      setLoadingAction(null);
    }
  }

  async function applySpeed() {
    if (!simulation) {
      return;
    }

    setLoadingAction("speed");
    setError("");

    try {
      const result = await apiPost<
        {
          speed_multiplier: number;
        },
        SimulationResponse
      >(
        `/simulations/${encodeURIComponent(
          simulation.simulation_id
        )}/speed`,
        {
          speed_multiplier: speedMultiplier,
        }
      );

      setSimulation(result);
    } catch (speedError) {
      setError(getErrorMessage(speedError));
    } finally {
      setLoadingAction(null);
    }
  }

  const content = (
    <section
      className={
        compact
          ? "mx-auto max-w-7xl px-0 py-0"
          : "mx-auto max-w-7xl px-6 py-10"
      }
    >
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
              Day 18 Telemetry Frontend
            </p>

            <h1 className="mt-4 text-4xl font-semibold tracking-tight">
              {title}
            </h1>

            <p className="mt-3 max-w-3xl text-slate-400">
              {description}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
            <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
              Replay state
            </p>

            <div className="mt-3">
              <StatusBadge
                status={simulation?.status ?? "created"}
              />
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-1">
            <h2 className="text-lg font-semibold">
              Simulation controls
            </h2>

            <label className="mt-5 block text-sm text-slate-400">
              Asset ID
            </label>

            <input
              value={assetId}
              onChange={(event) =>
                setAssetId(event.target.value)
              }
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <label className="mt-5 block text-sm text-slate-400">
              Scenario
            </label>

            <select
              value={scenario}
              onChange={(event) =>
                setScenario(
                  event.target.value as SimulationScenario
                )
              }
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            >
              {scenarioOptions.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              ))}
            </select>

            <label className="mt-5 block text-sm text-slate-400">
              Records
            </label>

            <input
              type="number"
              min={10}
              max={600}
              value={recordCount}
              onChange={(event) =>
                setRecordCount(
                  clamp(
                    Number(event.target.value),
                    10,
                    600
                  )
                )
              }
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <label className="mt-5 block text-sm text-slate-400">
              Replay speed
            </label>

            <input
              type="number"
              min={0.1}
              max={20}
              step={0.5}
              value={speedMultiplier}
              onChange={(event) =>
                setSpeedMultiplier(
                  clamp(
                    Number(event.target.value),
                    0.1,
                    20
                  )
                )
              }
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <div className="mt-6 grid gap-3">
              <button
                onClick={createSimulation}
                disabled={loadingAction !== null}
                className="rounded-xl bg-cyan-400 px-4 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loadingAction === "create"
                  ? "Creating..."
                  : "Create Replay"}
              </button>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() =>
                    postSimulationAction("start")
                  }
                  disabled={
                    !simulation ||
                    loadingAction !== null ||
                    simulation.status === "running"
                  }
                  className="rounded-xl border border-slate-700 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Start
                </button>

                <button
                  onClick={() =>
                    postSimulationAction("pause")
                  }
                  disabled={
                    !simulation ||
                    loadingAction !== null ||
                    simulation.status !== "running"
                  }
                  className="rounded-xl border border-slate-700 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-amber-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Pause
                </button>

                <button
                  onClick={() =>
                    postSimulationAction("resume")
                  }
                  disabled={
                    !simulation ||
                    loadingAction !== null ||
                    simulation.status !== "paused"
                  }
                  className="rounded-xl border border-slate-700 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Resume
                </button>

                <button
                  onClick={() =>
                    postSimulationAction("reset")
                  }
                  disabled={
                    !simulation ||
                    loadingAction !== null
                  }
                  className="rounded-xl border border-slate-700 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Reset
                </button>
              </div>

              <button
                onClick={applySpeed}
                disabled={
                  !simulation ||
                  loadingAction !== null
                }
                className="rounded-xl border border-cyan-700 px-4 py-3 text-sm font-semibold text-cyan-300 transition hover:border-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Apply Speed
              </button>
            </div>

            {error && (
              <p className="mt-5 rounded-xl border border-red-800 bg-red-950/60 p-3 text-sm text-red-300">
                {error}
              </p>
            )}
          </div>

          <div className="space-y-6 lg:col-span-3">
            <div className="grid gap-4 md:grid-cols-4">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Latest sensor timestamp
                </p>
                <p className="mt-2 text-sm font-semibold text-slate-100">
                  {formatTimestamp(latestRecord.timestamp)}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Data quality
                </p>
                <p className="mt-2 text-xl font-semibold text-emerald-300">
                  {latestRecord.data_quality}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Emitted records
                </p>
                <p className="mt-2 text-xl font-semibold text-cyan-300">
                  {simulation?.emitted_count ?? 0}
                  <span className="text-sm text-slate-500">
                    {" "}
                    / {simulation?.total_records ?? recordCount}
                  </span>
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Scenario
                </p>
                <p className="mt-2 text-sm font-semibold text-slate-100">
                  {formatScenario(
                    simulation?.scenario ?? scenario
                  )}
                </p>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-lg font-semibold">
                Replay safety labels
              </h2>

              <div className="mt-4 grid gap-4 md:grid-cols-3">
                <div className="rounded-xl bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                    Mode
                  </p>
                  <p className="mt-2 font-semibold text-cyan-300">
                    {simulation?.mode ?? "Historical replay"}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                    Source
                  </p>
                  <p className="mt-2 font-semibold text-cyan-300">
                    {simulation?.source ??
                      "Generated experimental dataset"}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                    Live plant
                  </p>
                  <p className="mt-2 font-semibold text-emerald-300">
                    {simulation?.live_plant_connected
                      ? "Connected"
                      : "Not connected to a live plant"}
                  </p>
                </div>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              {metricDefinitions.map((metric) => {
                const latestValue = getMetricValue(
                  latestRecord,
                  metric
                );

                return (
                  <div
                    key={metric.key}
                    className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-sm text-slate-400">
                          {metric.label}
                        </p>
                        <p className="mt-2 text-3xl font-semibold">
                          {formatValue(
                            latestValue,
                            metric
                          )}
                          {metric.unit && (
                            <span className="ml-2 text-sm text-slate-500">
                              {metric.unit}
                            </span>
                          )}
                        </p>
                      </div>

                      <span className="rounded-full bg-slate-950 px-3 py-1 text-xs text-slate-400">
                        polling
                      </span>
                    </div>

                    <Sparkline
                      records={displayRecords}
                      metric={metric}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
    </section>
  );

  if (compact) {
    return content;
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      {content}
    </main>
  );
}
