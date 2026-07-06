"use client";

import type {
  MaintenanceFilterState
} from "@/lib/types";

type MaintenanceFiltersProps = {
  filters: MaintenanceFilterState;
  onChange: (
    field: keyof MaintenanceFilterState,
    value: string
  ) => void;
  onReset: () => void;
  rcaCaseOptions?: string[];
  resultCount?: number;
};

const assetOptions = [
  "P-101",
  "C-201",
  "HX-301"
];

const priorityOptions = [
  "Critical",
  "High",
  "Medium",
  "Low"
];

const statusOptions = [
  "Open",
  "Delayed",
  "In Progress",
  "Planned",
  "Completed",
  "Cancelled"
];

const maintenanceTypeOptions = [
  "Corrective",
  "Condition-Based",
  "Verification",
  "Predictive",
  "Preventive"
];

const selectClassName =
  "mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-cyan-400";

export default function MaintenanceFilters({
  filters,
  onChange,
  onReset,
  rcaCaseOptions = ["RCA-P101-001"],
  resultCount
}: MaintenanceFiltersProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">
            Maintenance Filters
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Narrow work orders by asset, execution state, source RCA and due date.
          </p>
        </div>

        <div className="flex items-center gap-4">
          {typeof resultCount === "number" && (
            <span className="text-sm text-slate-400">
              {resultCount} work orders
            </span>
          )}

          <button
            type="button"
            onClick={onReset}
            className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-slate-100"
          >
            Clear filters
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div>
          <label
            htmlFor="maintenance-asset"
            className="text-sm font-medium text-slate-400"
          >
            Asset
          </label>

          <select
            id="maintenance-asset"
            value={filters.assetId}
            onChange={(event) =>
              onChange("assetId", event.target.value)
            }
            className={selectClassName}
          >
            <option value="ALL">All assets</option>

            {assetOptions.map((assetId) => (
              <option key={assetId} value={assetId}>
                {assetId}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="maintenance-priority"
            className="text-sm font-medium text-slate-400"
          >
            Priority
          </label>

          <select
            id="maintenance-priority"
            value={filters.priority}
            onChange={(event) =>
              onChange("priority", event.target.value)
            }
            className={selectClassName}
          >
            <option value="ALL">All priorities</option>

            {priorityOptions.map((priority) => (
              <option key={priority} value={priority}>
                {priority}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="maintenance-status"
            className="text-sm font-medium text-slate-400"
          >
            Status
          </label>

          <select
            id="maintenance-status"
            value={filters.status}
            onChange={(event) =>
              onChange("status", event.target.value)
            }
            className={selectClassName}
          >
            <option value="ALL">All statuses</option>

            {statusOptions.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="maintenance-type"
            className="text-sm font-medium text-slate-400"
          >
            Maintenance type
          </label>

          <select
            id="maintenance-type"
            value={filters.maintenanceType}
            onChange={(event) =>
              onChange(
                "maintenanceType",
                event.target.value
              )
            }
            className={selectClassName}
          >
            <option value="ALL">
              All maintenance types
            </option>

            {maintenanceTypeOptions.map(
              (maintenanceType) => (
                <option
                  key={maintenanceType}
                  value={maintenanceType}
                >
                  {maintenanceType}
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="maintenance-rca"
            className="text-sm font-medium text-slate-400"
          >
            RCA case
          </label>

          <select
            id="maintenance-rca"
            value={filters.rcaCaseId}
            onChange={(event) =>
              onChange("rcaCaseId", event.target.value)
            }
            className={selectClassName}
          >
            <option value="ALL">All RCA cases</option>

            {rcaCaseOptions.map((caseId) => (
              <option key={caseId} value={caseId}>
                {caseId}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="maintenance-due-date"
            className="text-sm font-medium text-slate-400"
          >
            Due date
          </label>

          <input
            id="maintenance-due-date"
            type="date"
            value={filters.dueDate}
            onChange={(event) =>
              onChange("dueDate", event.target.value)
            }
            className={selectClassName}
          />
        </div>
      </div>
    </section>
  );
}