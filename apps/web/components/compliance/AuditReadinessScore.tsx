import type {
  ComplianceScoringBreakdown,
} from "@/lib/types";

type AuditReadinessScoreProps = {
  score: number;
  breakdown: ComplianceScoringBreakdown;
};

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

function getScoreClass(score: number) {
  if (score >= 85) {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  if (score >= 65) {
    return "border-cyan-500/30 bg-cyan-500/10 text-cyan-300";
  }

  if (score >= 40) {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-red-500/30 bg-red-500/10 text-red-300";
}

export default function AuditReadinessScore({
  score,
  breakdown,
}: AuditReadinessScoreProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-slate-500">
            Audit Readiness
          </p>

          <div className="mt-4 flex flex-wrap items-end gap-4">
            <p className="text-6xl font-semibold tracking-tight text-slate-100">
              {score}
            </p>

            <p className="pb-2 text-lg text-slate-500">
              / {breakdown.maximum_score}
            </p>
          </div>

          <span
            className={`mt-5 inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${getScoreClass(
              score
            )}`}
          >
            {getScoreLabel(score)}
          </span>
        </div>

        <div className="w-full max-w-xl rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
            Score Formula
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-300">
            {breakdown.formula}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Severity Penalty
          </p>
          <p className="mt-2 text-2xl font-semibold text-red-300">
            -{breakdown.severity_penalty}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Missing Evidence
          </p>
          <p className="mt-2 text-2xl font-semibold text-amber-300">
            -{breakdown.missing_evidence_penalty}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Overdue Actions
          </p>
          <p className="mt-2 text-2xl font-semibold text-orange-300">
            -{breakdown.overdue_action_penalty}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Total Penalty
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-100">
            -{breakdown.total_penalty}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        {(["critical", "high", "medium"] as const).map(
          (severity) => (
            <div
              key={severity}
              className="rounded-xl border border-slate-800 bg-slate-950 p-4"
            >
              <div className="flex items-center justify-between gap-4">
                <p className="capitalize text-slate-300">
                  {severity} gaps
                </p>

                <span className="rounded-full bg-slate-800 px-3 py-1 text-sm text-slate-300">
                  {breakdown.gap_counts[severity]}
                </span>
              </div>

              <div className="mt-4 flex items-center justify-between text-sm">
                <span className="text-slate-500">
                  Raw penalty
                </span>
                <span className="text-slate-300">
                  {breakdown.raw_severity_penalties[severity]}
                </span>
              </div>

              <div className="mt-2 flex items-center justify-between text-sm">
                <span className="text-slate-500">
                  Applied penalty
                </span>
                <span className="font-medium text-slate-100">
                  {breakdown.applied_severity_penalties[severity]}
                </span>
              </div>

              <div className="mt-2 flex items-center justify-between text-sm">
                <span className="text-slate-500">
                  Penalty cap
                </span>
                <span className="text-slate-300">
                  {breakdown.penalty_caps[severity]}
                </span>
              </div>
            </div>
          )
        )}
      </div>
    </section>
  );
}