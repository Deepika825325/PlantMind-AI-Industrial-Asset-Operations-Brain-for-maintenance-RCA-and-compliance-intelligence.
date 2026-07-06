import type {
  ComplianceFilterState,
  ComplianceRuleDefinition,
} from "@/lib/types";

type ComplianceFiltersProps = {
  filters: ComplianceFilterState;
  assetIds: string[];
  rules: ComplianceRuleDefinition[];
  onChange: (filters: ComplianceFilterState) => void;
  onReset: () => void;
};

export default function ComplianceFilters({
  filters,
  assetIds,
  rules,
  onChange,
  onReset,
}: ComplianceFiltersProps) {
  function updateFilter(
    key: keyof ComplianceFilterState,
    value: string
  ) {
    onChange({
      ...filters,
      [key]: value,
    });
  }

  const fieldClass =
    "mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-cyan-400";

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-100">
            Compliance Filters
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Filter gaps, evidence and audit packages.
          </p>
        </div>

        <button
          type="button"
          onClick={onReset}
          className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-cyan-500 hover:text-cyan-300"
        >
          Reset filters
        </button>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <label className="text-sm text-slate-400">
          Asset
          <select
            value={filters.assetId}
            onChange={(event) =>
              updateFilter("assetId", event.target.value)
            }
            className={fieldClass}
          >
            <option value="ALL">All assets</option>

            {assetIds.map((assetId) => (
              <option key={assetId} value={assetId}>
                {assetId}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-slate-400">
          Severity
          <select
            value={filters.severity}
            onChange={(event) =>
              updateFilter("severity", event.target.value)
            }
            className={fieldClass}
          >
            <option value="ALL">All severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </label>

        <label className="text-sm text-slate-400">
          Status
          <select
            value={filters.status}
            onChange={(event) =>
              updateFilter("status", event.target.value)
            }
            className={fieldClass}
          >
            <option value="ALL">All statuses</option>
            <option value="Open">Open</option>
            <option value="Resolved">Resolved</option>
            <option value="Waived">Waived</option>
          </select>
        </label>

        <label className="text-sm text-slate-400">
          Rule
          <select
            value={filters.ruleId}
            onChange={(event) =>
              updateFilter("ruleId", event.target.value)
            }
            className={fieldClass}
          >
            <option value="ALL">All rules</option>

            {rules.map((rule) => (
              <option
                key={rule.rule_id}
                value={rule.rule_id}
              >
                {rule.rule_id} — {rule.rule_name}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-slate-400">
          Evidence availability
          <select
            value={filters.evidenceAvailability}
            onChange={(event) =>
              updateFilter(
                "evidenceAvailability",
                event.target.value
              )
            }
            className={fieldClass}
          >
            <option value="ALL">All evidence states</option>
            <option value="MISSING">
              No available evidence
            </option>
            <option value="PARTIAL">
              Partial evidence
            </option>
          </select>
        </label>

        <label className="text-sm text-slate-400">
          Audit package
          <select
            value={filters.auditPackage}
            onChange={(event) =>
              updateFilter(
                "auditPackage",
                event.target.value
              )
            }
            className={fieldClass}
          >
            <option value="ALL">All packages</option>
            <option value="WITH_GAPS">
              Packages with open gaps
            </option>
            <option value="READY">
              Audit-ready packages
            </option>
          </select>
        </label>
      </div>
    </section>
  );
}