type LoadingStateProps = {
  title?: string;
  message?: string;
  compact?: boolean;
};

export default function LoadingState({
  title = "Loading PlantMind data",
  message = "Retrieving the latest industrial intelligence.",
  compact = false,
}: LoadingStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`w-full rounded-2xl border border-slate-800 bg-slate-900 ${
        compact ? "p-5" : "p-8"
      }`}
    >
      <div className="flex min-w-0 items-start gap-4">
        <div
          className="mt-0.5 h-6 w-6 shrink-0 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-400"
          aria-hidden="true"
        />

        <div className="min-w-0">
          <p className="font-semibold text-slate-100">
            {title}
          </p>

          <p className="mt-1 break-words text-sm leading-6 text-slate-400">
            {message}
          </p>
        </div>
      </div>
    </div>
  );
}
