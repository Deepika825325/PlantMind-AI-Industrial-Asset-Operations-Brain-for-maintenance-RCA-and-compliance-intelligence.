import Link from "next/link";

import type { RcaCase } from "@/lib/types";

type IncidentSummaryProps = {
  incident: RcaCase;
};

function formatDateTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function getSeverityClasses(severity: string): string {
  const normalized = severity.toLowerCase();

  if (normalized === "critical") {
    return "border-red-500/40 bg-red-500/10 text-red-300";
  }

  if (normalized === "high") {
    return "border-orange-500/40 bg-orange-500/10 text-orange-300";
  }

  if (normalized === "medium") {
    return "border-amber-500/40 bg-amber-500/10 text-amber-300";
  }

  return "border-emerald-500/40 bg-emerald-500/10 text-emerald-300";
}

function getStatusClasses(status: string): string {
  const normalized = status.toLowerCase();

  if (normalized === "open") {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  if (normalized.includes("investigation")) {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  if (normalized === "closed") {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  return "border-slate-600 bg-slate-800 text-slate-300";
}

export default function IncidentSummary({
  incident,
}: IncidentSummaryProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-4xl">
          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${getSeverityClasses(
                incident.severity
              )}`}
            >
              {incident.severity}
            </span>

            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${getStatusClasses(
                incident.incident_status
              )}`}
            >
              {incident.incident_status}
            </span>

            <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-400">
              {incident.case_id}
            </span>
          </div>

          <h2 className="mt-5 text-3xl font-semibold tracking-tight text-slate-100">
            {incident.title}
          </h2>

          <p className="mt-3 text-sm text-slate-400">
            Detected {formatDateTime(incident.detected_at)}
          </p>
        </div>

        <div className="min-w-48 rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">
            Overall Confidence
          </p>

          <p className="mt-3 text-4xl font-semibold text-cyan-300">
            {formatConfidence(incident.overall_confidence)}
          </p>

          <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
            <div
              className="h-full rounded-full bg-cyan-400"
              style={{
                width: formatConfidence(
                  incident.overall_confidence
                ),
              }}
            />
          </div>
        </div>
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-2">
        <article className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Asset
          </p>

          <h3 className="mt-3 text-xl font-semibold text-slate-100">
            {incident.asset_id}
          </h3>

          <p className="mt-1 text-sm text-slate-300">
            {incident.asset_name}
          </p>

          <p className="mt-1 text-sm text-slate-500">
            {incident.asset_type}
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Problem Statement
          </p>

          <p className="mt-3 text-sm leading-7 text-slate-300">
            {incident.problem_statement}
          </p>
        </article>
      </div>

      <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-950 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
          RCA Summary
        </p>

        <p className="mt-3 text-base leading-8 text-slate-200">
          {incident.summary}
        </p>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_420px]">
        <article className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Observed Symptoms
          </p>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {incident.symptoms.map((symptom) => (
              <div
                key={symptom}
                className="flex items-start gap-3 rounded-xl border border-slate-800 bg-slate-900 p-4"
              >
                <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-500/15 text-xs text-red-300">
                  !
                </span>

                <p className="text-sm leading-6 text-slate-300">
                  {symptom}
                </p>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">
            PlantMind Recommendation
          </p>

          <p className="mt-4 text-sm leading-7 text-slate-200">
            {incident.recommendation_summary}
          </p>
        </article>
      </div>

      <div className="mt-6 flex flex-wrap gap-3 border-t border-slate-800 pt-6">
        <Link
          href={`/assets/${incident.asset_id}`}
          className="rounded-xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        >
          Open Asset 360
        </Link>

        <Link
          href={`/ask?asset=${incident.asset_id}`}
          className="rounded-xl border border-slate-700 bg-slate-950 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-cyan-400 hover:text-white"
        >
          Ask PlantMind
        </Link>

        <Link
          href={`/compliance?asset=${incident.asset_id}`}
          className="rounded-xl border border-slate-700 bg-slate-950 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-cyan-400 hover:text-white"
        >
          View Compliance
        </Link>

        <Link
          href="/pid"
          className="rounded-xl border border-slate-700 bg-slate-950 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-cyan-400 hover:text-white"
        >
          Open P&amp;ID
        </Link>
      </div>
    </section>
  );
}