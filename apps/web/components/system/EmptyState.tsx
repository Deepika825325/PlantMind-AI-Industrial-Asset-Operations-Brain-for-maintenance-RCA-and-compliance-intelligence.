import Link from "next/link";

type EmptyStateProps = {
  title?: string;
  message: string;
  actionLabel?: string;
  actionHref?: string;
};

export default function EmptyState({
  title = "No data available",
  message,
  actionLabel,
  actionHref,
}: EmptyStateProps) {
  return (
    <div className="w-full rounded-2xl border border-dashed border-slate-700 bg-slate-900 p-8 text-center">
      <div
        className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-slate-700 bg-slate-950 text-xl text-slate-400"
        aria-hidden="true"
      >
        —
      </div>

      <h2 className="mt-4 text-lg font-semibold text-slate-100">
        {title}
      </h2>

      <p className="mx-auto mt-2 max-w-2xl break-words text-sm leading-6 text-slate-400">
        {message}
      </p>

      {actionLabel && actionHref ? (
        <Link
          href={actionHref}
          className="mt-5 inline-flex min-h-11 items-center justify-center rounded-xl border border-slate-700 bg-slate-800 px-5 py-2.5 text-sm font-medium text-slate-100 transition hover:border-slate-600 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-slate-950"
        >
          {actionLabel}
        </Link>
      ) : null}
    </div>
  );
}
