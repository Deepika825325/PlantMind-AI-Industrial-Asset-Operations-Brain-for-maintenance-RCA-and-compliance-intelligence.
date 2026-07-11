"use client";

import { useMemo, useState } from "react";

import { apiPost } from "@/lib/api";

type WorkOrderLifecycleStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "assigned"
  | "in_progress"
  | "waiting_for_part"
  | "completed"
  | "verification_pending"
  | "verified"
  | "closed";

type LifecycleAuditEventType =
  | "transition"
  | "transition_rejected"
  | "approval_required";

type WorkOrderTransitionRequest = {
  target_status: WorkOrderLifecycleStatus;
  changed_by: string;
  changed_at: string;
  note?: string | null;
  approver_role?: string | null;
  approval_reference?: string | null;
};

type WorkOrderLifecycleAuditEvent = {
  event_id: string;
  work_order_id: string;
  event_type: LifecycleAuditEventType;
  timestamp: string;
  from_status: WorkOrderLifecycleStatus;
  to_status: WorkOrderLifecycleStatus;
  changed_by: string;
  note?: string | null;
  approval_reference?: string | null;
  approver_role?: string | null;
  explanation: string;
};

type WorkOrderLifecycleState = {
  work_order_id: string;
  asset_id: string;
  title: string;
  priority: string;
  risk_score: number;
  high_risk: boolean;
  approval_required: boolean;
  current_status: WorkOrderLifecycleStatus;
  allowed_next_statuses: WorkOrderLifecycleStatus[];
  audit_events: WorkOrderLifecycleAuditEvent[];
};

type WorkOrderTransitionResponse = {
  work_order_id: string;
  previous_status: WorkOrderLifecycleStatus;
  current_status: WorkOrderLifecycleStatus;
  high_risk: boolean;
  approval_required: boolean;
  audit_event: WorkOrderLifecycleAuditEvent;
  allowed_next_statuses: WorkOrderLifecycleStatus[];
  explanation: string;
};

const lifecycleOrder: WorkOrderLifecycleStatus[] = [
  "draft",
  "pending_approval",
  "approved",
  "assigned",
  "in_progress",
  "waiting_for_part",
  "completed",
  "verification_pending",
  "verified",
  "closed",
];

function label(value: string): string {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function fallbackState(): WorkOrderLifecycleState {
  return {
    work_order_id: "WO-P101-HIGH-001",
    asset_id: "P-101",
    title: "Inspect and relubricate drive-end bearing",
    priority: "critical",
    risk_score: 92,
    high_risk: true,
    approval_required: true,
    current_status: "draft",
    allowed_next_statuses: ["pending_approval"],
    audit_events: [
      {
        event_id: "WO-AUDIT-DEMO-001",
        work_order_id: "WO-P101-HIGH-001",
        event_type: "transition",
        timestamp: "2026-07-10T09:00:00+00:00",
        from_status: "draft",
        to_status: "pending_approval",
        changed_by: "maintenance.engineer",
        note: "Submitted high-risk bearing work order for approval.",
        explanation:
          "High-risk work order entered pending approval. Manager approval is required before Approved.",
      },
      {
        event_id: "WO-AUDIT-DEMO-002",
        work_order_id: "WO-P101-HIGH-001",
        event_type: "transition_rejected",
        timestamp: "2026-07-10T09:01:00+00:00",
        from_status: "pending_approval",
        to_status: "approved",
        changed_by: "maintenance.engineer",
        note: "Attempted approval without approval reference.",
        explanation:
          "Rejected: high-risk work order requires approval_reference and approver_role before it can move to Approved.",
      },
      {
        event_id: "WO-AUDIT-DEMO-003",
        work_order_id: "WO-P101-HIGH-001",
        event_type: "transition",
        timestamp: "2026-07-10T09:02:00+00:00",
        from_status: "pending_approval",
        to_status: "approved",
        changed_by: "maintenance.engineer",
        approval_reference: "APP-P101-001",
        approver_role: "maintenance_manager",
        note: "Approved by maintenance manager.",
        explanation:
          "Approved transition accepted because approval reference and approver role were supplied.",
      },
    ],
  };
}

function completedAuditPreview(): WorkOrderLifecycleAuditEvent[] {
  return [
    {
      event_id: "WO-AUDIT-COMPLETE-001",
      work_order_id: "WO-P101-COMPLETE-001",
      event_type: "transition_rejected",
      timestamp: "2026-07-10T09:00:00+00:00",
      from_status: "completed",
      to_status: "closed",
      changed_by: "maintenance.engineer",
      note: "Invalid direct close.",
      explanation:
        "Invalid transition: completed cannot directly become closed. Move to Verification Pending, then Verified, then Closed.",
    },
    {
      event_id: "WO-AUDIT-COMPLETE-002",
      work_order_id: "WO-P101-COMPLETE-001",
      event_type: "transition",
      timestamp: "2026-07-10T09:01:00+00:00",
      from_status: "completed",
      to_status: "verification_pending",
      changed_by: "maintenance.engineer",
      explanation:
        "Completed work order moved to Verification Pending for post-maintenance verification.",
    },
    {
      event_id: "WO-AUDIT-COMPLETE-003",
      work_order_id: "WO-P101-COMPLETE-001",
      event_type: "transition",
      timestamp: "2026-07-10T09:02:00+00:00",
      from_status: "verification_pending",
      to_status: "verified",
      changed_by: "maintenance.engineer",
      explanation:
        "Verification evidence accepted. Work order moved to Verified.",
    },
    {
      event_id: "WO-AUDIT-COMPLETE-004",
      work_order_id: "WO-P101-COMPLETE-001",
      event_type: "transition",
      timestamp: "2026-07-10T09:03:00+00:00",
      from_status: "verified",
      to_status: "closed",
      changed_by: "maintenance.engineer",
      explanation:
        "Verified work order closed through governed lifecycle path.",
    },
  ];
}

export function GovernedWorkOrderLifecyclePanel() {
  const [state, setState] = useState<WorkOrderLifecycleState>(() =>
    fallbackState(),
  );
  const [completedPreview] = useState<WorkOrderLifecycleAuditEvent[]>(() =>
    completedAuditPreview(),
  );
  const [status, setStatus] = useState(
    "Using local governed lifecycle preview.",
  );

  const currentIndex = useMemo(() => {
    return lifecycleOrder.indexOf(state.current_status);
  }, [state.current_status]);

  async function runBackendApprovalDemo() {
    setStatus("Running governed lifecycle approval demo through backend...");

    try {
      const pending = await apiPost<
        WorkOrderTransitionRequest,
        WorkOrderTransitionResponse
      >("/maintenance/work-orders/WO-P101-001/lifecycle/transition", {
        target_status: "pending_approval",
        changed_by: "maintenance.engineer",
        changed_at: new Date().toISOString(),
        note: "Submit high-risk P-101 work order for approval.",
      });

      let rejectedAudit: WorkOrderLifecycleAuditEvent | null = null;

      try {
        await apiPost<WorkOrderTransitionRequest, WorkOrderTransitionResponse>(
          "/maintenance/work-orders/WO-P101-001/lifecycle/transition",
          {
            target_status: "approved",
            changed_by: "maintenance.engineer",
            changed_at: new Date().toISOString(),
            note: "Attempt approval without approval reference.",
          },
        );
      } catch {
        rejectedAudit = {
          event_id: "WO-AUDIT-UI-REJECTED",
          work_order_id: "WO-P101-001",
          event_type: "transition_rejected",
          timestamp: new Date().toISOString(),
          from_status: "pending_approval",
          to_status: "approved",
          changed_by: "maintenance.engineer",
          note: "Attempt approval without approval reference.",
          explanation:
            "Rejected by backend: high-risk work order requires approval_reference and approver_role.",
        };
      }

      const approved = await apiPost<
        WorkOrderTransitionRequest,
        WorkOrderTransitionResponse
      >("/maintenance/work-orders/WO-P101-001/lifecycle/transition", {
        target_status: "approved",
        changed_by: "maintenance.engineer",
        changed_at: new Date().toISOString(),
        note: "Approved by maintenance manager.",
        approval_reference: "APP-P101-001",
        approver_role: "maintenance_manager",
      });

      setState({
        work_order_id: approved.work_order_id,
        asset_id: "P-101",
        title: "Inspect and relubricate drive-end bearing",
        priority: "critical",
        risk_score: 92,
        high_risk: approved.high_risk,
        approval_required: approved.approval_required,
        current_status: approved.current_status,
        allowed_next_statuses: approved.allowed_next_statuses,
        audit_events: [
          pending.audit_event,
          ...(rejectedAudit ? [rejectedAudit] : []),
          approved.audit_event,
        ],
      });

      setStatus("Backend approval demo completed successfully.");
    } catch {
      setState(fallbackState());
      setStatus(
        "Backend unavailable or demo work order already moved. Showing local governed lifecycle preview.",
      );
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Governed work-order lifecycle
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">
              Maintenance approval and transition control
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              This extends existing maintenance work orders with governed
              lifecycle validation. Invalid transitions return conflict errors,
              high-risk work requires approval, and every accepted or rejected
              transition creates an audit event.
            </p>
          </div>

          <button
            type="button"
            onClick={runBackendApprovalDemo}
            className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
          >
            Run approval demo
          </button>
        </div>

        <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          {status}
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Work order
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            {state.title}
          </h2>

          <div className="mt-6 grid gap-3 text-sm text-slate-700">
            <p>
              <span className="font-semibold">Work order:</span>{" "}
              {state.work_order_id}
            </p>
            <p>
              <span className="font-semibold">Asset:</span> {state.asset_id}
            </p>
            <p>
              <span className="font-semibold">Priority:</span>{" "}
              {label(state.priority)}
            </p>
            <p>
              <span className="font-semibold">Risk score:</span>{" "}
              {state.risk_score}
            </p>
            <p>
              <span className="font-semibold">High risk:</span>{" "}
              {state.high_risk ? "Yes" : "No"}
            </p>
            <p>
              <span className="font-semibold">Approval required:</span>{" "}
              {state.approval_required ? "Yes" : "No"}
            </p>
            <p>
              <span className="font-semibold">Current status:</span>{" "}
              {label(state.current_status)}
            </p>
          </div>

          <div className="mt-6 rounded-xl bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-950">
              Allowed next statuses
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {state.allowed_next_statuses.length > 0 ? (
                state.allowed_next_statuses.map((nextStatus) => (
                  <span
                    key={nextStatus}
                    className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 shadow-sm"
                  >
                    {label(nextStatus)}
                  </span>
                ))
              ) : (
                <span className="text-sm text-slate-500">No next status</span>
              )}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Lifecycle path
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Draft to closed with validation gates
          </h2>

          <div className="mt-6 grid gap-3 md:grid-cols-2">
            {lifecycleOrder.map((statusName, index) => (
              <div
                key={statusName}
                className={`rounded-xl border p-4 ${
                  index <= currentIndex
                    ? "border-slate-300 bg-slate-50"
                    : "border-slate-200 bg-white"
                }`}
              >
                <p className="text-sm font-semibold text-slate-950">
                  {index + 1}. {label(statusName)}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {index === currentIndex
                    ? "Current state"
                    : index < currentIndex
                      ? "Completed"
                      : "Pending"}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            High-risk approval audit
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Approval required before Approved
          </h2>

          <div className="mt-6 space-y-4">
            {state.audit_events.map((event) => (
              <div
                key={event.event_id}
                className="rounded-xl border border-slate-200 p-4"
              >
                <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <p className="font-semibold text-slate-950">
                    {label(event.from_status)} → {label(event.to_status)}
                  </p>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                    {label(event.event_type)}
                  </span>
                </div>

                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {event.explanation}
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  {event.event_id} · {event.changed_by}
                  {event.approval_reference
                    ? ` · Approval: ${event.approval_reference}`
                    : ""}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Closure validation
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Completed cannot directly become Closed
          </h2>

          <div className="mt-6 space-y-4">
            {completedPreview.map((event) => (
              <div
                key={event.event_id}
                className="rounded-xl border border-slate-200 p-4"
              >
                <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <p className="font-semibold text-slate-950">
                    {label(event.from_status)} → {label(event.to_status)}
                  </p>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                    {label(event.event_type)}
                  </span>
                </div>

                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {event.explanation}
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  {event.event_id}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}