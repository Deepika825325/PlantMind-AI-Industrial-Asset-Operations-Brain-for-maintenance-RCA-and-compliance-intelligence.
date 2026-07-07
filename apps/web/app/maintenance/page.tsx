"use client";

import { useEffect, useState } from "react";
import MaintenanceFilters from "@/components/maintenance/MaintenanceFilters";
import MaintenanceKpiCards from "@/components/maintenance/MaintenanceKpiCards";
import WorkOrderDetail from "@/components/maintenance/WorkOrderDetail";
import WorkOrderList from "@/components/maintenance/WorkOrderList";
import { apiGet } from "@/lib/api";
import type {
  MaintenanceFilterState,
  MaintenanceStatistics,
  MaintenanceWorkOrder,
  MaintenanceWorkOrdersResponse
} from "@/lib/types";

const defaultFilters: MaintenanceFilterState = {
  assetId: "ALL",
  priority: "ALL",
  status: "ALL",
  maintenanceType: "ALL",
  rcaCaseId: "ALL",
  dueDate: ""
};

function buildWorkOrdersEndpoint(
  filters: MaintenanceFilterState
) {
  const parameters = new URLSearchParams();

  if (filters.assetId !== "ALL") {
    parameters.set("asset_id", filters.assetId);
  }

  if (filters.priority !== "ALL") {
    parameters.set("priority", filters.priority);
  }

  if (filters.status !== "ALL") {
    parameters.set("status", filters.status);
  }

  if (filters.maintenanceType !== "ALL") {
    parameters.set(
      "maintenance_type",
      filters.maintenanceType
    );
  }

  if (filters.rcaCaseId !== "ALL") {
    parameters.set(
      "rca_case_id",
      filters.rcaCaseId
    );
  }

  if (filters.dueDate) {
    parameters.set("due_date", filters.dueDate);
  }

  const queryString = parameters.toString();

  return queryString
    ? `/maintenance/work-orders?${queryString}`
    : "/maintenance/work-orders";
}

function updateRcaQueryParameter(rcaCaseId: string) {
  const url = new URL(window.location.href);

  if (rcaCaseId === "ALL") {
    url.searchParams.delete("rca");
  } else {
    url.searchParams.set("rca", rcaCaseId);
  }

  window.history.replaceState(
    {},
    "",
    `${url.pathname}${url.search}${url.hash}`
  );
}

export default function MaintenancePage() {
  const [filters, setFilters] =
    useState<MaintenanceFilterState>(defaultFilters);

  const [workOrders, setWorkOrders] = useState<
    MaintenanceWorkOrder[]
  >([]);

  const [statistics, setStatistics] =
    useState<MaintenanceStatistics | null>(null);

  const [
    selectedWorkOrderId,
    setSelectedWorkOrderId
  ] = useState<string | null>(null);

  const [selectedWorkOrder, setSelectedWorkOrder] =
    useState<MaintenanceWorkOrder | null>(null);

  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(true);
  const [statisticsLoading, setStatisticsLoading] =
    useState(true);

  const [error, setError] = useState("");

  useEffect(() => {
    const parameters = new URLSearchParams(
      window.location.search
    );

    const rcaCaseId = parameters.get("rca");

    if (rcaCaseId) {
      setFilters((currentFilters) => ({
        ...currentFilters,
        rcaCaseId
      }));
    }

    setInitialized(true);
  }, []);

  useEffect(() => {
    let active = true;

    async function loadStatistics() {
      try {
        setStatisticsLoading(true);

        const result =
          await apiGet<MaintenanceStatistics>(
            "/maintenance/work-orders/statistics"
          );

        if (active) {
          setStatistics(result);
        }
      } catch (requestError) {
        if (active) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : "Failed to load maintenance statistics"
          );
        }
      } finally {
        if (active) {
          setStatisticsLoading(false);
        }
      }
    }

    loadStatistics();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!initialized) {
      return;
    }

    let active = true;

    async function loadWorkOrders() {
      try {
        setLoading(true);
        setError("");

        const endpoint =
          buildWorkOrdersEndpoint(filters);

        const result =
          await apiGet<MaintenanceWorkOrdersResponse>(
            endpoint
          );

        if (!active) {
          return;
        }

        setWorkOrders(result.work_orders);

        setSelectedWorkOrderId(
          (currentWorkOrderId) => {
            if (currentWorkOrderId) {
              const matchingWorkOrder =
                result.work_orders.find(
                  (workOrder) =>
                    workOrder.work_order_id ===
                    currentWorkOrderId
                );

              if (matchingWorkOrder) {
                return currentWorkOrderId;
              }
            }

            return (
              result.work_orders[0]
                ?.work_order_id ?? null
            );
          }
        );
      } catch (requestError) {
        if (active) {
          setWorkOrders([]);
          setSelectedWorkOrder(null);

          setError(
            requestError instanceof Error
              ? requestError.message
              : "Failed to load maintenance work orders"
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadWorkOrders();

    return () => {
      active = false;
    };
  }, [filters, initialized]);

  useEffect(() => {
    if (!selectedWorkOrderId) {
      setSelectedWorkOrder(null);
      return;
    }

    const workOrderId =
      selectedWorkOrderId;

    let active = true;

    async function loadWorkOrderDetail() {
      try {
        setError("");
        setSelectedWorkOrder(null);

        const result =
          await apiGet<MaintenanceWorkOrder>(
            `/maintenance/work-orders/${encodeURIComponent(
              workOrderId
            )}`
          );

        if (active) {
          setSelectedWorkOrder(result);
        }
      } catch (requestError) {
        if (active) {
          setSelectedWorkOrder(null);

          setError(
            requestError instanceof Error
              ? requestError.message
              : "Failed to load work order details"
          );
        }
      }
    }

    loadWorkOrderDetail();

    return () => {
      active = false;
    };
  }, [selectedWorkOrderId]);

  function handleFilterChange(
    field: keyof MaintenanceFilterState,
    value: string
  ) {
    setFilters((currentFilters) => ({
      ...currentFilters,
      [field]: value
    }));

    if (field === "rcaCaseId") {
      updateRcaQueryParameter(value);
    }
  }

  function handleResetFilters() {
    setFilters(defaultFilters);
    updateRcaQueryParameter("ALL");
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-[1600px] px-6 py-10">
        <header className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
              Maintenance Command Center
            </p>

            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-slate-100">
              Prioritized Maintenance Work Orders
            </h1>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Convert root-cause findings, inspection evidence
              and asset risks into controlled maintenance actions
              with procedures, ownership and verification criteria.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 px-5 py-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Active Portfolio
            </p>

            <p className="mt-2 text-lg font-semibold text-slate-200">
              P-101 · C-201 · HX-301
            </p>
          </div>
        </header>

        <div className="mt-8">
          <MaintenanceKpiCards
            statistics={statistics}
            loading={statisticsLoading}
          />
        </div>

        <div className="mt-8">
          <MaintenanceFilters
            filters={filters}
            onChange={handleFilterChange}
            onReset={handleResetFilters}
            rcaCaseOptions={["RCA-P101-001"]}
            resultCount={workOrders.length}
          />
        </div>

        {filters.rcaCaseId !== "ALL" && (
          <div className="mt-6 rounded-2xl border border-violet-500/20 bg-violet-500/5 px-5 py-4">
            <p className="text-sm text-violet-200">
              Showing maintenance work orders linked to{" "}
              <span className="font-semibold">
                {filters.rcaCaseId}
              </span>
              .
            </p>
          </div>
        )}

        {error && (
          <div className="mt-6 rounded-2xl border border-red-500/30 bg-red-500/10 p-5">
            <p className="font-medium text-red-300">
              Maintenance data could not be loaded
            </p>

            <p className="mt-2 text-sm text-red-200/80">
              {error}
            </p>
          </div>
        )}

        <div className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(420px,0.65fr)]">
          <WorkOrderList
            workOrders={workOrders}
            selectedWorkOrderId={
              selectedWorkOrderId ?? undefined
            }
            onSelect={(workOrder) =>
              setSelectedWorkOrderId(
                workOrder.work_order_id
              )
            }
            loading={!initialized || loading}
          />

          <div className="xl:sticky xl:top-6 xl:self-start">
            <WorkOrderDetail
              workOrder={selectedWorkOrder}
              onClose={() => {
                setSelectedWorkOrderId(null);
                setSelectedWorkOrder(null);
              }}
            />
          </div>
        </div>
      </section>
    </main>
  );
}