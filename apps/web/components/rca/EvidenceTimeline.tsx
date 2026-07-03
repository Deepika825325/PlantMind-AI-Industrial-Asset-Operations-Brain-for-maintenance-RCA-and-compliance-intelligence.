import type {
  RcaEvidence,
  RcaTimelineEvent,
} from "@/lib/types";

type EvidenceTimelineProps = {
  timeline: RcaTimelineEvent[];
  evidence: RcaEvidence[];
};

function formatDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
  }).format(date);
}

function formatTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return new Intl.DateTimeFormat("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
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

function getTimelineDotClasses(severity: string): string {
  const normalized = severity.toLowerCase();

  if (normalized === "critical") {
    return "border-red-300 bg-red-500 shadow-red-500/40";
  }

  if (normalized === "high") {
    return "border-orange-300 bg-orange-500 shadow-orange-500/40";
  }

  if (normalized === "medium") {
    return "border-amber-300 bg-amber-500 shadow-amber-500/40";
  }

  return "border-emerald-300 bg-emerald-500 shadow-emerald-500/40";
}

function getEventTypeClasses(eventType: string): string {
  const normalized = eventType.toLowerCase();

  if (normalized.includes("compliance")) {
    return "border-violet-500/30 bg-violet-500/10 text-violet-300";
  }

  if (normalized.includes("sensor")) {
    return "border-cyan-500/30 bg-cyan-500/10 text-cyan-300";
  }

  if (normalized.includes("inspection")) {
    return "border-blue-500/30 bg-blue-500/10 text-blue-300";
  }

  if (normalized.includes("maintenance")) {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  return "border-slate-700 bg-slate-800 text-slate-300";
}

export default function EvidenceTimeline({
  timeline,
  evidence,
}: EvidenceTimelineProps) {
  const sortedTimeline = [...timeline].sort(
    (first, second) =>
      new Date(first.timestamp).getTime() -
      new Date(second.timestamp).getTime()
  );

  const evidenceById = new Map(
    evidence.map((item) => [item.evidence_id, item])
  );

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-3 border-b border-slate-800 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-cyan-400">
            Evidence Timeline
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            Incident progression
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Chronological evidence showing how the incident developed from
            an initial control gap to confirmed equipment degradation.
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Timeline events
          </p>

          <p className="mt-1 text-2xl font-semibold text-cyan-400">
            {sortedTimeline.length}
          </p>
        </div>
      </div>

      {sortedTimeline.length === 0 && (
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-6 text-sm text-slate-500">
          No timeline events are available for this RCA case.
        </div>
      )}

      <div className="relative mt-8">
        {sortedTimeline.length > 1 && (
          <div className="absolute bottom-8 left-[19px] top-8 w-px bg-slate-700" />
        )}

        <div className="space-y-6">
          {sortedTimeline.map((event, index) => {
            const linkedEvidence = event.evidence_ids
              .map((evidenceId) => evidenceById.get(evidenceId))
              .filter(
                (item): item is RcaEvidence => item !== undefined
              );

            return (
              <article
                key={event.event_id}
                className="relative grid gap-4 pl-14 lg:grid-cols-[180px_minmax(0,1fr)]"
              >
                <div
                  className={`absolute left-2 top-6 z-10 flex h-6 w-6 items-center justify-center rounded-full border-2 shadow-lg ${getTimelineDotClasses(
                    event.severity
                  )}`}
                >
                  <span className="text-[10px] font-bold text-slate-950">
                    {index + 1}
                  </span>
                </div>

                <div className="pt-1">
                  <p className="text-sm font-semibold text-slate-200">
                    {formatDate(event.timestamp)}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {formatTime(event.timestamp)}
                  </p>

                  <span
                    className={`mt-3 inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${getSeverityClasses(
                      event.severity
                    )}`}
                  >
                    {event.severity}
                  </span>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <span
                        className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${getEventTypeClasses(
                          event.event_type
                        )}`}
                      >
                        {event.event_type}
                      </span>

                      <h3 className="mt-4 text-lg font-semibold text-slate-100">
                        {event.title}
                      </h3>
                    </div>

                    <span className="text-xs text-slate-600">
                      {event.event_id}
                    </span>
                  </div>

                  <p className="mt-3 text-sm leading-7 text-slate-300">
                    {event.description}
                  </p>

                  <div className="mt-5 border-t border-slate-800 pt-5">
                    <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                      Supporting evidence
                    </p>

                    {linkedEvidence.length === 0 && (
                      <p className="mt-3 text-sm text-slate-500">
                        No linked evidence was found for this event.
                      </p>
                    )}

                    <div className="mt-3 space-y-3">
                      {linkedEvidence.map((item) => (
                        <div
                          key={item.evidence_id}
                          className="rounded-xl border border-slate-800 bg-slate-900 p-4"
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

                            <span className="shrink-0 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                              {item.evidence_id}
                            </span>
                          </div>

                          <blockquote className="mt-4 border-l-2 border-cyan-500/40 pl-4 text-sm italic leading-6 text-slate-400">
                            {item.excerpt}
                          </blockquote>

                          <p className="mt-3 break-all text-xs text-slate-600">
                            Document ID: {item.document_id}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}