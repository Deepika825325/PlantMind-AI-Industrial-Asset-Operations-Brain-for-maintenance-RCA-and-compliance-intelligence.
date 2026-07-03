"use client";

import type { RcaCaseSummary } from "@/lib/types";

type IncidentSelectorProps = {
  cases: RcaCaseSummary[];
  selectedCaseId: string;
  onSelectCase: (caseId: string) => void;
  disabled?: boolean;
};

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

function formatDetectedAt(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getSeverityClasses(severity: string): string {
  const normalizedSeverity = severity.toLowerCase();

  if (normalizedSeverity === "critical") {
    return "border-red-500/40 bg-red-500/10 text-red-300";
  }

  if (normalizedSeverity === "high") {
    return "border-orange-500/40 bg-orange-500/10 text-orange-300";
  }

  if (normalizedSeverity === "medium") {
    return "border-amber-500/40 bg-amber-500/10 text-amber-300";
  }

  return "border-emerald-500/40 bg-emerald-500/10 text-emerald-300";
}

export default function IncidentSelector({
  cases,
  selectedCaseId,
  onSelectCase,
  disabled = false,
}: IncidentSelectorProps) {
  const selectedCase =
    cases.find((incident) => incident.case_id === selectedCaseId) ??
    cases[0] ??
    null;

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-cyan-400">
            Incident Selector
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            Select an RCA case
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Choose an incident to inspect its evidence timeline, causal chain,
            ranked root causes and recommended corrective actions.
          </p>
        </div>

        <div className="w-full xl:max-w-xl">
          <label
            htmlFor="rca-case-selector"
            className="text-sm font-medium text-slate-300"
          >
            RCA incident
          </label>

          <select
            id="rca-case-selector"
            value={selectedCaseId}
            disabled={disabled || cases.length === 0}
            onChange={(event) => onSelectCase(event.target.value)}
            className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {cases.length === 0 && (
              <option value="">No RCA cases available</option>
            )}

            {cases.map((incident) => (
              <option key={incident.case_id} value={incident.case_id}>
                {incident.case_id} — {incident.asset_id} — {incident.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedCase && (
        <div className="mt-6 grid gap-4 border-t border-slate-800 pt-6 md:grid-cols-2 xl:grid-cols-5">
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Asset
            </p>

            <p className="mt-2 text-lg font-semibold text-slate-100">
              {selectedCase.asset_id}
            </p>

            <p className="mt-1 text-sm text-slate-400">
              {selectedCase.asset_name}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Severity
            </p>

            <span
              className={`mt-3 inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${getSeverityClasses(
                selectedCase.severity
              )}`}
            >
              {selectedCase.severity}
            </span>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Status
            </p>

            <p className="mt-2 text-lg font-semibold text-slate-100">
              {selectedCase.incident_status}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {formatDetectedAt(selectedCase.detected_at)}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              RCA Confidence
            </p>

            <p className="mt-2 text-2xl font-semibold text-cyan-400">
              {formatConfidence(selectedCase.overall_confidence)}
            </p>

            <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-cyan-400 transition-all"
                style={{
                  width: formatConfidence(selectedCase.overall_confidence),
                }}
              />
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Leading Cause
            </p>

            <p className="mt-2 text-sm font-semibold leading-6 text-slate-100">
              {selectedCase.top_root_cause?.title ?? "Not available"}
            </p>

            {selectedCase.top_root_cause && (
              <p className="mt-2 text-xs text-cyan-400">
                {formatConfidence(
                  selectedCase.top_root_cause.confidence
                )}{" "}
                confidence
              </p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}