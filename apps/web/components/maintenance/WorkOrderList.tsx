"use client";

import type { MaintenanceWorkOrder } from "@/lib/types";
import WorkOrderCard from "./WorkOrderCard";

type WorkOrderListProps = {
  workOrders: MaintenanceWorkOrder[];
  selectedWorkOrderId?: string | null;
  onSelect: (workOrder: MaintenanceWorkOrder) => void;
  loading?: boolean;
};

function WorkOrderListSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, index) => (
        <div
          key={index}
          className="animate-pulse rounded-2xl border border-slate-800 bg-slate-950 p-5"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="h-4 w-32 rounded bg-slate-800" />
              <div className="mt-4 h-6 w-2/3 rounded bg-slate-800" />
              <div className="mt-3 h-4 w-full rounded bg-slate-800" />
              <div className="mt-2 h-4 w-4/5 rounded bg-slate-800" />
            </div>

            <div className="h-10 w-12 rounded bg-slate-800" />
          </div>

          <div className="mt-5 grid gap-3 border-t border-slate-800 pt-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, itemIndex) => (
              <div key={itemIndex}>
                <div className="h-3 w-20 rounded bg-slate-800" />
                <div className="mt-2 h-4 w-28 rounded bg-slate-800" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function WorkOrderList({
  workOrders,
  selectedWorkOrderId = null,
  onSelect,
  loading = false
}: WorkOrderListProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-100">
            Prioritized Work Orders
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Select a work order to review procedures, evidence and RCA links.
          </p>
        </div>

        <span className="rounded-full bg-slate-800 px-3 py-1 text-sm font-medium text-slate-300">
          {workOrders.length}
        </span>
      </div>

      <div className="mt-6">
        {loading ? (
          <WorkOrderListSkeleton />
        ) : workOrders.length > 0 ? (
          <div className="space-y-4">
            {workOrders.map((workOrder) => (
              <WorkOrderCard
                key={workOrder.work_order_id}
                workOrder={workOrder}
                selected={
                  selectedWorkOrderId === workOrder.work_order_id
                }
                onSelect={onSelect}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950 px-6 py-12 text-center">
            <p className="text-base font-medium text-slate-300">
              No work orders found
            </p>

            <p className="mt-2 text-sm text-slate-500">
              Adjust or clear the selected maintenance filters.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}