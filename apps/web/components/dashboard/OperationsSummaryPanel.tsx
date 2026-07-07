import Link from "next/link";

import EmptyState from "@/components/system/EmptyState";

import type {
  OperationsSummary,
} from "@/lib/types";


type OperationsSummaryPanelProps = {
  data: OperationsSummary;
};


function getSeverityBadgeClass(
  severity: string | null
): string {
  const normalizedSeverity =
    severity?.trim().toLowerCase();

  if (
    normalizedSeverity === "critical" ||
    normalizedSeverity === "high" ||
    normalizedSeverity === "immediate"
  ) {
    return (
      "border-red-800 bg-red-950/60 " +
      "text-red-200"
    );
  }

  if (
    normalizedSeverity === "medium" ||
    normalizedSeverity === "preventive"
  ) {
    return (
      "border-amber-800 bg-amber-950/50 " +
      "text-amber-200"
    );
  }

  return (
    "border-slate-700 bg-slate-800 " +
    "text-slate-300"
  );
}


function getReadinessClass(
  score: number
): string {
  if (score >= 90) {
    return "text-emerald-400";
  }

  if (score >= 70) {
    return "text-cyan-400";
  }

  if (score >= 40) {
    return "text-amber-400";
  }

  return "text-red-400";
}


function getRiskScoreClass(
  score: number | null
): string {
  if (
    score !== null &&
    score >= 80
  ) {
    return "text-red-400";
  }

  if (
    score !== null &&
    score >= 50
  ) {
    return "text-amber-400";
  }

  return "text-emerald-400";
}


function formatConfidence(
  confidence: number | null
): string {
  if (confidence === null) {
    return "Not available";
  }

  return `${Math.round(
    confidence * 100
  )}%`;
}


function formatDateTime(
  value: string | null
): string {
  if (!value) {
    return "Not scheduled";
  }

  const parsedDate = new Date(
    value
  );

  if (
    Number.isNaN(
      parsedDate.getTime()
    )
  ) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-IN",
    {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "UTC",
    }
  ).format(
    parsedDate
  );
}


function getActionHref(
  sourceType: string | null
): string {
  if (
    sourceType
      ?.trim()
      .toLowerCase() === "rca"
  ) {
    return "/rca";
  }

  return "/maintenance";
}


export default function OperationsSummaryPanel({
  data,
}: OperationsSummaryPanelProps) {
  const topAction =
    data.top_recommended_action;

  return (
    <section
      aria-labelledby="operations-summary-heading"
      className="mt-8 min-w-0"
    >
      <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="text-sm font-medium uppercase tracking-[0.25em] text-cyan-400">
            Operations Command Center
          </p>

          <h2
            id="operations-summary-heading"
            className="mt-2 break-words text-2xl font-semibold text-slate-100"
          >
            Live operational priorities
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            Current asset risk, RCA, compliance,
            maintenance and audit-readiness signals
            calculated from the active PlantMind
            demo dataset.
          </p>
        </div>

        <p className="shrink-0 text-xs text-slate-500">
          Generated:{" "}
          {formatDateTime(
            data.generated_at
          )}
        </p>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
        <div className="rounded-2xl border border-red-900/70 bg-red-950/20 p-5">
          <p className="text-sm text-slate-400">
            Assets at Risk
          </p>

          <p className="mt-3 text-3xl font-semibold text-red-400">
            {data.assets_at_risk.count}
          </p>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            Medium, high or critical
            operational risk
          </p>
        </div>

        <div className="rounded-2xl border border-red-900/70 bg-red-950/20 p-5">
          <p className="text-sm text-slate-400">
            Critical RCA Cases
          </p>

          <p className="mt-3 text-3xl font-semibold text-red-400">
            {data.critical_rca_cases.count}
          </p>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            Open high-severity investigations
          </p>
        </div>

        <div className="rounded-2xl border border-amber-900/70 bg-amber-950/20 p-5">
          <p className="text-sm text-slate-400">
            Compliance Gaps
          </p>

          <p className="mt-3 text-3xl font-semibold text-amber-400">
            {data.open_compliance_gaps.count}
          </p>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            Missing, delayed or overdue controls
          </p>
        </div>

        <div className="rounded-2xl border border-amber-900/70 bg-amber-950/20 p-5">
          <p className="text-sm text-slate-400">
            Urgent Work Orders
          </p>

          <p className="mt-3 text-3xl font-semibold text-amber-400">
            {data.urgent_work_orders.count}
          </p>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            Open high-priority maintenance work
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Audit Readiness
          </p>

          <p
            className={`mt-3 text-3xl font-semibold ${getReadinessClass(
              data.audit_readiness.score
            )}`}
          >
            {data.audit_readiness.score}%
          </p>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            {data.audit_readiness.label}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Missing Evidence
          </p>

          <p className="mt-3 text-3xl font-semibold text-red-400">
            {
              data.audit_readiness
                .missing_evidence_gap_count
            }
          </p>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            Open gaps without linked evidence
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-cyan-900/70 bg-cyan-950/20 p-6">
        <div className="flex min-w-0 flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-[0.25em] text-cyan-400">
              Highest-Priority Recommended Action
            </p>

            {topAction ? (
              <>
                <div className="mt-3 flex flex-wrap items-center gap-3">
                  <h3 className="break-words text-xl font-semibold text-slate-100">
                    {topAction.title ||
                      "Recommended operational action"}
                  </h3>

                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-medium ${getSeverityBadgeClass(
                      topAction.priority
                    )}`}
                  >
                    {topAction.priority ||
                      "Priority not set"}
                  </span>
                </div>

                {topAction.description ? (
                  <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-300">
                    {topAction.description}
                  </p>
                ) : null}

                <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-400">
                  <span>
                    Asset:{" "}
                    <strong className="font-medium text-slate-200">
                      {topAction.asset_id ||
                        "Not assigned"}
                    </strong>
                  </span>

                  <span>
                    Owner:{" "}
                    <strong className="font-medium text-slate-200">
                      {topAction.owner_role ||
                        "Not assigned"}
                    </strong>
                  </span>

                  <span>
                    Confidence:{" "}
                    <strong className="font-medium text-slate-200">
                      {formatConfidence(
                        topAction.confidence
                      )}
                    </strong>
                  </span>

                  {topAction.due_in_hours !== null ? (
                    <span>
                      Due in:{" "}
                      <strong className="font-medium text-slate-200">
                        {topAction.due_in_hours} hours
                      </strong>
                    </span>
                  ) : null}
                </div>

                {topAction.verification_metric ? (
                  <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-xs uppercase tracking-wider text-slate-500">
                      Verification requirement
                    </p>

                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      {topAction.verification_metric}
                    </p>
                  </div>
                ) : null}
              </>
            ) : (
              <div className="mt-4">
                <EmptyState
                  title="No recommended action"
                  message="PlantMind did not identify an outstanding RCA action or urgent work order."
                />
              </div>
            )}
          </div>

          {topAction ? (
            <Link
              href={getActionHref(
                topAction.source_type
              )}
              className="inline-flex min-h-11 shrink-0 items-center justify-center rounded-xl border border-cyan-700 bg-cyan-900/50 px-5 py-2.5 text-sm font-medium text-cyan-100 transition hover:border-cyan-500 hover:bg-cyan-800/60 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-slate-950"
            >
              Open source workspace
            </Link>
          ) : null}
        </div>
      </div>

      <div className="mt-6 grid min-w-0 gap-6 xl:grid-cols-3">
        <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between gap-4">
            <h3 className="text-lg font-semibold text-slate-100">
              Assets at Risk
            </h3>

            <Link
              href="/assets"
              className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              View assets
            </Link>
          </div>

          {data.assets_at_risk.items.length ? (
            <div className="mt-5 space-y-4">
              {data.assets_at_risk.items.map(
                (
                  asset,
                  index
                ) => (
                  <Link
                    key={
                      asset.asset_id ||
                      `risk-asset-${index}`
                    }
                    href={
                      asset.asset_id
                        ? `/assets/${encodeURIComponent(
                            asset.asset_id
                          )}`
                        : "/assets"
                    }
                    className="block min-w-0 rounded-xl border border-slate-800 bg-slate-950 p-4 transition hover:border-slate-700 hover:bg-slate-900"
                  >
                    <div className="flex min-w-0 items-start justify-between gap-4">
                      <div className="min-w-0">
                        <p className="truncate font-medium text-slate-100">
                          {asset.asset_id ||
                            "Unknown asset"}
                        </p>

                        <p className="mt-1 truncate text-sm text-slate-400">
                          {asset.asset_name ||
                            "Asset name unavailable"}
                        </p>
                      </div>

                      <p
                        className={`shrink-0 text-xl font-semibold ${getRiskScoreClass(
                          asset.risk_score
                        )}`}
                      >
                        {asset.risk_score ?? "—"}
                      </p>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2">
                      <span
                        className={`rounded-full border px-2.5 py-1 text-xs ${getSeverityBadgeClass(
                          asset.risk_level
                        )}`}
                      >
                        {asset.risk_level ||
                          "Unknown risk"}
                      </span>

                      <span className="rounded-full border border-slate-700 bg-slate-800 px-2.5 py-1 text-xs text-slate-300">
                        Health:{" "}
                        {asset.health_score ?? "—"}
                      </span>

                      <span className="rounded-full border border-slate-700 bg-slate-800 px-2.5 py-1 text-xs text-slate-300">
                        Sensor:{" "}
                        {asset.sensor_status ||
                          "Unknown"}
                      </span>
                    </div>
                  </Link>
                )
              )}
            </div>
          ) : (
            <div className="mt-5">
              <EmptyState
                title="No assets at risk"
                message="No medium, high or critical asset risks are currently active."
              />
            </div>
          )}
        </div>

        <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between gap-4">
            <h3 className="text-lg font-semibold text-slate-100">
              Critical RCA Cases
            </h3>

            <Link
              href="/rca"
              className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              Open RCA
            </Link>
          </div>

          {data.critical_rca_cases.items.length ? (
            <div className="mt-5 space-y-4">
              {data.critical_rca_cases.items.map(
                (
                  rcaCase,
                  index
                ) => (
                  <div
                    key={
                      rcaCase.case_id ||
                      `critical-rca-${index}`
                    }
                    className="min-w-0 rounded-xl border border-slate-800 bg-slate-950 p-4"
                  >
                    <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <p className="break-words font-medium text-slate-100">
                          {rcaCase.case_id ||
                            "Unknown RCA case"}
                        </p>

                        <p className="mt-1 break-words text-sm leading-5 text-slate-400">
                          {rcaCase.title ||
                            "RCA title unavailable"}
                        </p>
                      </div>

                      <span
                        className={`w-fit shrink-0 rounded-full border px-2.5 py-1 text-xs ${getSeverityBadgeClass(
                          rcaCase.severity
                        )}`}
                      >
                        {rcaCase.severity ||
                          "Unknown"}
                      </span>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
                      <span>
                        Asset:{" "}
                        {rcaCase.asset_id ||
                          "Unknown"}
                      </span>

                      <span>
                        Status:{" "}
                        {rcaCase.incident_status ||
                          "Unknown"}
                      </span>

                      <span>
                        Confidence:{" "}
                        {formatConfidence(
                          rcaCase.overall_confidence
                        )}
                      </span>
                    </div>

                    {rcaCase.recommendation_summary ? (
                      <p className="mt-3 break-words text-sm leading-6 text-slate-300">
                        {
                          rcaCase.recommendation_summary
                        }
                      </p>
                    ) : null}
                  </div>
                )
              )}
            </div>
          ) : (
            <div className="mt-5">
              <EmptyState
                title="No critical RCA cases"
                message="No open critical or high-severity RCA investigations were found."
              />
            </div>
          )}
        </div>

        <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between gap-4">
            <h3 className="text-lg font-semibold text-slate-100">
              Open Compliance Gaps
            </h3>

            <Link
              href="/compliance"
              className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              View compliance
            </Link>
          </div>

          {data.open_compliance_gaps.items.length ? (
            <div className="mt-5 space-y-4">
              {data.open_compliance_gaps.items
                .slice(
                  0,
                  5
                )
                .map(
                  (
                    gap,
                    index
                  ) => (
                    <div
                      key={
                        gap.gap_id ||
                        `compliance-gap-${index}`
                      }
                      className="min-w-0 rounded-xl border border-slate-800 bg-slate-950 p-4"
                    >
                      <div className="flex min-w-0 items-start justify-between gap-4">
                        <div className="min-w-0">
                          <p className="break-words font-medium text-slate-100">
                            {gap.gap_id ||
                              "Unknown gap"}
                          </p>

                          <p className="mt-1 break-words text-sm leading-5 text-slate-400">
                            {gap.requirement ||
                              "Requirement unavailable"}
                          </p>
                        </div>

                        <span
                          className={`shrink-0 rounded-full border px-2.5 py-1 text-xs ${getSeverityBadgeClass(
                            gap.gap_severity
                          )}`}
                        >
                          {gap.gap_severity ||
                            "Unknown"}
                        </span>
                      </div>

                      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
                        <span>
                          Asset:{" "}
                          {gap.asset_id ||
                            "Unknown"}
                        </span>

                        <span>
                          Status:{" "}
                          {gap.current_status ||
                            "Unknown"}
                        </span>
                      </div>

                      <div className="mt-3">
                        <span
                          className={`inline-flex rounded-full border px-2.5 py-1 text-xs ${
                            gap.evidence_available
                              ? "border-emerald-800 bg-emerald-950/50 text-emerald-300"
                              : "border-red-800 bg-red-950/50 text-red-300"
                          }`}
                        >
                          {gap.evidence_available
                            ? "Evidence linked"
                            : "Evidence missing"}
                        </span>
                      </div>
                    </div>
                  )
                )}
            </div>
          ) : (
            <div className="mt-5">
              <EmptyState
                title="No open compliance gaps"
                message="No missing, delayed or overdue compliance requirements were found."
              />
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <h3 className="text-lg font-semibold text-slate-100">
              Urgent Maintenance Work
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              Open work orders with high priority
              or elevated operational risk.
            </p>
          </div>

          <Link
            href="/maintenance"
            className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
          >
            Open maintenance command center
          </Link>
        </div>

        {data.urgent_work_orders.items.length ? (
          <div className="mt-5 grid min-w-0 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {data.urgent_work_orders.items.map(
              (
                workOrder,
                index
              ) => (
                <div
                  key={
                    workOrder.work_order_id ||
                    `urgent-work-order-${index}`
                  }
                  className="min-w-0 rounded-xl border border-slate-800 bg-slate-950 p-5"
                >
                  <div className="flex min-w-0 items-start justify-between gap-4">
                    <div className="min-w-0">
                      <p className="break-words font-medium text-slate-100">
                        {workOrder.work_order_id ||
                          "Unknown work order"}
                      </p>

                      <p className="mt-1 text-sm text-slate-500">
                        {workOrder.asset_id ||
                          "Unknown asset"}
                      </p>
                    </div>

                    <span
                      className={`shrink-0 rounded-full border px-2.5 py-1 text-xs ${getSeverityBadgeClass(
                        workOrder.priority
                      )}`}
                    >
                      {workOrder.priority ||
                        "Unknown"}
                    </span>
                  </div>

                  <p className="mt-4 break-words text-sm font-medium leading-6 text-slate-200">
                    {workOrder.title ||
                      "Work-order title unavailable"}
                  </p>

                  <div className="mt-4 space-y-2 text-xs text-slate-500">
                    <div className="flex justify-between gap-4">
                      <span>Status</span>

                      <span className="text-right text-slate-300">
                        {workOrder.status ||
                          "Unknown"}
                      </span>
                    </div>

                    <div className="flex justify-between gap-4">
                      <span>Risk score</span>

                      <span
                        className={`text-right font-medium ${getRiskScoreClass(
                          workOrder.risk_score
                        )}`}
                      >
                        {workOrder.risk_score ??
                          "Not available"}
                      </span>
                    </div>

                    <div className="flex justify-between gap-4">
                      <span>Confidence</span>

                      <span className="text-right text-slate-300">
                        {formatConfidence(
                          workOrder.confidence
                        )}
                      </span>
                    </div>

                    <div className="flex justify-between gap-4">
                      <span>Due</span>

                      <span className="text-right text-slate-300">
                        {formatDateTime(
                          workOrder.due_at
                        )}
                      </span>
                    </div>
                  </div>

                  {workOrder.owner_role ? (
                    <p className="mt-4 break-words border-t border-slate-800 pt-4 text-xs text-slate-500">
                      Owner:{" "}
                      <span className="text-slate-300">
                        {workOrder.owner_role}
                      </span>
                    </p>
                  ) : null}
                </div>
              )
            )}
          </div>
        ) : (
          <div className="mt-5">
            <EmptyState
              title="No urgent work orders"
              message="No open work orders currently meet the urgent operational-risk criteria."
            />
          </div>
        )}
      </div>
    </section>
  );
}
