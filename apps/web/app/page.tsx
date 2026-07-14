import Link from "next/link";

import OperationsSummaryPanel from "@/components/dashboard/OperationsSummaryPanel";
import EmptyState from "@/components/system/EmptyState";

import {
  apiGet,
} from "@/lib/api";

import type {
  DashboardOverview,
  OperationsSummary,
} from "@/lib/types";

export const dynamic = "force-dynamic";

function getRiskBadgeClass(
  riskLevel: string
): string {
  const normalizedRisk =
    riskLevel.trim().toLowerCase();

  if (
    normalizedRisk === "critical" ||
    normalizedRisk === "high"
  ) {
    return (
      "border-red-800 bg-red-950/50 " +
      "text-red-300"
    );
  }

  if (
    normalizedRisk === "medium"
  ) {
    return (
      "border-amber-800 bg-amber-950/50 " +
      "text-amber-300"
    );
  }

  return (
    "border-emerald-800 bg-emerald-950/50 " +
    "text-emerald-300"
  );
}


function getHealthBarClass(
  healthScore: number
): string {
  if (healthScore < 40) {
    return "bg-red-500";
  }

  if (healthScore < 70) {
    return "bg-amber-500";
  }

  return "bg-emerald-500";
}


export default async function HomePage() {
  const [
    data,
    operationsSummary,
  ] = await Promise.all([
    apiGet<DashboardOverview>(
      "/dashboard/overview"
    ),
    apiGet<OperationsSummary>(
      "/dashboard/operations-summary"
    ),
  ]);

  return (
    <main className="min-h-screen min-w-0 bg-slate-950 text-slate-100">
      <section className="border-b border-slate-800 bg-slate-950">
        <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6">
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            PlantMind AI
          </p>

          <div className="mt-4 flex min-w-0 flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="min-w-0">
              <h1 className="break-words text-3xl font-semibold tracking-tight sm:text-4xl">
                Industrial Asset Intelligence
                Dashboard
              </h1>

              <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400 sm:text-base">
                Maintenance, RCA, compliance,
                document intelligence and asset
                knowledge for industrial operations.
              </p>
            </div>

            <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 px-5 py-4 lg:max-w-md">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Demo Story
              </p>

              <p className="mt-2 break-words text-sm leading-6 text-slate-300">
                {data.summary.demo_story}
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6">
        <div className="grid min-w-0 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Total Assets
            </p>

            <p className="mt-3 text-3xl font-semibold text-slate-100">
              {data.summary.total_assets}
            </p>

            <Link
              href="/assets"
              className="mt-3 inline-flex text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              Open asset registry
            </Link>
          </div>

          <div className="rounded-2xl border border-red-900/70 bg-red-950/20 p-5">
            <p className="text-sm text-slate-400">
              High-Risk Assets
            </p>

            <p className="mt-3 text-3xl font-semibold text-red-400">
              {
                data.summary
                  .high_risk_assets.length
              }
            </p>

            <p className="mt-2 break-words text-sm text-slate-500">
              {data.summary.high_risk_assets
                .length
                ? data.summary.high_risk_assets.join(
                    ", "
                  )
                : "No high-risk assets"}
            </p>
          </div>

          <div className="rounded-2xl border border-amber-900/70 bg-amber-950/20 p-5">
            <p className="text-sm text-slate-400">
              Compliance Gaps
            </p>

            <p className="mt-3 text-3xl font-semibold text-amber-400">
              {
                data.summary
                  .total_compliance_gaps
              }
            </p>

            <p className="mt-2 text-sm text-slate-500">
              High severity:{" "}
              {
                data.summary
                  .high_severity_gaps.length
              }
            </p>
          </div>

          <div className="rounded-2xl border border-cyan-900/70 bg-cyan-950/20 p-5">
            <p className="text-sm text-slate-400">
              Knowledge Graph
            </p>

            <p className="mt-3 text-3xl font-semibold text-cyan-400">
              {
                data.summary
                  .knowledge_graph_nodes
              }
            </p>

            <p className="mt-2 text-sm text-slate-500">
              {
                data.summary
                  .knowledge_graph_edges
              }{" "}
              relationships
            </p>
          </div>
        </div>

        <OperationsSummaryPanel
          data={operationsSummary}
        />

        <div className="mt-8 grid min-w-0 gap-6 lg:grid-cols-3">
          <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
            <div className="flex min-w-0 flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <h2 className="text-xl font-semibold">
                  Asset Health
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Current risk and condition
                  summary
                </p>
              </div>

              <span className="shrink-0 text-sm text-slate-500">
                {data.assets.length} assets
                monitored
              </span>
            </div>

            {data.assets.length ? (
              <div className="mt-6 space-y-5">
                {data.assets.map(
                  (
                    asset
                  ) => (
                    <Link
                      key={asset.asset_id}
                      href={`/assets/${encodeURIComponent(
                        asset.asset_id
                      )}`}
                      className="block min-w-0 rounded-2xl border border-slate-800 bg-slate-950 p-5 transition hover:border-slate-700 hover:bg-slate-900"
                    >
                      <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div className="min-w-0">
                          <div className="flex min-w-0 flex-wrap items-center gap-3">
                            <h3 className="break-words text-lg font-semibold">
                              {asset.asset_id}
                            </h3>

                            <span
                              className={`rounded-full border px-3 py-1 text-xs font-medium ${getRiskBadgeClass(
                                asset.risk_level
                              )}`}
                            >
                              {asset.risk_level} Risk
                            </span>
                          </div>

                          <p className="mt-1 break-words text-sm text-slate-400">
                            {asset.asset_name} •{" "}
                            {asset.asset_type}
                          </p>
                        </div>

                        <div className="shrink-0 text-left sm:text-right">
                          <p className="text-sm text-slate-500">
                            Risk Score
                          </p>

                          <p className="text-2xl font-semibold">
                            {asset.risk_score}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5">
                        <div className="flex justify-between gap-4 text-sm">
                          <span className="text-slate-400">
                            Health Score
                          </span>

                          <span>
                            {asset.health_score}/100
                          </span>
                        </div>

                        <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800">
                          <div
                            className={`h-2 rounded-full ${getHealthBarClass(
                              asset.health_score
                            )}`}
                            style={{
                              width: `${Math.max(
                                0,
                                Math.min(
                                  asset.health_score,
                                  100
                                )
                              )}%`,
                            }}
                          />
                        </div>
                      </div>

                      <p className="mt-4 break-words text-sm leading-6 text-slate-300">
                        {asset.critical_story}
                      </p>

                      <div className="mt-4 flex flex-wrap gap-2 text-xs">
                        <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-slate-300">
                          Sensor:{" "}
                          {asset.sensor_status}
                        </span>

                        <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-slate-300">
                          Compliance:{" "}
                          {
                            asset.compliance_status
                          }
                        </span>

                        <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-slate-300">
                          Gaps:{" "}
                          {
                            asset.total_compliance_gaps
                          }
                        </span>
                      </div>
                    </Link>
                  )
                )}
              </div>
            ) : (
              <div className="mt-6">
                <EmptyState
                  title="No asset data"
                  message="PlantMind did not receive any asset-health records from the backend."
                  actionLabel="Open asset registry"
                  actionHref="/assets"
                />
              </div>
            )}
          </div>

          <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-semibold">
                Maintenance Events
              </h2>

              <Link
                href="/maintenance"
                className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
              >
                View all
              </Link>
            </div>

            {data.top_maintenance_events
              .length ? (
              <div className="mt-6 space-y-4">
                {data.top_maintenance_events.map(
                  (
                    event
                  ) => (
                    <div
                      key={event.event_id}
                      className="min-w-0 rounded-2xl border border-slate-800 bg-slate-950 p-4"
                    >
                      <div className="flex min-w-0 items-center justify-between gap-3">
                        <p className="truncate font-medium">
                          {event.event_id}
                        </p>

                        <span
                          className={`shrink-0 rounded-full border px-3 py-1 text-xs ${getRiskBadgeClass(
                            event.priority
                          )}`}
                        >
                          {event.priority}
                        </span>
                      </div>

                      <p className="mt-2 break-words text-sm text-slate-400">
                        {event.event_type}
                      </p>

                      <p className="mt-2 break-words text-sm leading-5 text-slate-300">
                        {event.description}
                      </p>

                      <div className="mt-3 flex flex-col gap-1 text-xs text-slate-500 sm:flex-row sm:justify-between">
                        <span>
                          {event.asset_id}
                        </span>

                        <span>
                          Due: {event.due_date}
                        </span>
                      </div>
                    </div>
                  )
                )}
              </div>
            ) : (
              <div className="mt-6">
                <EmptyState
                  title="No maintenance events"
                  message="No maintenance events are currently available."
                  actionLabel="Open maintenance"
                  actionHref="/maintenance"
                />
              </div>
            )}
          </div>
        </div>
      </section>

      {/* PlantMind Nexus final demo CTA */}
      <section className="mx-auto mt-10 max-w-7xl px-6 pb-12">
        <div className="rounded-3xl border border-cyan-900/70 bg-cyan-950/20 p-6 shadow-2xl shadow-cyan-950/20 md:p-8">
          <div className="grid gap-6 lg:grid-cols-[1.4fr_0.6fr] lg:items-center">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-300">
                Final Judge Demo
              </p>

              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-slate-100">
                P-101 Closed-Loop Industrial Maintenance Intelligence
              </h2>

              <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-300">
                Walk through telemetry degradation, anomaly explanation,
                failure hypothesis ranking, SOP/RAG evidence, governed work
                orders, recovery verification, and audit-ready compliance in
                one guided demo.
              </p>

              <div className="mt-5 flex flex-wrap gap-2 text-xs text-slate-300">
                <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1">
                  Anomaly explanation
                </span>
                <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1">
                  RCA hypothesis ranking
                </span>
                <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1">
                  SOP evidence trail
                </span>
                <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1">
                  Judge metrics
                </span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
              <p className="text-sm text-slate-500">
                Recommended first page during demo
              </p>

              <Link
                href="/demo/p101-closed-loop"
                className="mt-4 inline-flex w-full justify-center rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
              >
                Open P-101 Demo
              </Link>

              <p className="mt-4 text-xs leading-5 text-slate-500">
                Use this page as the main hackathon walkthrough before showing
                detailed modules like RCA, work orders, compliance, and model
                registry.
              </p>
            </div>
          </div>
        </div>
      </section>

</main>
  );
}
