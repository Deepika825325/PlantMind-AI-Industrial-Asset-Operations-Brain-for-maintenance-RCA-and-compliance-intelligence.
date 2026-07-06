"use client";

import Link from "next/link";

type LinkedRcaPanelProps = {
  rcaCaseId: string | null;
  rootCauseIds: string[];
  sourceType: string;
  sourceId: string;
};

export default function LinkedRcaPanel({
  rcaCaseId,
  rootCauseIds,
  sourceType,
  sourceId
}: LinkedRcaPanelProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-violet-400">
            RCA Linkage
          </p>

          <h3 className="mt-2 text-lg font-semibold text-slate-100">
            Root Cause and Source Context
          </h3>
        </div>

        {rcaCaseId && (
          <Link
            href={`/rca?case=${encodeURIComponent(rcaCaseId)}`}
            className="rounded-xl border border-violet-500/30 bg-violet-500/10 px-4 py-2 text-sm font-medium text-violet-300 transition hover:border-violet-400 hover:text-violet-200"
          >
            Open RCA
          </Link>
        )}
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            RCA Case
          </p>

          <p className="mt-2 text-sm font-medium text-slate-200">
            {rcaCaseId ?? "Not linked"}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Work Order Source
          </p>

          <p className="mt-2 text-sm font-medium text-slate-200">
            {sourceType}
          </p>

          <p className="mt-1 break-all text-xs text-slate-500">
            {sourceId}
          </p>
        </div>
      </div>

      <div className="mt-5">
        <p className="text-xs uppercase tracking-wider text-slate-500">
          Linked Root Causes
        </p>

        {rootCauseIds.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {rootCauseIds.map((causeId) => (
              <span
                key={causeId}
                className="rounded-full border border-violet-500/20 bg-violet-500/5 px-3 py-1 text-xs font-medium text-violet-300"
              >
                {causeId}
              </span>
            ))}
          </div>
        ) : (
          <p className="mt-3 text-sm text-slate-500">
            No RCA root causes are linked to this work order.
          </p>
        )}
      </div>

      {rcaCaseId && (
        <div className="mt-5 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
          <p className="text-sm leading-6 text-cyan-200">
            This work order was generated from findings associated with{" "}
            <span className="font-semibold">{rcaCaseId}</span>.
          </p>
        </div>
      )}
    </section>
  );
}