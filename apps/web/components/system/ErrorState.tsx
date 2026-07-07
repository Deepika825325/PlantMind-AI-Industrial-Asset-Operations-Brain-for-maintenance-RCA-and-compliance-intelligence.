"use client";

type ErrorStateProps = {
  title?: string;
  message: string;
  requestId?: string | null;
  backendUnavailable?: boolean;
  retryLabel?: string;
  onRetry?: (() => void) | null;
  compact?: boolean;
};

export default function ErrorState({
  title,
  message,
  requestId,
  backendUnavailable = false,
  retryLabel = "Retry",
  onRetry,
  compact = false,
}: ErrorStateProps) {
  const resolvedTitle =
    title ||
    (
      backendUnavailable
        ? "PlantMind backend unavailable"
        : "PlantMind could not load this data"
    );

  return (
    <div
      role="alert"
      className={`w-full rounded-2xl border ${
        backendUnavailable
          ? "border-amber-800/80 bg-amber-950/30"
          : "border-red-900/80 bg-red-950/30"
      } ${compact ? "p-5" : "p-8"}`}
    >
      <div className="flex min-w-0 flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p
            className={`font-semibold ${
              backendUnavailable
                ? "text-amber-200"
                : "text-red-200"
            }`}
          >
            {resolvedTitle}
          </p>

          <p className="mt-2 break-words text-sm leading-6 text-slate-300">
            {message}
          </p>

          {backendUnavailable ? (
            <p className="mt-3 text-sm leading-6 text-slate-400">
              Confirm that the PlantMind API is running and that the configured backend URL is reachable.
            </p>
          ) : null}

          {requestId ? (
            <p className="mt-3 break-all font-mono text-xs text-slate-500">
              Request ID: {requestId}
            </p>
          ) : null}
        </div>

        {onRetry ? (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex min-h-11 shrink-0 items-center justify-center rounded-xl border border-slate-600 bg-slate-800 px-5 py-2.5 text-sm font-medium text-slate-100 transition hover:border-slate-500 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-slate-950"
          >
            {retryLabel}
          </button>
        ) : null}
      </div>
    </div>
  );
}
