import type { MaintenanceStatistics } from "@/lib/types";

type MaintenanceKpiCardsProps = {
  statistics: MaintenanceStatistics | null;
  loading?: boolean;
};

type KpiCard = {
  label: string;
  value: string | number;
  description: string;
  valueClassName: string;
};

function createKpiCards(
  statistics: MaintenanceStatistics | null
): KpiCard[] {
  return [
    {
      label: "Total Work Orders",
      value: statistics?.total_work_orders ?? 0,
      description: "All maintenance actions",
      valueClassName: "text-slate-100"
    },
    {
      label: "Open Actions",
      value: statistics?.open_work_orders ?? 0,
      description: "Pending execution",
      valueClassName: "text-cyan-400"
    },
    {
      label: "Overdue",
      value: statistics?.overdue_work_orders ?? 0,
      description: "Past the required due date",
      valueClassName: "text-red-400"
    },
    {
      label: "High Risk",
      value: statistics?.high_risk_work_orders ?? 0,
      description: "Risk score of 80 or higher",
      valueClassName: "text-amber-400"
    },
    {
      label: "RCA Linked",
      value: statistics?.rca_linked_work_orders ?? 0,
      description: "Generated from RCA findings",
      valueClassName: "text-violet-400"
    },
    {
      label: "Average Risk",
      value: statistics
        ? statistics.average_risk_score.toFixed(1)
        : "0.0",
      description: "Portfolio-level risk score",
      valueClassName: "text-orange-400"
    }
  ];
}

export default function MaintenanceKpiCards({
  statistics,
  loading = false
}: MaintenanceKpiCardsProps) {
  const cards = createKpiCards(statistics);

  return (
    <section
      aria-label="Maintenance key performance indicators"
      className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6"
    >
      {cards.map((card) => (
        <article
          key={card.label}
          className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-sm"
        >
          <p className="text-sm font-medium text-slate-400">
            {card.label}
          </p>

          {loading ? (
            <div className="mt-4 h-9 w-20 animate-pulse rounded-lg bg-slate-800" />
          ) : (
            <p
              className={`mt-3 text-3xl font-semibold tracking-tight ${card.valueClassName}`}
            >
              {card.value}
            </p>
          )}

          <p className="mt-2 text-xs leading-5 text-slate-500">
            {card.description}
          </p>
        </article>
      ))}
    </section>
  );
}