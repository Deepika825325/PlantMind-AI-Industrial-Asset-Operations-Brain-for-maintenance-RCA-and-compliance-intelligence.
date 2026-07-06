import Link from "next/link";

import type {
  ComplianceAuditPackage,
} from "@/lib/types";

type EvidencePackageViewProps = {
  auditPackage: ComplianceAuditPackage;
};

export default function EvidencePackageView({
  auditPackage,
}: EvidencePackageViewProps) {
  const assetId = auditPackage.asset.asset_id;

  const linkedWorkOrderIds = Array.from(
    new Set(
      auditPackage.open_gaps.flatMap(
        (gap) => gap.linked_work_order_ids
      )
    )
  );

  const linkedRcaCaseIds = Array.from(
    new Set(
      auditPackage.open_gaps.flatMap(
        (gap) => gap.linked_rca_case_ids
      )
    )
  );

  const missingEvidence = Array.from(
    new Set(
      auditPackage.open_gaps.flatMap(
        (gap) => gap.missing_evidence
      )
    )
  );

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-cyan-400">
            Evidence Package
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            {assetId} Audit Package
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            Consolidated rules, evidence, inspections, work orders,
            RCA cases and remediation actions for audit review.
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 px-5 py-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Audit Score
          </p>

          <p className="mt-2 text-3xl font-semibold text-cyan-300">
            {auditPackage.audit_readiness_score}/100
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-sm text-slate-400">
            Applicable Rules
          </p>

          <p className="mt-2 text-2xl font-semibold text-slate-100">
            {auditPackage.applicable_rules.length}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-sm text-slate-400">
            Passed Rules
          </p>

          <p className="mt-2 text-2xl font-semibold text-emerald-300">
            {auditPackage.passed_rules.length}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-sm text-slate-400">
            Failed Rules
          </p>

          <p className="mt-2 text-2xl font-semibold text-red-300">
            {auditPackage.failed_rules.length}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-sm text-slate-400">
            Evidence Documents
          </p>

          <p className="mt-2 text-2xl font-semibold text-amber-300">
            {auditPackage.evidence_documents.length}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <section className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <h3 className="text-lg font-semibold text-slate-100">
            Evidence Documents
          </h3>

          <div className="mt-4 space-y-3">
            {auditPackage.evidence_documents.length > 0 ? (
              auditPackage.evidence_documents.map(
                (document) => (
                  <article
                    key={document.document_id}
                    className="rounded-xl border border-slate-800 bg-slate-900 p-4"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                        {document.document_id}
                      </span>

                      <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                        {document.document_type}
                      </span>
                    </div>

                    <p className="mt-3 font-medium text-slate-100">
                      {document.title}
                    </p>

                    <p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-400">
                      {document.summary}
                    </p>
                  </article>
                )
              )
            ) : (
              <p className="text-sm text-slate-500">
                No evidence documents are linked.
              </p>
            )}
          </div>
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <h3 className="text-lg font-semibold text-slate-100">
            Related Inspections
          </h3>

          <div className="mt-4 space-y-3">
            {auditPackage.related_inspections.length > 0 ? (
              auditPackage.related_inspections.map(
                (inspection) => (
                  <article
                    key={inspection.document_id}
                    className="rounded-xl border border-slate-800 bg-slate-900 p-4"
                  >
                    <p className="text-xs uppercase tracking-wider text-slate-500">
                      {inspection.document_id}
                    </p>

                    <p className="mt-2 font-medium text-slate-100">
                      {inspection.title}
                    </p>

                    <p className="mt-2 text-sm text-slate-400">
                      {inspection.document_type}
                    </p>
                  </article>
                )
              )
            ) : (
              <p className="text-sm text-slate-500">
                No related inspections are available.
              </p>
            )}
          </div>
        </section>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <section className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <h3 className="font-semibold text-slate-100">
            Missing Evidence
          </h3>

          <ul className="mt-4 space-y-2">
            {missingEvidence.length > 0 ? (
              missingEvidence.map((evidence) => (
                <li
                  key={evidence}
                  className="text-sm leading-6 text-red-300"
                >
                  {evidence}
                </li>
              ))
            ) : (
              <li className="text-sm text-emerald-300">
                No evidence is missing.
              </li>
            )}
          </ul>
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <h3 className="font-semibold text-slate-100">
            Linked Work Orders
          </h3>

          <div className="mt-4 flex flex-wrap gap-2">
            {linkedWorkOrderIds.length > 0 ? (
              linkedWorkOrderIds.map((workOrderId) => (
                <Link
                  key={workOrderId}
                  href={`/maintenance?asset=${encodeURIComponent(
                    assetId
                  )}`}
                  className="rounded-lg border border-cyan-500/20 bg-cyan-500/10 px-3 py-2 text-xs font-medium text-cyan-300 transition hover:border-cyan-400"
                >
                  {workOrderId}
                </Link>
              ))
            ) : (
              <p className="text-sm text-slate-500">
                No linked work orders.
              </p>
            )}
          </div>
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <h3 className="font-semibold text-slate-100">
            Linked RCA Cases
          </h3>

          <div className="mt-4 flex flex-wrap gap-2">
            {linkedRcaCaseIds.length > 0 ? (
              linkedRcaCaseIds.map((caseId) => (
                <Link
                  key={caseId}
                  href={`/rca?case=${encodeURIComponent(caseId)}`}
                  className="rounded-lg border border-cyan-500/20 bg-cyan-500/10 px-3 py-2 text-xs font-medium text-cyan-300 transition hover:border-cyan-400"
                >
                  {caseId}
                </Link>
              ))
            ) : (
              <p className="text-sm text-slate-500">
                No linked RCA cases.
              </p>
            )}
          </div>
        </section>
      </div>

      <section className="mt-6 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-5">
        <h3 className="font-semibold text-cyan-300">
          Recommended Remediation
        </h3>

        <ol className="mt-4 space-y-3">
          {auditPackage.recommended_actions.map(
            (action, index) => (
              <li
                key={action}
                className="flex gap-3 text-sm leading-6 text-slate-300"
              >
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-cyan-500/10 text-xs font-semibold text-cyan-300">
                  {index + 1}
                </span>

                <span>{action}</span>
              </li>
            )
          )}
        </ol>
      </section>
    </section>
  );
}