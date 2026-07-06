"use client";

import type { MaintenanceWorkOrder } from "@/lib/types";

type WorkOrderCardProps = {
  workOrder: MaintenanceWorkOrder;
  selected?: boolean;
  onSelect: (workOrder: MaintenanceWorkOrder) => void;
};

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

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(new Date(value));
}

export default function WorkOrderCard({
  workOrder,
  selected = false,
  onSelect
}: WorkOrderCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(workOrder)}
      className={`w-full rounded-2xl border p-5 text-left transition ${
        selected
          ? "border-cyan-400 bg-cyan-400/5 shadow-lg shadow-cyan-950/30"
          : "border-slate-800 bg-slate-950 hover:border-slate-700 hover:bg-slate-900"
      }`}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">
              {workOrder.work_order_id}
            </span>

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
          </div>

          <h3 className="mt-4 text-lg font-semibold text-slate-100">
            {workOrder.title}
          </h3>

          <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-400">
            {workOrder.description}
          </p>
        </div>

        <div className="shrink-0 text-left sm:text-right">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Risk score
          </p>

          <p className="mt-1 text-2xl font-semibold text-orange-300">
            {workOrder.risk_score}
          </p>
        </div>
      </div>

      <div className="mt-5 grid gap-3 border-t border-slate-800 pt-4 sm:grid-cols-2 xl:grid-cols-4">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Maintenance type
          </p>

          <p className="mt-1 text-sm text-slate-300">
            {workOrder.maintenance_type}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Owner
          </p>

          <p className="mt-1 text-sm text-slate-300">
            {workOrder.owner_role}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Due date
          </p>

          <p className="mt-1 text-sm text-slate-300">
            {formatDate(workOrder.due_at)}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Confidence
          </p>

          <p className="mt-1 text-sm text-slate-300">
            {Math.round(workOrder.confidence * 100)}%
          </p>
        </div>
      </div>

      {workOrder.linked_rca_case_id && (
        <div className="mt-4 rounded-xl border border-violet-500/20 bg-violet-500/5 px-4 py-3">
          <p className="text-xs font-medium text-violet-300">
            Linked RCA: {workOrder.linked_rca_case_id}
          </p>
        </div>
      )}
    </button>
  );
}