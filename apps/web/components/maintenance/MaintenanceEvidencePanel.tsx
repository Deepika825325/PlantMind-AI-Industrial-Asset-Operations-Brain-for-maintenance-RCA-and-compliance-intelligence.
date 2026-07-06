type MaintenanceEvidencePanelProps = {
  evidenceIds: string[];
  requiredProcedure: string;
  verificationMetric: string;
};

export default function MaintenanceEvidencePanel({
  evidenceIds,
  requiredProcedure,
  verificationMetric
}: MaintenanceEvidencePanelProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
          Evidence and Verification
        </p>

        <h3 className="mt-2 text-lg font-semibold text-slate-100">
          Supporting Maintenance Evidence
        </h3>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          Review the linked evidence, approved procedure and completion metric
          before closing the work order.
        </p>
      </div>

      <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950 p-4">
        <p className="text-xs uppercase tracking-wider text-slate-500">
          Required Procedure
        </p>

        <p className="mt-2 break-words text-sm font-medium text-cyan-300">
          {requiredProcedure}
        </p>
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between gap-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Linked Evidence
          </p>

          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-300">
            {evidenceIds.length}
          </span>
        </div>

        {evidenceIds.length > 0 ? (
          <div className="mt-3 space-y-2">
            {evidenceIds.map((evidenceId, index) => (
              <div
                key={evidenceId}
                className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-950 px-4 py-3"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-cyan-500/10 text-xs font-semibold text-cyan-300">
                  {index + 1}
                </span>

                <span className="break-all text-sm font-medium text-slate-300">
                  {evidenceId}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-3 rounded-xl border border-dashed border-slate-700 bg-slate-950 px-4 py-8 text-center">
            <p className="text-sm text-slate-500">
              No supporting evidence is linked to this work order.
            </p>
          </div>
        )}
      </div>

      <div className="mt-5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
        <p className="text-xs uppercase tracking-wider text-emerald-400">
          Verification Metric
        </p>

        <p className="mt-2 text-sm leading-6 text-emerald-100">
          {verificationMetric}
        </p>
      </div>
    </section>
  );
}