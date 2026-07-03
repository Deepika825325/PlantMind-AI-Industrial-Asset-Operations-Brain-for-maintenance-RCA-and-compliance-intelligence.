import type {
  RcaEvidence,
  RcaRootCause,
} from "@/lib/types";

type RootCauseRankingProps = {
  causes: RcaRootCause[];
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
    normalized.includes("mechanical") ||
    normalized.includes("equipment")
  ) {
    return "border-orange-500/30 bg-orange-500/10 text-orange-300";
  }

  if (
    normalized.includes("process") ||
    normalized.includes("operation")
  ) {
    return "border-blue-500/30 bg-blue-500/10 text-blue-300";
  }

  if (
    normalized.includes("instrument") ||
    normalized.includes("sensor")
  ) {
    return "border-cyan-500/30 bg-cyan-500/10 text-cyan-300";
  }

  if (
    normalized.includes("human") ||
    normalized.includes("procedure")
  ) {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
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

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.9) {
    return "Very high";
  }

  if (confidence >= 0.75) {
    return "High";
  }

  if (confidence >= 0.6) {
    return "Moderate";
  }

  return "Low";
}

function getRankClasses(rank: number): string {
  if (rank === 1) {
    return "border-cyan-400/40 bg-cyan-400/10 text-cyan-300";
  }

  if (rank === 2) {
    return "border-slate-500 bg-slate-800 text-slate-200";
  }

  if (rank === 3) {
    return "border-amber-700/50 bg-amber-900/20 text-amber-300";
  }

  return "border-slate-700 bg-slate-900 text-slate-400";
}

export default function RootCauseRanking({
  causes,
  evidence,
}: RootCauseRankingProps) {
  const orderedCauses = [...causes].sort(
    (first, second) => first.rank - second.rank
  );

  const evidenceById = new Map(
    evidence.map((item) => [item.evidence_id, item])
  );

  const leadingCause = orderedCauses[0] ?? null;

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 border-b border-slate-800 pb-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-cyan-400">
            Root-Cause Ranking
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            Most probable causes
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Candidate causes ranked using available maintenance,
            inspection, operating and compliance evidence.
          </p>
        </div>

        {leadingCause && (
          <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-5 py-4">
            <p className="text-xs uppercase tracking-wider text-cyan-400">
              Leading cause
            </p>

            <p className="mt-2 max-w-sm text-sm font-semibold text-slate-100">
              {leadingCause.title}
            </p>

            <p className="mt-2 text-xl font-semibold text-cyan-300">
              {formatConfidence(leadingCause.confidence)}
            </p>
          </div>
        )}
      </div>

      {orderedCauses.length === 0 && (
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-6 text-sm text-slate-500">
          No root causes are available for this RCA case.
        </div>
      )}

      <div className="mt-6 space-y-5">
        {orderedCauses.map((cause) => {
          const supportingEvidence = cause.evidence_ids
            .map((evidenceId) => evidenceById.get(evidenceId))
            .filter(
              (item): item is RcaEvidence => item !== undefined
            );

          return (
            <article
              key={cause.cause_id}
              className={`overflow-hidden rounded-2xl border ${
                cause.rank === 1
                  ? "border-cyan-500/30 bg-cyan-500/[0.04]"
                  : "border-slate-800 bg-slate-950"
              }`}
            >
              <div className="grid gap-5 p-5 xl:grid-cols-[90px_minmax(0,1fr)_220px]">
                <div>
                  <div
                    className={`flex h-16 w-16 flex-col items-center justify-center rounded-2xl border ${getRankClasses(
                      cause.rank
                    )}`}
                  >
                    <span className="text-[10px] font-medium uppercase tracking-wider">
                      Rank
                    </span>

                    <span className="text-2xl font-semibold">
                      {cause.rank}
                    </span>
                  </div>
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${getCategoryClasses(
                        cause.category
                      )}`}
                    >
                      {cause.category}
                    </span>

                    {cause.rank === 1 && (
                      <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300">
                        Primary hypothesis
                      </span>
                    )}

                    <span className="text-xs text-slate-600">
                      {cause.cause_id}
                    </span>
                  </div>

                  <h3 className="mt-4 text-xl font-semibold text-slate-100">
                    {cause.title}
                  </h3>

                  <div className="mt-5 rounded-xl border border-slate-800 bg-slate-900 p-4">
                    <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                      PlantMind reasoning
                    </p>

                    <p className="mt-3 text-sm leading-7 text-slate-300">
                      {cause.reasoning}
                    </p>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Confidence
                  </p>

                  <p
                    className={`mt-3 text-3xl font-semibold ${getConfidenceClasses(
                      cause.confidence
                    )}`}
                  >
                    {formatConfidence(cause.confidence)}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {getConfidenceLabel(cause.confidence)} confidence
                  </p>

                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-cyan-400"
                      style={{
                        width: formatConfidence(cause.confidence),
                      }}
                    />
                  </div>

                  <div className="mt-5 border-t border-slate-800 pt-4">
                    <p className="text-xs text-slate-500">
                      Supporting evidence
                    </p>

                    <p className="mt-1 text-lg font-semibold text-slate-200">
                      {supportingEvidence.length}
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid gap-5 border-t border-slate-800 p-5 xl:grid-cols-2">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.2em] text-emerald-400">
                    Supporting evidence
                  </p>

                  {supportingEvidence.length === 0 && (
                    <p className="mt-3 text-sm text-slate-500">
                      No supporting evidence is linked to this cause.
                    </p>
                  )}

                  <div className="mt-3 space-y-3">
                    {supportingEvidence.map((item) => (
                      <div
                        key={item.evidence_id}
                        className="rounded-xl border border-emerald-500/15 bg-emerald-500/[0.04] p-4"
                      >
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                          <div>
                            <p className="text-sm font-semibold text-slate-100">
                              {item.document_title}
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              {item.document_type} · {item.section_title}
                            </p>
                          </div>

                          <span className="shrink-0 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300">
                            {item.evidence_id}
                          </span>
                        </div>

                        <blockquote className="mt-3 border-l-2 border-emerald-500/40 pl-4 text-sm italic leading-6 text-slate-400">
                          {item.excerpt}
                        </blockquote>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.2em] text-amber-400">
                    Counter-evidence and uncertainty
                  </p>

                  {cause.counter_evidence.length === 0 ? (
                    <div className="mt-3 rounded-xl border border-slate-800 bg-slate-900 p-4">
                      <p className="text-sm leading-6 text-slate-500">
                        No material counter-evidence is currently recorded.
                      </p>
                    </div>
                  ) : (
                    <div className="mt-3 space-y-3">
                      {cause.counter_evidence.map(
                        (counterEvidence, index) => (
                          <div
                            key={`${cause.cause_id}-counter-${index}`}
                            className="flex items-start gap-3 rounded-xl border border-amber-500/15 bg-amber-500/[0.04] p-4"
                          >
                            <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-amber-500/10 text-xs font-semibold text-amber-300">
                              ?
                            </span>

                            <p className="text-sm leading-6 text-slate-400">
                              {counterEvidence}
                            </p>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}