"use client";

import { useMemo, useState } from "react";

type ModelStage =
  | "Development"
  | "Candidate"
  | "Validated"
  | "Staging"
  | "Production"
  | "Archived";

type ApprovalStatus = "pending" | "approved" | "rejected" | "not_required";

type SelectionSource = "environment_config" | "registry_stage" | "fallback";

type RegisteredModelVersion = {
  model_name: string;
  model_version: string;
  dataset_version: string;
  feature_version: string;
  parameters: Record<string, string | number | boolean>;
  metrics: Record<string, number>;
  artifact_location: string;
  deployment_stage: ModelStage;
  approval: ApprovalStatus;
  approved_by?: string | null;
  rollback_target?: string | null;
  created_at: string;
  updated_at: string;
  description?: string | null;
  tags: Record<string, string>;
};

type ProductionModelSelection = {
  model_name: string;
  selected_version: string;
  selection_source: SelectionSource;
  configuration_key?: string | null;
  rollback_target?: string | null;
  model: RegisteredModelVersion;
};

type ModelRegistryOverview = {
  stages: ModelStage[];
  registered_model_count: number;
  model_version_count: number;
  production_model_count: number;
  model_names: string[];
  audit_event_count: number;
};

type RegistryAuditEvent = {
  event_id: string;
  event_type:
    | "model_registered"
    | "stage_transitioned"
    | "production_restored"
    | "production_selected";
  model_name: string;
  model_version: string;
  from_stage?: ModelStage | null;
  to_stage?: ModelStage | null;
  actor: string;
  reason: string;
  created_at: string;
};

function label(value: string): string {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function fallbackOverview(): ModelRegistryOverview {
  return {
    stages: [
      "Development",
      "Candidate",
      "Validated",
      "Staging",
      "Production",
      "Archived",
    ],
    registered_model_count: 1,
    model_version_count: 2,
    production_model_count: 1,
    model_names: ["plantmind-p101-anomaly-detector"],
    audit_event_count: 1,
  };
}

function fallbackProduction(): ProductionModelSelection {
  return {
    model_name: "plantmind-p101-anomaly-detector",
    selected_version: "v0.3.11",
    selection_source: "registry_stage",
    configuration_key: null,
    rollback_target: "v0.3.10",
    model: {
      model_name: "plantmind-p101-anomaly-detector",
      model_version: "v0.3.11",
      dataset_version: "telemetry-demo-v1",
      feature_version: "p101-multivariate-features-v1",
      parameters: {
        window_size: 12,
        contamination: 0.08,
        feature_count: 5,
        random_state: 42,
      },
      metrics: {
        precision: 0.94,
        recall: 0.91,
        f1_score: 0.925,
        roc_auc: 0.96,
        false_positive_rate: 0.04,
        model_latency_ms: 18,
      },
      artifact_location:
        "artifacts/models/p101-anomaly-detector/v0.3.11/model.pkl",
      deployment_stage: "Production",
      approval: "approved",
      approved_by: "maintenance_lead",
      rollback_target: "v0.3.10",
      created_at: "2026-07-10T09:00:00+00:00",
      updated_at: "2026-07-10T09:00:00+00:00",
      description:
        "P-101 multivariate anomaly detector promoted after evaluation.",
      tags: {
        asset_id: "P-101",
        model_family: "anomaly_detection",
        source_commit: "b774f59",
      },
    },
  };
}

function fallbackVersions(): RegisteredModelVersion[] {
  return [
    fallbackProduction().model,
    {
      model_name: "plantmind-p101-anomaly-detector",
      model_version: "v0.3.10",
      dataset_version: "telemetry-demo-v1",
      feature_version: "p101-multivariate-features-v1",
      parameters: {
        window_size: 8,
        contamination: 0.1,
        feature_count: 5,
        random_state: 42,
      },
      metrics: {
        precision: 0.89,
        recall: 0.87,
        f1_score: 0.88,
        roc_auc: 0.92,
        false_positive_rate: 0.07,
        model_latency_ms: 16,
      },
      artifact_location:
        "artifacts/models/p101-anomaly-detector/v0.3.10/model.pkl",
      deployment_stage: "Validated",
      approval: "approved",
      approved_by: "maintenance_lead",
      rollback_target: null,
      created_at: "2026-07-09T09:00:00+00:00",
      updated_at: "2026-07-09T09:00:00+00:00",
      description: "Previous validated anomaly detector available for rollback.",
      tags: {
        asset_id: "P-101",
        model_family: "anomaly_detection",
        source_commit: "7243b52",
      },
    },
  ];
}

function fallbackEvents(): RegistryAuditEvent[] {
  return [
    {
      event_id: "REG-P101-ANOMALY-V0311",
      event_type: "model_registered",
      model_name: "plantmind-p101-anomaly-detector",
      model_version: "v0.3.11",
      from_stage: null,
      to_stage: "Production",
      actor: "system",
      reason: "Seed production anomaly model for Day 28 registry.",
      created_at: "2026-07-10T09:00:00+00:00",
    },
  ];
}

function metricLabel(metricName: string): string {
  if (metricName === "f1_score") {
    return "F1 score";
  }

  if (metricName === "roc_auc") {
    return "ROC AUC";
  }

  if (metricName === "model_latency_ms") {
    return "Model latency";
  }

  return label(metricName);
}

function metricValue(metricName: string, value: number): string {
  if (metricName === "model_latency_ms") {
    return `${value.toFixed(1)} ms`;
  }

  return value.toFixed(3);
}

export function ModelRegistryPanel() {
  const [modelName, setModelName] = useState(
    "plantmind-p101-anomaly-detector",
  );
  const [overview, setOverview] = useState<ModelRegistryOverview>(() =>
    fallbackOverview(),
  );
  const [production, setProduction] = useState<ProductionModelSelection>(() =>
    fallbackProduction(),
  );
  const [versions, setVersions] = useState<RegisteredModelVersion[]>(() =>
    fallbackVersions(),
  );
  const [events, setEvents] = useState<RegistryAuditEvent[]>(() =>
    fallbackEvents(),
  );
  const [status, setStatus] = useState(
    "Using local model registry preview.",
  );

  const productionMetrics = useMemo(
    () => Object.entries(production.model.metrics),
    [production.model.metrics],
  );

  const productionParameters = useMemo(
    () => Object.entries(production.model.parameters),
    [production.model.parameters],
  );

  async function loadRegistry() {
    setStatus(`Loading model registry for ${modelName}...`);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

      const [overviewResponse, productionResponse, versionsResponse, eventsResponse] =
        await Promise.all([
          fetch(`${baseUrl}/mlops/model-registry/overview`, {
            headers: { Accept: "application/json" },
          }),
          fetch(
            `${baseUrl}/mlops/model-registry/production/${encodeURIComponent(modelName)}`,
            {
              headers: { Accept: "application/json" },
            },
          ),
          fetch(
            `${baseUrl}/mlops/model-registry/models/${encodeURIComponent(modelName)}/versions`,
            {
              headers: { Accept: "application/json" },
            },
          ),
          fetch(
            `${baseUrl}/mlops/model-registry/audit-events?model_name=${encodeURIComponent(modelName)}`,
            {
              headers: { Accept: "application/json" },
            },
          ),
        ]);

      if (
        !overviewResponse.ok ||
        !productionResponse.ok ||
        !versionsResponse.ok ||
        !eventsResponse.ok
      ) {
        throw new Error("One or more registry requests failed.");
      }

      setOverview((await overviewResponse.json()) as ModelRegistryOverview);
      setProduction(
        (await productionResponse.json()) as ProductionModelSelection,
      );
      setVersions((await versionsResponse.json()) as RegisteredModelVersion[]);
      setEvents((await eventsResponse.json()) as RegistryAuditEvent[]);

      setStatus(`Loaded production model for ${modelName}.`);
    } catch {
      setOverview(fallbackOverview());
      setProduction(fallbackProduction());
      setVersions(fallbackVersions());
      setEvents(fallbackEvents());
      setStatus(
        "Backend unavailable or authentication required. Showing local MLOps registry preview.",
      );
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Phase 8 · MLOps
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">
          MLflow-style model registry and experiment tracking
        </h1>
        <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-600">
          Track model name, version, dataset version, feature version,
          parameters, metrics, artifact location, deployment stage, approval,
          and rollback target for PlantMind production models.
        </p>

        <div className="mt-5 flex flex-col gap-3 lg:flex-row">
          <input
            value={modelName}
            onChange={(event) => setModelName(event.target.value)}
            className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-slate-500"
            aria-label="Model name"
          />
          <button
            type="button"
            onClick={loadRegistry}
            className="rounded-xl bg-slate-950 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-800"
          >
            Load registry
          </button>
        </div>

        <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          {status}
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Registered models
          </p>
          <p className="mt-2 text-3xl font-semibold text-slate-950">
            {overview.registered_model_count}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Model versions
          </p>
          <p className="mt-2 text-3xl font-semibold text-slate-950">
            {overview.model_version_count}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Production models
          </p>
          <p className="mt-2 text-3xl font-semibold text-slate-950">
            {overview.production_model_count}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Audit events
          </p>
          <p className="mt-2 text-3xl font-semibold text-slate-950">
            {overview.audit_event_count}
          </p>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Production selection
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            {production.selected_version}
          </h2>

          <div className="mt-6 space-y-3 text-sm text-slate-700">
            <p>
              <span className="font-semibold">Model:</span>{" "}
              {production.model_name}
            </p>
            <p>
              <span className="font-semibold">Selection source:</span>{" "}
              {label(production.selection_source)}
            </p>
            <p>
              <span className="font-semibold">Configuration key:</span>{" "}
              {production.configuration_key ?? "Registry stage"}
            </p>
            <p>
              <span className="font-semibold">Rollback target:</span>{" "}
              {production.rollback_target ?? "Not configured"}
            </p>
            <p>
              <span className="font-semibold">Artifact:</span>{" "}
              {production.model.artifact_location}
            </p>
            <p>
              <span className="font-semibold">Approval:</span>{" "}
              {label(production.model.approval)}
              {production.model.approved_by
                ? ` by ${production.model.approved_by}`
                : ""}
            </p>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {overview.stages.map((stage) => (
              <span
                key={stage}
                className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
              >
                {stage}
              </span>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Evaluation metrics
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Attached model evaluation
          </h2>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {productionMetrics.map(([metricName, value]) => (
              <div key={metricName} className="rounded-xl bg-slate-50 p-4">
                <p className="text-2xl font-semibold text-slate-950">
                  {metricValue(metricName, value)}
                </p>
                <p className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
                  {metricLabel(metricName)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Version registry
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-slate-950">
          Model lifecycle history
        </h2>

        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Stage</th>
                <th className="px-4 py-3">Dataset</th>
                <th className="px-4 py-3">Features</th>
                <th className="px-4 py-3">F1</th>
                <th className="px-4 py-3">Rollback</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {versions.map((version) => (
                <tr key={version.model_version}>
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-950">
                      {version.model_version}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {version.model_name}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {version.deployment_stage}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {version.dataset_version}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {version.feature_version}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {version.metrics.f1_score?.toFixed(3) ?? "N/A"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {version.rollback_target ?? "None"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Parameters
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Production configuration
          </h2>

          <div className="mt-6 space-y-3">
            {productionParameters.map(([parameterName, value]) => (
              <div
                key={parameterName}
                className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3 text-sm"
              >
                <span className="font-medium text-slate-700">
                  {label(parameterName)}
                </span>
                <span className="text-slate-600">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Registry audit trail
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Governance events
          </h2>

          <div className="mt-6 space-y-3">
            {events.map((event) => (
              <div
                key={event.event_id}
                className="rounded-xl border border-slate-200 p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {label(event.event_type)}
                  </span>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {event.model_version}
                  </span>
                </div>
                <p className="mt-3 font-semibold text-slate-950">
                  {event.reason}
                </p>
                <p className="mt-2 text-sm text-slate-600">
                  Actor: {event.actor}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {event.from_stage ?? "None"} → {event.to_stage ?? "None"}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}