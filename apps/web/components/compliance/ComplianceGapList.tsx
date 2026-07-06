import type {
  ComplianceGap,
} from "@/lib/types";

import ComplianceGapCard from "./ComplianceGapCard";

type ComplianceGapListProps = {
  gaps: ComplianceGap[];
  loading?: boolean;
};

export default function ComplianceGapList({
  gaps,
  loading = false,
}: ComplianceGapListProps) {
  if (loading) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
        <p className="text-sm text-slate-400">
          Loading compliance gaps...
        </p>
      </section>
    );
  }

  if (gaps.length === 0) {
    return (
      <section className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-8 text-center">
        <p className="text-lg font-semibold text-emerald-300">
          No compliance gaps found
        </p>

        <p className="mt-2 text-sm text-slate-400">
          No gaps match the selected filters.
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-100">
            Open Compliance Gaps
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Review missing evidence, linked records and recommended remediation.
          </p>
        </div>

        <span className="inline-flex w-fit rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-300">
          {gaps.length} {gaps.length === 1 ? "gap" : "gaps"}
        </span>
      </div>

      <div className="mt-6 space-y-5">
        {gaps.map((gap) => (
          <ComplianceGapCard
            key={gap.gap_id}
            gap={gap}
          />
        ))}
      </div>
    </section>
  );
}