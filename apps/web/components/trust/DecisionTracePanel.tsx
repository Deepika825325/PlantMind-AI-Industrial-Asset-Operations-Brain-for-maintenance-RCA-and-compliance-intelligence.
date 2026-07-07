"use client";

import type {
  DecisionTrace,
  EvidenceValidationStatus,
} from "@/lib/types";

type DecisionTracePanelProps = {
  trace: DecisionTrace | null | undefined;
  title?: string;
  className?: string;
};

type TraceListProps = {
  title: string;
  values: string[];
  emptyMessage: string;
  tone?: "default" | "warning" | "danger";
};

function getConfidenceClass(
  confidence: number
) {
  if (confidence >= 0.85) {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  if (confidence >= 0.65) {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-red-500/30 bg-red-500/10 text-red-300";
}

function getValidationClass(
  status: EvidenceValidationStatus
) {
  if (status === "Verified") {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  if (status === "Partially verified") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-red-500/30 bg-red-500/10 text-red-300";
}

function getQualityClass(
  rating: string
) {
  if (rating === "High") {
    return "border-cyan-500/30 bg-cyan-500/10 text-cyan-300";
  }

  if (rating === "Medium-High") {
    return "border-violet-500/30 bg-violet-500/10 text-violet-300";
  }

  if (rating === "Medium") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-slate-700 bg-slate-800 text-slate-300";
}

function TraceList({
  title,
  values,
  emptyMessage,
  tone = "default",
}: TraceListProps) {
  const containerClass =
    tone === "warning"
      ? "border-amber-500/20 bg-amber-500/5"
      : tone === "danger"
        ? "border-red-500/20 bg-red-500/5"
        : "border-slate-800 bg-slate-950";

  const titleClass =
    tone === "warning"
      ? "text-amber-400"
      : tone === "danger"
        ? "text-red-400"
        : "text-slate-400";

  return (
    <section
      className={`rounded-2xl border p-5 ${containerClass}`}
    >
      <p
        className={`text-xs font-semibold uppercase tracking-[0.2em] ${titleClass}`}
      >
        {title}
      </p>

      {values.length > 0 ? (
        <div className="mt-4 space-y-3">
          {values.map((value, index) => (
            <div
              key={`${title}-${index}-${value}`}
              className="flex items-start gap-3"
            >
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-slate-700 bg-slate-900 text-xs font-semibold text-slate-400">
                {index + 1}
              </span>

              <p className="text-sm leading-6 text-slate-300">
                {value}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-4 text-sm text-slate-500">
          {emptyMessage}
        </p>
      )}
    </section>
  );
}

export default function DecisionTracePanel({
  trace,
  title = "Decision Trace",
  className = "",
}: DecisionTracePanelProps) {
  if (!trace) {
    return null;
  }

  const confidencePercentage =
    Math.round(trace.confidence * 100);

  const explanation =
    trace.confidence_explanation;

  return (
    <section
      className={`overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 ${className}`}
    >
      <header className="border-b border-slate-800 p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
              Trust and Explainability
            </p>

            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-100">
              {title}
            </h2>

            <p className="mt-3 max-w-4xl text-sm leading-7 text-slate-400">
              Review the validated evidence,
              confidence reasoning, applied rules
              and verification requirements behind
              this decision.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <span
              className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${
                trace.supported
                  ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                  : "border-red-500/30 bg-red-500/10 text-red-300"
              }`}
            >
              {trace.supported
                ? "Evidence Supported"
                : "Insufficient Evidence"}
            </span>

            <span
              className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${getConfidenceClass(
                trace.confidence
              )}`}
            >
              Confidence {confidencePercentage}%
            </span>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Decision
          </p>

          <p className="mt-3 text-sm leading-7 text-slate-200">
            {trace.answer}
          </p>
        </div>
      </header>

      <div className="grid gap-px bg-slate-800 sm:grid-cols-2 xl:grid-cols-5">
        <div className="bg-slate-900 p-5">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Confidence
          </p>

          <p className="mt-2 text-2xl font-semibold text-cyan-300">
            {explanation.percentage}%
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {explanation.label}
          </p>
        </div>

        <div className="bg-slate-900 p-5">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Verified Sources
          </p>

          <p className="mt-2 text-2xl font-semibold text-emerald-300">
            {explanation.verified_source_count}
          </p>
        </div>

        <div className="bg-slate-900 p-5">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Partial Sources
          </p>

          <p className="mt-2 text-2xl font-semibold text-amber-300">
            {explanation.partial_source_count}
          </p>
        </div>

        <div className="bg-slate-900 p-5">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Missing Evidence
          </p>

          <p className="mt-2 text-2xl font-semibold text-orange-300">
            {explanation.missing_evidence_count}
          </p>
        </div>

        <div className="bg-slate-900 p-5">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Conflicts
          </p>

          <p className="mt-2 text-2xl font-semibold text-red-300">
            {explanation.conflict_count}
          </p>
        </div>
      </div>

      <div className="space-y-6 p-6">
        <div className="grid gap-6 xl:grid-cols-2">
          <TraceList
            title="Reasoning Summary"
            values={trace.reasoning_summary}
            emptyMessage="No reasoning summary was provided."
          />

          <TraceList
            title="Confidence Explanation"
            values={explanation.why}
            emptyMessage="No confidence explanation was provided."
          />
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <TraceList
            title="Rules Applied"
            values={trace.rules_applied}
            emptyMessage="No explicit rules were recorded."
          />

          <TraceList
            title="Evidence Not Found"
            values={trace.evidence_not_found}
            emptyMessage="No required evidence is currently missing."
            tone="warning"
          />
        </div>

        <TraceList
          title="Conflicting Evidence"
          values={trace.conflicting_evidence}
          emptyMessage="No material conflicting evidence was identified."
          tone="danger"
        />

        <section className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <div className="flex flex-col gap-6 xl:flex-row">
            <div className="flex-1">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
                Recommended Action
              </p>

              <p className="mt-3 text-sm leading-7 text-slate-300">
                {trace.recommended_action ??
                  "No recommended action was provided."}
              </p>
            </div>

            <div className="hidden w-px bg-slate-800 xl:block" />

            <div className="flex-1">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-400">
                Verification Method
              </p>

              <p className="mt-3 text-sm leading-7 text-slate-300">
                {trace.verification_method ??
                  "No verification method was provided."}
              </p>
            </div>
          </div>
        </section>

        <section>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
                Validated Evidence
              </p>

              <h3 className="mt-2 text-lg font-semibold text-slate-100">
                Evidence Integrity Results
              </h3>
            </div>

            <p className="text-xs text-slate-500">
              {trace.evidence_used.length}{" "}
              {trace.evidence_used.length === 1
                ? "evidence item"
                : "evidence items"}
            </p>
          </div>

          {trace.evidence_used.length > 0 ? (
            <div className="mt-5 grid gap-4 xl:grid-cols-2">
              {trace.evidence_used.map(
                (evidence) => (
                  <article
                    key={evidence.citation_id}
                    className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                  >
                    <div className="flex flex-wrap gap-2">
                      <span
                        className={`rounded-full border px-3 py-1 text-xs font-semibold ${getValidationClass(
                          evidence.validation_status
                        )}`}
                      >
                        {evidence.validation_status}
                      </span>

                      <span
                        className={`rounded-full border px-3 py-1 text-xs font-semibold ${getQualityClass(
                          evidence.source_quality.rating
                        )}`}
                      >
                        {evidence.source_quality.rating} quality
                      </span>
                    </div>

                    <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      {evidence.document_type}
                    </p>

                    <h4 className="mt-2 font-semibold text-slate-100">
                      {evidence.document_title}
                    </h4>

                    <p className="mt-1 text-xs text-slate-500">
                      {evidence.document_id}
                    </p>

                    <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900 p-4">
                      <p className="text-xs font-medium text-slate-500">
                        {evidence.section_title}
                      </p>

                      <p className="mt-2 text-sm leading-6 text-slate-300">
                        {evidence.evidence_excerpt}
                      </p>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2 text-xs">
                      <span className="rounded-lg bg-slate-800 px-2.5 py-1.5 text-slate-300">
                        {evidence.source_quality.label}
                      </span>

                      <span className="rounded-lg bg-slate-800 px-2.5 py-1.5 text-slate-400">
                        Citation {evidence.citation_id}
                      </span>
                    </div>
                  </article>
                )
              )}
            </div>
          ) : (
            <div className="mt-5 rounded-2xl border border-dashed border-slate-700 bg-slate-950 p-6 text-sm text-slate-500">
              No validated evidence was available.
            </div>
          )}
        </section>
      </div>
    </section>
  );
}
