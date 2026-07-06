import type {
  ComplianceAssetSummary,
} from "@/lib/types";

type AssetAuditSummaryProps = {
  assets: ComplianceAssetSummary[];
  selectedAssetId: string;
  onSelect: (assetId: string) => void;
};

function getScoreClass(score: number) {
  if (score >= 85) {
    return "text-emerald-300";
  }

  if (score >= 65) {
    return "text-cyan-300";
  }

  if (score >= 40) {
    return "text-amber-300";
  }

  return "text-red-300";
}

function getScoreLabel(score: number) {
  if (score >= 85) {
    return "Audit Ready";
  }

  if (score >= 65) {
    return "Needs Attention";
  }

  if (score >= 40) {
    return "High Audit Risk";
  }

  return "Not Audit Ready";
}

export default function AssetAuditSummary({
  assets,
  selectedAssetId,
  onSelect,
}: AssetAuditSummaryProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">
          Asset Audit Readiness
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Select an asset to inspect its complete audit package.
        </p>
      </div>

      <div className="mt-6 space-y-4">
        {assets.map((asset) => {
          const selected =
            selectedAssetId === asset.asset_id;

          return (
            <button
              key={asset.asset_id}
              type="button"
              onClick={() => onSelect(asset.asset_id)}
              className={`w-full rounded-2xl border p-5 text-left transition ${
                selected
                  ? "border-cyan-500 bg-cyan-500/5"
                  : "border-slate-800 bg-slate-950 hover:border-slate-700"
              }`}
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-lg font-semibold text-slate-100">
                      {asset.asset_id}
                    </h3>

                    {selected && (
                      <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-300">
                        Selected
                      </span>
                    )}
                  </div>

                  <p className="mt-1 text-sm text-slate-400">
                    {asset.asset_name || "Industrial asset"}
                  </p>

                  <p
                    className={`mt-3 text-sm font-medium ${getScoreClass(
                      asset.audit_readiness_score
                    )}`}
                  >
                    {getScoreLabel(
                      asset.audit_readiness_score
                    )}
                  </p>
                </div>

                <div className="text-left sm:text-right">
                  <p
                    className={`text-3xl font-semibold ${getScoreClass(
                      asset.audit_readiness_score
                    )}`}
                  >
                    {asset.audit_readiness_score}
                  </p>

                  <p className="text-xs text-slate-500">
                    out of 100
                  </p>
                </div>
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <div className="rounded-xl bg-slate-900 p-3">
                  <p className="text-xs text-slate-500">
                    Open gaps
                  </p>

                  <p className="mt-1 font-semibold text-red-300">
                    {asset.open_gaps}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-900 p-3">
                  <p className="text-xs text-slate-500">
                    Passed
                  </p>

                  <p className="mt-1 font-semibold text-emerald-300">
                    {asset.passed_rules}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-900 p-3">
                  <p className="text-xs text-slate-500">
                    Failed
                  </p>

                  <p className="mt-1 font-semibold text-orange-300">
                    {asset.failed_rules}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-900 p-3">
                  <p className="text-xs text-slate-500">
                    Critical
                  </p>

                  <p className="mt-1 font-semibold text-red-300">
                    {asset.critical_gaps}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}