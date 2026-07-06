import type {
  ComplianceOverview,
} from "@/lib/types";

type ComplianceKpiCardsProps = {
  overview: ComplianceOverview;
};

export default function ComplianceKpiCards({
  overview,
}: ComplianceKpiCardsProps) {
  const cards = [
    {
      label: "Average Audit Score",
      value: `${overview.average_audit_readiness_score}`,
      suffix: "/100",
      valueClass: "text-cyan-300",
    },
    {
      label: "Open Gaps",
      value: `${overview.total_open_gaps}`,
      suffix: "",
      valueClass: "text-red-300",
    },
    {
      label: "Missing Evidence",
      value: `${overview.missing_evidence_gaps}`,
      suffix: "",
      valueClass: "text-amber-300",
    },
    {
      label: "Assets Assessed",
      value: `${overview.total_assets}`,
      suffix: "",
      valueClass: "text-emerald-300",
    },
  ];

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article
          key={card.label}
          className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
        >
          <p className="text-sm text-slate-400">
            {card.label}
          </p>

          <div className="mt-3 flex items-end gap-2">
            <p
              className={`text-3xl font-semibold ${card.valueClass}`}
            >
              {card.value}
            </p>

            {card.suffix && (
              <span className="pb-1 text-sm text-slate-500">
                {card.suffix}
              </span>
            )}
          </div>
        </article>
      ))}
    </section>
  );
}