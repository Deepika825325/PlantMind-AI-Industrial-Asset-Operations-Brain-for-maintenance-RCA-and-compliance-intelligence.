import Link from "next/link";

import type {
  ComplianceGap,
} from "@/lib/types";

type ComplianceGapCardProps = {
  gap: ComplianceGap;
};

function getSeverityClass(severity: string) {
  if (severity === "Critical") {
    return "border-red-500/40 bg-red-500/10 text-red-300";
  }

  if (severity === "High") {
    return "border-orange-500/40 bg-orange-500/10 text-orange-300";
  }

  if (severity === "Medium") {
    return "border-amber-500/40 bg-amber-500/10 text-amber-300";
  }

  return "border-slate-600 bg-slate-800 text-slate-300";
}

export default function ComplianceGapCard({
  gap,
}: ComplianceGapCardProps) {
  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-300">
              {gap.gap_id}
            </span>

            <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-300">
              {gap.asset_id}
            </span>

            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-300">
              {gap.rule_id}
            </span>

            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${getSeverityClass(
                gap.severity
              )}`}
            >
              {gap.severity}
            </span>
          </div>

          <h3 className="mt-4 text-lg font-semibold text-slate-100">
            {gap.rule_name}
          </h3>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            {gap.description}
          </p>
        </div>

        <span className="inline-flex w-fit rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-300">
          {gap.status}
        </span>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
            Available Evidence
          </p>

          {gap.available_evidence.length > 0 ? (
            <ul className="mt-3 space-y-2">
              {gap.available_evidence.map((evidence) => (
                <li
                  key={evidence}
                  className="text-sm leading-6 text-emerald-300"
                >
                  {evidence}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-slate-500">
              No evidence is currently available.
            </p>
          )}
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
            Missing Evidence
          </p>

          {gap.missing_evidence.length > 0 ? (
            <ul className="mt-3 space-y-2">
              {gap.missing_evidence.map((evidence) => (
                <li
                  key={evidence}
                  className="text-sm leading-6 text-red-300"
                >
                  {evidence}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-emerald-300">
              No evidence is missing.
            </p>
          )}
        </section>
      </div>

      <section className="mt-5 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-cyan-400">
          Recommended Remediation
        </p>

        <p className="mt-3 text-sm leading-6 text-slate-300">
          {gap.recommendation}
        </p>
      </section>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <section>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Documents
          </p>

          <div className="mt-2 flex flex-wrap gap-2">
            {gap.linked_document_ids.length > 0 ? (
              gap.linked_document_ids.map((documentId) => (
                <span
                  key={documentId}
                  className="rounded-lg bg-slate-800 px-3 py-2 text-xs text-slate-300"
                >
                  {documentId}
                </span>
              ))
            ) : (
              <span className="text-sm text-slate-600">
                None
              </span>
            )}
          </div>
        </section>

        <section>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Work Orders
          </p>

          <div className="mt-2 flex flex-wrap gap-2">
            {gap.linked_work_order_ids.length > 0 ? (
              gap.linked_work_order_ids.map((workOrderId) => (
                <Link
                  key={workOrderId}
                  href={`/maintenance?asset=${encodeURIComponent(
                    gap.asset_id
                  )}`}
                  className="rounded-lg bg-slate-800 px-3 py-2 text-xs text-cyan-300 transition hover:bg-slate-700"
                >
                  {workOrderId}
                </Link>
              ))
            ) : (
              <span className="text-sm text-slate-600">
                None
              </span>
            )}
          </div>
        </section>

        <section>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            RCA Cases
          </p>

          <div className="mt-2 flex flex-wrap gap-2">
            {gap.linked_rca_case_ids.length > 0 ? (
              gap.linked_rca_case_ids.map((caseId) => (
                <Link
                  key={caseId}
                  href={`/rca?case=${encodeURIComponent(caseId)}`}
                  className="rounded-lg bg-slate-800 px-3 py-2 text-xs text-cyan-300 transition hover:bg-slate-700"
                >
                  {caseId}
                </Link>
              ))
            ) : (
              <span className="text-sm text-slate-600">
                None
              </span>
            )}
          </div>
        </section>
      </div>

      <p className="mt-5 text-xs text-slate-600">
        Confidence: {(gap.confidence * 100).toFixed(0)}%
      </p>
    </article>
  );
}