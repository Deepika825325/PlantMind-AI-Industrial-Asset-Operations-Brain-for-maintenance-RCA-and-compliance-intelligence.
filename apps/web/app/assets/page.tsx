import Link from "next/link";
import { apiGet } from "@/lib/api";
import { Asset } from "@/lib/types";

export const dynamic = "force-dynamic";

type AssetsResponse = {
  total: number;
  assets: Asset[];
};

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

export default async function AssetsPage() {
  const data = await apiGet<AssetsResponse>("/assets");

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Asset 360
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Industrial Asset Risk Overview
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            View risk score, health score, compliance status, connected sensors,
            work orders, and evidence sources for each monitored asset.
          </p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          {data.assets.map((asset) => (
            <div
              key={asset.asset_id}
              className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-semibold">{asset.asset_id}</h2>

                  <p className="mt-1 text-sm text-slate-400">
                    {asset.asset_name}
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    {asset.asset_type}
                  </p>
                </div>

                <span
                  className={`rounded-full border px-3 py-1 text-xs font-medium ${getRiskBadgeClass(
                    asset.risk_level
                  )}`}
                >
                  {asset.risk_level} Risk
                </span>
              </div>

              <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="rounded-xl bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Risk Score
                  </p>

                  <p className="mt-2 text-3xl font-semibold">
                    {asset.risk_score}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Health Score
                  </p>

                  <p className="mt-2 text-3xl font-semibold">
                    {asset.health_score}
                  </p>
                </div>
              </div>

              <div className="mt-5">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Health</span>
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

              <p className="mt-5 text-sm leading-6 text-slate-300">
                {asset.critical_story}
              </p>

              <div className="mt-5 space-y-3 text-sm">
                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-500">Sensor Status</span>
                  <span>{asset.sensor_status}</span>
                </div>

                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-500">Compliance</span>
                  <span>{asset.compliance_status}</span>
                </div>

                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-500">Compliance Gaps</span>
                  <span>{asset.total_compliance_gaps}</span>
                </div>

                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-500">Open/Delayed WOs</span>
                  <span>{asset.open_or_delayed_work_orders.length}</span>
                </div>
              </div>

              <div className="mt-5">
                <p className="text-sm font-medium text-slate-300">
                  Connected Sensors
                </p>

                <div className="mt-3 flex flex-wrap gap-2">
                  {asset.connected_sensors.map((sensor) => (
                    <span
                      key={sensor}
                      className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300"
                    >
                      {sensor}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-5">
                <p className="text-sm font-medium text-slate-300">
                  Source Documents
                </p>

                <div className="mt-3 flex flex-wrap gap-2">
                  {asset.source_documents.map((doc) => (
                    <span
                      key={doc}
                      className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300"
                    >
                      {doc}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  href={`/assets/${asset.asset_id}`}
                  className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
                >
                  View Asset 360
                </Link>

                <Link
                  href={`/ask?asset=${asset.asset_id}`}
                  className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-400 hover:text-white"
                >
                  Ask PlantMind
                </Link>

                <Link
                  href={`/compliance?asset=${asset.asset_id}`}
                  className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-400 hover:text-white"
                >
                  Compliance
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
