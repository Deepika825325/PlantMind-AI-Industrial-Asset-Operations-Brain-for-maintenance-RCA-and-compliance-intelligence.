import { apiGet } from "@/lib/api";
import { DashboardOverview } from "@/lib/types";

function getRiskBadgeClass(riskLevel: string) {
  if (riskLevel === "High") {
    return "bg-red-100 text-red-700 border-red-200";
  }

  if (riskLevel === "Medium") {
    return "bg-amber-100 text-amber-700 border-amber-200";
  }

  return "bg-emerald-100 text-emerald-700 border-emerald-200";
}

function getHealthBarClass(healthScore: number) {
  if (healthScore < 40) {
    return "bg-red-500";
  }

  if (healthScore < 70) {
    return "bg-amber-500";
  }

  return "bg-emerald-500";
}

export default async function HomePage() {
  const data = await apiGet<DashboardOverview>("/dashboard/overview");

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="border-b border-slate-800 bg-slate-950">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            PlantMind AI
          </p>

          <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <h1 className="text-4xl font-semibold tracking-tight">
                Industrial Asset Intelligence Dashboard
              </h1>

              <p className="mt-3 max-w-3xl text-slate-400">
                Maintenance, RCA, compliance, document intelligence, and asset
                knowledge graph demo for industrial operations.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 px-5 py-4">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Demo Story
              </p>

              <p className="mt-2 max-w-md text-sm text-slate-300">
                {data.summary.demo_story}
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-8">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Total Assets</p>
            <p className="mt-3 text-3xl font-semibold">
              {data.summary.total_assets}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">High Risk Assets</p>
            <p className="mt-3 text-3xl font-semibold text-red-400">
              {data.summary.high_risk_assets.length}
            </p>
            <p className="mt-2 text-sm text-slate-500">
              {data.summary.high_risk_assets.join(", ")}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Compliance Gaps</p>
            <p className="mt-3 text-3xl font-semibold text-amber-400">
              {data.summary.total_compliance_gaps}
            </p>
            <p className="mt-2 text-sm text-slate-500">
              High severity: {data.summary.high_severity_gaps.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Knowledge Graph</p>
            <p className="mt-3 text-3xl font-semibold text-cyan-400">
              {data.summary.knowledge_graph_nodes}
            </p>
            <p className="mt-2 text-sm text-slate-500">
              {data.summary.knowledge_graph_edges} relationships
            </p>
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Asset Health</h2>
              <span className="text-sm text-slate-500">
                {data.assets.length} assets monitored
              </span>
            </div>

            <div className="mt-6 space-y-5">
              {data.assets.map((asset) => (
                <div
                  key={asset.asset_id}
                  className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                >
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold">
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

                      <p className="mt-1 text-sm text-slate-400">
                        {asset.asset_name} · {asset.asset_type}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-sm text-slate-500">Risk Score</p>
                      <p className="text-2xl font-semibold">
                        {asset.risk_score}
                      </p>
                    </div>
                  </div>

                  <div className="mt-5">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Health Score</span>
                      <span>{asset.health_score}/100</span>
                    </div>

                    <div className="mt-2 h-2 rounded-full bg-slate-800">
                      <div
                        className={`h-2 rounded-full ${getHealthBarClass(
                          asset.health_score
                        )}`}
                        style={{ width: `${asset.health_score}%` }}
                      />
                    </div>
                  </div>

                  <p className="mt-4 text-sm leading-6 text-slate-300">
                    {asset.critical_story}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-2 text-xs">
                    <span className="rounded-full bg-slate-800 px-3 py-1 text-slate-300">
                      Sensor: {asset.sensor_status}
                    </span>
                    <span className="rounded-full bg-slate-800 px-3 py-1 text-slate-300">
                      Compliance: {asset.compliance_status}
                    </span>
                    <span className="rounded-full bg-slate-800 px-3 py-1 text-slate-300">
                      Gaps: {asset.total_compliance_gaps}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">Top Maintenance Events</h2>

            <div className="mt-6 space-y-4">
              {data.top_maintenance_events.map((event) => (
                <div
                  key={event.event_id}
                  className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium">{event.event_id}</p>
                    <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                      {event.priority}
                    </span>
                  </div>

                  <p className="mt-2 text-sm text-slate-400">
                    {event.event_type}
                  </p>

                  <p className="mt-2 text-sm leading-5 text-slate-300">
                    {event.description}
                  </p>

                  <div className="mt-3 flex justify-between text-xs text-slate-500">
                    <span>{event.asset_id}</span>
                    <span>Due: {event.due_date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}