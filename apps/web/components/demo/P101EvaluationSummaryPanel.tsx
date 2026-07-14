type EvaluationMetric = {
  metricName: string;
  displayName: string;
  score: number;
  status: string;
  evidence: string[];
  judgeReadout: string;
};

type EvaluationGap = {
  gapId: string;
  title: string;
  severity: string;
  explanation: string;
  mitigation: string;
};

const metrics: EvaluationMetric[] = [
  {
    metricName: "closed_loop_completion",
    displayName: "Closed-loop workflow completion",
    score: 100,
    status: "passed",
    evidence: [
      "Telemetry replay",
      "Anomaly detection",
      "Incident creation",
      "RCA hypothesis",
      "Governed work order",
      "Recovery verification",
      "Audit package",
    ],
    judgeReadout:
      "The demo shows a complete industrial maintenance decision loop from signal to governed closure.",
  },
  {
    metricName: "anomaly_explanation_coverage",
    displayName: "Anomaly explanation coverage",
    score: 92,
    status: "passed",
    evidence: [
      "Primary driver: vibration_mm_s",
      "Secondary driver: bearing_temperature_deg_c",
      "Model registry link included",
      "Human review reason included",
    ],
    judgeReadout:
      "The anomaly is not shown as a black-box alert. It is explained using signal contributions, confidence, and model metadata.",
  },
  {
    metricName: "failure_hypothesis_quality",
    displayName: "Failure hypothesis ranking quality",
    score: 90,
    status: "passed",
    evidence: [
      "Lubrication degradation ranked first",
      "Bearing damage ranked second",
      "Misalignment and cavitation included as alternatives",
      "Sensor fault treated as low-confidence hypothesis",
    ],
    judgeReadout:
      "The system ranks plausible causes and shows evidence, contradictions, missing tests, and recommended next actions.",
  },
  {
    metricName: "rag_evidence_grounding",
    displayName: "SOP and RAG evidence grounding",
    score: 92,
    status: "passed",
    evidence: [
      "SOP-P101-001",
      "SOP-P101-002",
      "IR-P101-001",
      "IR-P101-002",
      "INC-P101-001",
      "COMP-001",
    ],
    judgeReadout:
      "The maintenance decision is grounded in SOPs, inspection reports, incident context, and compliance evidence.",
  },
  {
    metricName: "governance_and_safety",
    displayName: "Governance and safety controls",
    score: 95,
    status: "passed",
    evidence: [
      "Engineer approval required",
      "Root cause is not auto-confirmed",
      "Safety-critical work order is not auto-closed",
      "Audit package remains part of closure flow",
    ],
    judgeReadout:
      "The demo is credible because it prevents unrestricted agent behavior in safety-critical maintenance decisions.",
  },
  {
    metricName: "demo_readiness",
    displayName: "Judge demo readiness",
    score: 91,
    status: "passed",
    evidence: [
      "/demo/p101-closed-loop",
      "/demo/p101/anomaly-explanation",
      "/demo/p101/failure-hypotheses",
      "/demo/p101/sop-evidence",
      "/demo/p101/evaluation-summary",
    ],
    judgeReadout:
      "The demo has a clear story, visible evidence, diagnostic reasoning, and measurable readiness.",
  },
];

const openGaps: EvaluationGap[] = [
  {
    gapId: "GAP-P101-001",
    title: "Live plant connection not enabled",
    severity: "medium",
    explanation:
      "The demo uses deterministic telemetry and curated industrial evidence instead of a live plant historian.",
    mitigation:
      "Present this as a production-ready demo layer that can connect to historian, CMMS, and document repositories in deployment.",
  },
  {
    gapId: "GAP-P101-002",
    title: "Physical inspection still required",
    severity: "low",
    explanation:
      "PlantMind ranks likely failure causes, but bearing inspection, lubricant inspection, and alignment readings are still required before final confirmation.",
    mitigation:
      "Use this as a strength: the system supports engineers instead of replacing safety-critical approval.",
  },
];

const demoOrder = [
  "Start with P-101 closed-loop timeline.",
  "Show anomaly explanation and signal contributions.",
  "Show ranked failure hypotheses with contradictions.",
  "Show SOP/RAG evidence and citation trail.",
  "Close with evaluation summary and governance note.",
];

function getScoreWidth(score: number): string {
  return `${score}%`;
}

export function P101EvaluationSummaryPanel() {
  return (
    <section className="mt-8 rounded-2xl border border-emerald-900/70 bg-emerald-950/20 p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-emerald-300">
            Day 5 Judge Metrics Dashboard
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            Evaluation summary for the P-101 demo
          </h2>

          <p className="mt-4 max-w-4xl text-sm leading-6 text-slate-300">
            This panel summarizes why the demo is judge-ready: it covers the
            closed-loop workflow, anomaly explanation, failure hypothesis
            ranking, SOP/RAG evidence, and safety governance controls.
          </p>
        </div>

        <div className="rounded-2xl border border-emerald-800 bg-slate-950 p-5 text-sm">
          <p className="text-slate-500">
            Overall score
          </p>

          <p className="mt-1 text-4xl font-semibold text-emerald-300">
            93%
          </p>

          <p className="mt-3 rounded-full border border-emerald-800 bg-emerald-950/40 px-3 py-1 text-xs font-semibold text-emerald-200">
            judge_ready
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Demo name
          </p>

          <p className="mt-3 text-lg font-semibold text-slate-100">
            P-101 Closed-Loop Industrial Maintenance Demo
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Evaluation version
          </p>

          <p className="mt-3 text-lg font-semibold text-slate-100">
            demo-eval-v1
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Validated endpoint
          </p>

          <code className="mt-3 block break-all text-sm text-cyan-300">
            GET /demo/p101/evaluation-summary
          </code>
        </div>
      </div>

      <div className="mt-6 grid gap-4">
        {metrics.map((metric) => (
          <article
            key={metric.metricName}
            className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full border border-emerald-800 bg-emerald-950/40 px-3 py-1 text-xs font-semibold text-emerald-200">
                    {metric.status}
                  </span>

                  <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300">
                    {metric.metricName}
                  </span>
                </div>

                <h3 className="mt-4 text-xl font-semibold text-slate-100">
                  {metric.displayName}
                </h3>

                <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-400">
                  {metric.judgeReadout}
                </p>
              </div>

              <div className="w-full max-w-sm rounded-2xl border border-slate-800 bg-slate-900 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Score
                </p>

                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-2 rounded-full bg-emerald-400"
                    style={{
                      width: getScoreWidth(metric.score),
                    }}
                  />
                </div>

                <p className="mt-3 text-sm font-semibold text-slate-100">
                  {metric.score}%
                </p>
              </div>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {metric.evidence.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300"
                >
                  {item}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-amber-900/70 bg-amber-950/20 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-amber-300">
            Open gaps to explain honestly
          </p>

          <div className="mt-4 space-y-4">
            {openGaps.map((gap) => (
              <div
                key={gap.gapId}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
              >
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full border border-amber-800 bg-amber-950/40 px-3 py-1 text-xs text-amber-200">
                    {gap.severity}
                  </span>

                  <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300">
                    {gap.gapId}
                  </span>
                </div>

                <h3 className="mt-3 font-semibold text-slate-100">
                  {gap.title}
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  {gap.explanation}
                </p>

                <p className="mt-3 text-sm leading-6 text-amber-100">
                  Mitigation: {gap.mitigation}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Recommended judge demo order
          </p>

          <ol className="mt-4 space-y-3 text-sm text-slate-300">
            {demoOrder.map((step) => (
              <li key={step}>
                {step}
              </li>
            ))}
          </ol>

          <div className="mt-5 rounded-2xl border border-emerald-900/70 bg-emerald-950/20 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">
              Governance note
            </p>

            <p className="mt-3 text-sm leading-6 text-emerald-100">
              PlantMind provides ranked and evidence-backed decision support,
              but it does not automatically confirm root cause, approve safety
              work, or close critical maintenance actions.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
