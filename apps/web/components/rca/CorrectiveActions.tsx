import type {
  RcaCorrectiveAction,
  RcaRootCause,
} from "@/lib/types";

type CorrectiveActionsProps = {
  actions: RcaCorrectiveAction[];
  rootCauses: RcaRootCause[];
};

function formatDueTime(hours: number): string {
  if (hours <= 0) {
    return "Immediate";
  }

  if (hours < 24) {
    return `Within ${hours} hour${hours === 1 ? "" : "s"}`;
  }

  const days = hours / 24;

  if (Number.isInteger(days)) {
    return `Within ${days} day${days === 1 ? "" : "s"}`;
  }

  return `Within ${hours} hours`;
}

function getPriorityClasses(priority: string): string {
  const normalized = priority.toLowerCase();

  if (
    normalized === "critical" ||
    normalized === "p0"
  ) {
    return "border-red-500/40 bg-red-500/10 text-red-300";
  }

  if (
    normalized === "high" ||
    normalized === "p1"
  ) {
    return "border-orange-500/40 bg-orange-500/10 text-orange-300";
  }

  if (
    normalized === "medium" ||
    normalized === "p2"
  ) {
    return "border-amber-500/40 bg-amber-500/10 text-amber-300";
  }

  return "border-emerald-500/40 bg-emerald-500/10 text-emerald-300";
}

function getStatusClasses(status: string): string {
  const normalized = status.toLowerCase();

  if (
    normalized === "completed" ||
    normalized === "closed"
  ) {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  if (
    normalized.includes("progress") ||
    normalized.includes("active")
  ) {
    return "border-cyan-500/30 bg-cyan-500/10 text-cyan-300";
  }

  if (
    normalized.includes("blocked") ||
    normalized.includes("overdue")
  ) {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  return "border-slate-700 bg-slate-800 text-slate-300";
}

function getActionBorderClasses(priority: string): string {
  const normalized = priority.toLowerCase();

  if (
    normalized === "critical" ||
    normalized === "p0"
  ) {
    return "border-red-500/25";
  }

  if (
    normalized === "high" ||
    normalized === "p1"
  ) {
    return "border-orange-500/25";
  }

  if (
    normalized === "medium" ||
    normalized === "p2"
  ) {
    return "border-amber-500/25";
  }

  return "border-slate-800";
}

export default function CorrectiveActions({
  actions,
  rootCauses,
}: CorrectiveActionsProps) {
  const causesById = new Map(
    rootCauses.map((cause) => [cause.cause_id, cause])
  );

  const orderedActions = [...actions].sort(
    (first, second) => {
      const priorityOrder: Record<string, number> = {
        critical: 0,
        p0: 0,
        high: 1,
        p1: 1,
        medium: 2,
        p2: 2,
        low: 3,
        p3: 3,
      };

      const firstPriority =
        priorityOrder[first.priority.toLowerCase()] ?? 99;

      const secondPriority =
        priorityOrder[second.priority.toLowerCase()] ?? 99;

      if (firstPriority !== secondPriority) {
        return firstPriority - secondPriority;
      }

      return first.due_in_hours - second.due_in_hours;
    }
  );

  const completedActions = orderedActions.filter((action) => {
    const status = action.status.toLowerCase();

    return (
      status === "completed" ||
      status === "closed"
    );
  }).length;

  const urgentActions = orderedActions.filter(
    (action) => action.due_in_hours <= 24
  ).length;

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 border-b border-slate-800 pb-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-cyan-400">
            Corrective and Preventive Actions
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            Recommended response plan
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Prioritized actions to control the immediate risk, restore the
            asset and prevent recurrence of the identified failure modes.
          </p>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Total
            </p>

            <p className="mt-1 text-2xl font-semibold text-cyan-400">
              {orderedActions.length}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Urgent
            </p>

            <p className="mt-1 text-2xl font-semibold text-orange-300">
              {urgentActions}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Completed
            </p>

            <p className="mt-1 text-2xl font-semibold text-emerald-300">
              {completedActions}
            </p>
          </div>
        </div>
      </div>

      {orderedActions.length === 0 && (
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-6 text-sm text-slate-500">
          No corrective actions are available for this RCA case.
        </div>
      )}

      <div className="mt-6 grid gap-5 xl:grid-cols-2">
        {orderedActions.map((action, index) => {
          const linkedCauses = action.linked_cause_ids
            .map((causeId) => causesById.get(causeId))
            .filter(
              (cause): cause is RcaRootCause =>
                cause !== undefined
            );

          return (
            <article
              key={action.action_id}
              className={`rounded-2xl border bg-slate-950 p-5 ${getActionBorderClasses(
                action.priority
              )}`}
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-cyan-500/25 bg-cyan-500/10 text-lg font-semibold text-cyan-300">
                    {index + 1}
                  </div>

                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`rounded-full border px-3 py-1 text-xs font-semibold ${getPriorityClasses(
                          action.priority
                        )}`}
                      >
                        {action.priority} priority
                      </span>

                      <span
                        className={`rounded-full border px-3 py-1 text-xs font-medium ${getStatusClasses(
                          action.status
                        )}`}
                      >
                        {action.status}
                      </span>
                    </div>

                    <h3 className="mt-4 text-lg font-semibold leading-7 text-slate-100">
                      {action.title}
                    </h3>
                  </div>
                </div>

                <span className="shrink-0 text-xs text-slate-600">
                  {action.action_id}
                </span>
              </div>

              <p className="mt-5 text-sm leading-7 text-slate-300">
                {action.description}
              </p>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Responsible owner
                  </p>

                  <p className="mt-2 text-sm font-semibold text-slate-200">
                    {action.owner_role}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Required by
                  </p>

                  <p className="mt-2 text-sm font-semibold text-orange-300">
                    {formatDueTime(action.due_in_hours)}
                  </p>
                </div>
              </div>

              <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900 p-4">
                <p className="text-xs uppercase tracking-wider text-slate-500">
                  Verification metric
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {action.verification_metric}
                </p>
              </div>

              <div className="mt-5 border-t border-slate-800 pt-5">
                <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                  Linked root causes
                </p>

                {linkedCauses.length === 0 ? (
                  <p className="mt-3 text-sm text-slate-500">
                    No root causes are linked to this action.
                  </p>
                ) : (
                  <div className="mt-3 space-y-2">
                    {linkedCauses.map((cause) => (
                      <div
                        key={cause.cause_id}
                        className="flex items-start gap-3 rounded-xl border border-slate-800 bg-slate-900 p-3"
                      >
                        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-cyan-500/10 text-xs font-semibold text-cyan-300">
                          {cause.rank}
                        </span>

                        <div>
                          <p className="text-sm font-medium text-slate-200">
                            {cause.title}
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            {cause.cause_id} ·{" "}
                            {Math.round(cause.confidence * 100)}%
                            confidence
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}