import type {
  ComplianceOverview,
  ComplianceSeverity,
} from "@/lib/types";

type GapSeverityDistributionProps = {
  distribution: ComplianceOverview["severity_distribution"];
};

const severityConfig: Array<{
  key: ComplianceSeverity;
  label: string;
  barClass: string;
  textClass: string;
}> = [
  {
    key: "Critical",
    label: "Critical",
    barClass: "bg-red-500",
    textClass: "text-red-300",
  },
  {
    key: "High",
    label: "High",
    barClass: "bg-orange-500",
    textClass: "text-orange-300",
  },
  {
    key: "Medium",
    label: "Medium",
    barClass: "bg-amber-500",
    textClass: "text-amber-300",
  },
  {
    key: "Low",
    label: "Low",
    barClass: "bg-slate-500",
    textClass: "text-slate-300",
  },
];

export default function GapSeverityDistribution({
  distribution,
}: GapSeverityDistributionProps) {
  const total = Object.values(distribution).reduce(
    (sum, value) => sum + value,
    0
  );

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">
          Gap Severity Distribution
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Distribution of currently open compliance gaps.
        </p>
      </div>

      <div className="mt-6 space-y-5">
        {severityConfig.map((severity) => {
          const count = distribution[severity.key] || 0;
          const percentage =
            total > 0 ? Math.round((count / total) * 100) : 0;

          return (
            <div key={severity.key}>
              <div className="flex items-center justify-between gap-4">
                <p className={`text-sm font-medium ${severity.textClass}`}>
                  {severity.label}
                </p>

                <p className="text-sm text-slate-400">
                  {count} gap{count === 1 ? "" : "s"} · {percentage}%
                </p>
              </div>

              <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full rounded-full ${severity.barClass}`}
                  style={{
                    width: `${percentage}%`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-400">
            Total open gaps
          </p>

          <p className="text-2xl font-semibold text-slate-100">
            {total}
          </p>
        </div>
      </div>
    </section>
  );
}