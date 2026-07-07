"use client";

import type { MaintenanceWorkOrder } from "@/lib/types";
import DecisionTracePanel from "@/components/trust/DecisionTracePanel";
import LinkedRcaPanel from "./LinkedRcaPanel";
import MaintenanceEvidencePanel from "./MaintenanceEvidencePanel";

type WorkOrderDetailProps = {
  workOrder: MaintenanceWorkOrder | null;
  onClose?: () => void;
};

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function getPriorityClass(priority: string) {
  if (priority === "Critical") {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  if (priority === "High") {
    return "border-orange-500/30 bg-orange-500/10 text-orange-300";
  }

  if (priority === "Medium") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
}

function getStatusClass(status: string) {
  if (status === "Open") {
    return "bg-cyan-500/10 text-cyan-300";
  }

  if (status === "Delayed") {
    return "bg-red-500/10 text-red-300";
  }

  if (status === "In Progress") {
    return "bg-violet-500/10 text-violet-300";
  }

  if (status === "Planned") {
    return "bg-blue-500/10 text-blue-300";
  }

  if (status === "Completed") {
    return "bg-emerald-500/10 text-emerald-300";
  }

  return "bg-slate-800 text-slate-300";
}

export default function WorkOrderDetail({
  workOrder,
  onClose
}: WorkOrderDetailProps) {
  if (!workOrder) {
    return (
      <aside className="rounded-2xl border border-dashed border-slate-700 bg-slate-900 p-8">
        <div className="flex min-h-72 flex-col items-center justify-center text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800 text-xl text-slate-400">
            WO
          </div>

          <h2 className="mt-5 text-lg font-semibold text-slate-200">
            Select a work order
          </h2>

          <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
            Choose a work order to review its procedure, safety requirements,
            parts, evidence and linked RCA findings.
          </p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="space-y-5">
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
              {workOrder.work_order_id}
            </p>

            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-100">
              {workOrder.title}
            </h2>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              {workOrder.description}
            </p>
          </div>

          {onClose && (
            <button
              type="button"
              onClick={onClose}
              aria-label="Close work order details"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-slate-700 text-lg text-slate-400 transition hover:border-slate-500 hover:text-slate-100"
            >
              ×
            </button>
          )}
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-300">
            {workOrder.asset_id}
          </span>

          <span
            className={`rounded-full border px-3 py-1 text-xs font-medium ${getPriorityClass(
              workOrder.priority
            )}`}
          >
            {workOrder.priority}
          </span>

          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${getStatusClass(
              workOrder.status
            )}`}
          >
            {workOrder.status}
          </span>

          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-300">
            {workOrder.maintenance_type}
          </span>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Owner
            </p>

            <p className="mt-2 text-sm font-medium text-slate-200">
              {workOrder.owner_role}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Estimated Duration
            </p>

            <p className="mt-2 text-sm font-medium text-slate-200">
              {workOrder.estimated_duration_hours} hours
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Created
            </p>

            <p className="mt-2 text-sm font-medium text-slate-200">
              {formatDateTime(workOrder.created_at)}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Due
            </p>

            <p className="mt-2 text-sm font-medium text-slate-200">
              {formatDateTime(workOrder.due_at)}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-orange-500/20 bg-orange-500/5 p-4">
            <p className="text-xs uppercase tracking-wider text-orange-400">
              Risk Score
            </p>

            <p className="mt-2 text-3xl font-semibold text-orange-200">
              {workOrder.risk_score}
            </p>
          </div>

          <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
            <p className="text-xs uppercase tracking-wider text-cyan-400">
              Confidence
            </p>

            <p className="mt-2 text-3xl font-semibold text-cyan-200">
              {Math.round(workOrder.confidence * 100)}%
            </p>
          </div>
        </div>
      </section>

      {workOrder.decision_trace && (
        <DecisionTracePanel
          trace={workOrder.decision_trace}
          title="Maintenance Decision Trace"
        />
      )}

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-400">
          Safety Requirements
        </p>

        <div className="mt-4 space-y-2">
          {workOrder.safety_requirements.map((requirement, index) => (
            <div
              key={`${requirement}-${index}`}
              className="flex items-start gap-3 rounded-xl border border-slate-800 bg-slate-950 px-4 py-3"
            >
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-amber-500/10 text-xs font-semibold text-amber-300">
                {index + 1}
              </span>

              <p className="text-sm leading-6 text-slate-300">
                {requirement}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-400">
          Parts and Equipment
        </p>

        {workOrder.parts_required.length > 0 ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {workOrder.parts_required.map((part) => (
              <span
                key={part}
                className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-3 py-2 text-sm text-emerald-200"
              >
                {part}
              </span>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-slate-500">
            No parts are currently required.
          </p>
        )}
      </section>

      <LinkedRcaPanel
        rcaCaseId={workOrder.linked_rca_case_id}
        rootCauseIds={workOrder.linked_root_cause_ids}
        sourceType={workOrder.source_type}
        sourceId={workOrder.source_id}
      />

      <MaintenanceEvidencePanel
        evidenceIds={workOrder.linked_evidence_ids}
        requiredProcedure={workOrder.required_procedure}
        verificationMetric={workOrder.verification_metric}
      />

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          Completion Notes
        </p>

        <p className="mt-3 text-sm leading-6 text-slate-300">
          {workOrder.completion_notes ??
            "No completion notes have been recorded."}
        </p>
      </section>
    </aside>
  );
}