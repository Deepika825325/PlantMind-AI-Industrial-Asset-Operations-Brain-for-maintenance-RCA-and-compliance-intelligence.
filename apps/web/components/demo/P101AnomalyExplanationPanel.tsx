type SignalContribution = {
  signalName: string;
  displayName: string;
  baselineValue: number;
  observedValue: number;
  unit: string;
  deviationPercent: number;
  contributionWeight: number;
  explanation: string;
};

const SIGNAL_CONTRIBUTIONS: SignalContribution[] = [
  {
    signalName: "vibration_mm_s",
    displayName: "Vibration",
    baselineValue: 2.4,
    observedValue: 8.4,
    unit: "mm/s",
    deviationPercent: 250,
    contributionWeight: 42,
    explanation:
      "Strongest driver. Vibration moved from normal operating range into severe mechanical-degradation range.",
  },
  {
    signalName: "bearing_temperature_deg_c",
    displayName: "Bearing temperature",
    baselineValue: 64,
    observedValue: 91,
    unit: "deg C",
    deviationPercent: 42.2,
    contributionWeight: 31,
    explanation:
      "Temperature rose with vibration, supporting bearing wear or lubrication-degradation hypothesis.",
  },
  {
    signalName: "motor_current_a",
    displayName: "Motor current",
    baselineValue: 18.7,
    observedValue: 24,
    unit: "A",
    deviationPercent: 28.3,
    contributionWeight: 17,
    explanation:
      "Current increased moderately, suggesting higher mechanical load rather than an isolated sensor spike.",
  },
  {
    signalName: "rpm",
    displayName: "RPM",
    baselineValue: 1480,
    observedValue: 1455,
    unit: "rpm",
    deviationPercent: -1.7,
    contributionWeight: 10,
    explanation:
      "RPM dipped slightly while vibration and current increased, supporting mechanical-load interpretation.",
  },
];

const evidenceIds = [
  "P101-EV-001",
  "P101-EV-002",
  "P101-EV-003",
  "RCA-P101-001",
];

export function P101AnomalyExplanationPanel() {
  return (
    <section className="mt-8 rounded-2xl border border-purple-900/70 bg-purple-950/20 p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-purple-300">
            Day 2 AI Explanation
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            Why P-101 was flagged as critical
          </h2>

          <p className="mt-4 max-w-4xl text-sm leading-6 text-slate-300">
            P-101 was flagged because vibration and bearing temperature
            increased together during the degradation replay. The combined
            multivariate residual exceeded the production threshold and
            matched the known high-vibration bearing-temperature RCA pattern.
          </p>
        </div>

        <div className="rounded-2xl border border-purple-800 bg-slate-950 p-4 text-sm">
          <p className="text-slate-500">
            Model
          </p>

          <p className="mt-1 font-semibold text-purple-200">
            plantmind-p101-anomaly-detector
          </p>

          <p className="mt-3 text-slate-500">
            Version
          </p>

          <p className="mt-1 font-semibold text-slate-100">
            v0.3.11 Production
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-sm text-slate-500">
            Anomaly label
          </p>

          <p className="mt-2 text-2xl font-semibold text-red-300">
            critical
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-sm text-slate-500">
            Anomaly score
          </p>

          <p className="mt-2 text-2xl font-semibold text-amber-300">
            0.87
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-sm text-slate-500">
            Confidence
          </p>

          <p className="mt-2 text-2xl font-semibold text-emerald-300">
            91%
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        {SIGNAL_CONTRIBUTIONS.map((signal) => (
          <article
            key={signal.signalName}
            className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-100">
                  {signal.displayName}
                </h3>

                <p className="mt-1 text-xs text-slate-500">
                  {signal.signalName}
                </p>
              </div>

              <span className="rounded-full border border-purple-800 bg-purple-950/50 px-3 py-1 text-xs font-semibold text-purple-200">
                {signal.contributionWeight}% impact
              </span>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div>
                <p className="text-xs text-slate-500">
                  Baseline
                </p>

                <p className="mt-1 font-semibold">
                  {signal.baselineValue} {signal.unit}
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-500">
                  Observed
                </p>

                <p className="mt-1 font-semibold">
                  {signal.observedValue} {signal.unit}
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-500">
                  Deviation
                </p>

                <p className="mt-1 font-semibold">
                  {signal.deviationPercent}%
                </p>
              </div>
            </div>

            <p className="mt-4 text-sm leading-6 text-slate-400">
              {signal.explanation}
            </p>
          </article>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Supporting evidence
          </p>

          <div className="mt-3 flex flex-wrap gap-2">
            {evidenceIds.map((evidenceId) => (
              <span
                key={evidenceId}
                className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300"
              >
                {evidenceId}
              </span>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-amber-900/70 bg-amber-950/20 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-amber-300">
            Human review required
          </p>

          <p className="mt-3 text-sm leading-6 text-amber-100">
            The model explains dominant signals, but maintenance approval still
            requires engineer review of RCA evidence, safety procedure, and
            post-maintenance verification.
          </p>

          <code className="mt-4 block break-all rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-cyan-300">
            GET /demo/p101/anomaly-explanation
          </code>
        </div>
      </div>
    </section>
  );
}
