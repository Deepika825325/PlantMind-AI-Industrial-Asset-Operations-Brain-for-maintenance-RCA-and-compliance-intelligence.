import type {
  RcaCausalStep,
  RcaEvidence,
} from "@/lib/types";

type CausalChainProps = {
  steps: RcaCausalStep[];
  evidence: RcaEvidence[];
};

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function getCategoryClasses(category: string): string {
  const normalized = category.toLowerCase();

  if (normalized.includes("maintenance")) {
    return "border-violet-500/30 bg-violet-500/10 text-violet-300";
  }

  if (
    normalized.includes("physical") ||
    normalized.includes("mechanical")
  ) {
    return "border-orange-500/30 bg-orange-500/10 text-orange-300";
  }

  if (normalized.includes("thermal")) {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  if (
    normalized.includes("sensor") ||
    normalized.includes("instrument")
  ) {
    return "border-cyan-500/30 bg-cyan-500/10 text-cyan-300";
  }

  if (
    normalized.includes("process") ||
    normalized.includes("hydraulic")
  ) {
    return "border-blue-500/30 bg-blue-500/10 text-blue-300";
  }

  return "border-slate-700 bg-slate-800 text-slate-300";
}

function getConfidenceClasses(confidence: number): string {
  if (confidence >= 0.9) {
    return "text-emerald-300";
  }

  if (confidence >= 0.75) {
    return "text-cyan-300";
  }

  if (confidence >= 0.6) {
    return "text-amber-300";
  }

  return "text-red-300";
}

export default function CausalChain({
  steps,
  evidence,
}: CausalChainProps) {
  const orderedSteps = [...steps].sort(
    (first, second) => first.sequence - second.sequence
  );

  const evidenceById = new Map(
    evidence.map((item) => [item.evidence_id, item])
  );

  const averageConfidence =
    orderedSteps.length > 0
      ? orderedSteps.reduce(
          (total, step) => total + step.confidence,
          0
        ) / orderedSteps.length
      : 0;

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-cyan-400">
            Causal Chain
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            How the incident developed
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Ordered reasoning that connects the initial control failure
            to the final observed asset condition.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Chain steps
            </p>

            <p className="mt-1 text-2xl font-semibold text-cyan-400">
              {orderedSteps.length}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Confidence
            </p>

            <p
              className={`mt-1 text-2xl font-semibold ${getConfidenceClasses(
                averageConfidence
              )}`}
            >
              {formatConfidence(averageConfidence)}
            </p>
          </div>
        </div>
      </div>

      {orderedSteps.length === 0 && (
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-6 text-sm text-slate-500">
          No causal-chain steps are available for this RCA case.
        </div>
      )}

      <div className="mt-8 space-y-0">
        {orderedSteps.map((step, index) => {
          const linkedEvidence = step.evidence_ids
            .map((evidenceId) => evidenceById.get(evidenceId))
            .filter(
              (item): item is RcaEvidence => item !== undefined
            );

          const isLastStep = index === orderedSteps.length - 1;

          return (
            <div key={step.step_id}>
              <article className="grid gap-5 rounded-2xl border border-slate-800 bg-slate-950 p-5 lg:grid-cols-[80px_minmax(0,1fr)_220px]">
                <div className="flex items-start justify-center">
                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-500/30 bg-cyan-500/10 text-xl font-semibold text-cyan-300">
                    {step.sequence}
                  </div>
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${getCategoryClasses(
                        step.category
                      )}`}
                    >
                      {step.category}
                    </span>

                    <span className="text-xs text-slate-600">
                      {step.step_id}
                    </span>
                  </div>

                  <h3 className="mt-4 text-xl font-semibold text-slate-100">
                    {step.title}
                  </h3>

                  <p className="mt-3 text-sm leading-7 text-slate-300">
                    {step.description}
                  </p>

                  <div className="mt-5">
                    <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                      Supporting evidence
                    </p>

                    {linkedEvidence.length === 0 && (
                      <p className="mt-3 text-sm text-slate-500">
                        No evidence is linked to this causal step.
                      </p>
                    )}

                    <div className="mt-3 grid gap-3 xl:grid-cols-2">
                      {linkedEvidence.map((item) => (
                        <div
                          key={item.evidence_id}
                          className="rounded-xl border border-slate-800 bg-slate-900 p-4"
                        >
                          <div className="flex flex-wrap items-start justify-between gap-3">
                            <div>
                              <p className="text-sm font-semibold text-slate-100">
                                {item.document_title}
                              </p>

                              <p className="mt-1 text-xs text-slate-500">
                                {item.document_type}
                              </p>
                            </div>

                            <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                              {item.evidence_id}
                            </span>
                          </div>

                          <p className="mt-3 text-xs font-medium text-slate-400">
                            {item.section_title}
                          </p>

                          <p className="mt-2 text-sm leading-6 text-slate-400">
                            {item.excerpt}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Step Confidence
                  </p>

                  <p
                    className={`mt-3 text-3xl font-semibold ${getConfidenceClasses(
                      step.confidence
                    )}`}
                  >
                    {formatConfidence(step.confidence)}
                  </p>

                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-cyan-400"
                      style={{
                        width: formatConfidence(step.confidence),
                      }}
                    />
                  </div>

                  <p className="mt-4 text-xs leading-5 text-slate-500">
                    Supported by {step.evidence_ids.length} evidence
                    {step.evidence_ids.length === 1 ? " item" : " items"}.
                  </p>
                </div>
              </article>

              {!isLastStep && (
                <div className="flex h-16 items-center justify-center">
                  <div className="flex flex-col items-center">
                    <div className="h-8 w-px bg-cyan-500/50" />

                    <div className="flex h-7 w-7 items-center justify-center rounded-full border border-cyan-500/40 bg-cyan-500/10 text-sm text-cyan-300">
                      ↓
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}