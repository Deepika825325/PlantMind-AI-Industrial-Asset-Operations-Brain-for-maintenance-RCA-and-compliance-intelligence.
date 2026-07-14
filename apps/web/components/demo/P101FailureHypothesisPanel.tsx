type FailureHypothesis = {
  rank: number;
  failureMode: string;
  displayName: string;
  probability: number;
  confidenceLabel: string;
  supportingSignals: string[];
  supportingEvidenceIds: string[];
  contradictoryEvidence: string[];
  missingTests: string[];
  recommendedNextAction: string;
  decisionReason: string;
};

const HYPOTHESES: FailureHypothesis[] = [
  {
    rank: 1,
    failureMode: "lubrication_degradation",
    displayName: "Lubrication degradation",
    probability: 37,
    confidenceLabel: "High",
    supportingSignals: [
      "Missing lubrication evidence",
      "Bearing temperature rise",
      "Vibration escalation",
      "Abnormal mechanical noise",
    ],
    supportingEvidenceIds: [
      "P101-EV-001",
      "P101-EV-002",
      "P101-EV-003",
    ],
    contradictoryEvidence: [
      "No lubricant laboratory analysis is currently available.",
    ],
    missingTests: [
      "Lubricant condition inspection",
      "Lubricant quantity verification",
      "Bearing housing inspection",
    ],
    recommendedNextAction:
      "Inspect and restore bearing lubrication before confirming the RCA.",
    decisionReason:
      "Lubrication evidence is missing before the temperature and vibration escalation. This makes lubrication degradation the strongest explainable maintenance hypothesis.",
  },
  {
    rank: 2,
    failureMode: "bearing_damage",
    displayName: "Bearing wear or damage",
    probability: 29,
    confidenceLabel: "High",
    supportingSignals: [
      "High vibration",
      "Bearing temperature rise",
      "Abnormal mechanical noise near bearing housing",
    ],
    supportingEvidenceIds: [
      "P101-EV-002",
      "P101-EV-003",
      "P101-EV-004",
    ],
    contradictoryEvidence: [
      "Direct bearing inspection result is not yet attached.",
    ],
    missingTests: [
      "Bearing clearance check",
      "Bearing visual inspection",
      "Vibration spectrum analysis",
    ],
    recommendedNextAction:
      "Inspect bearing condition and attach inspection evidence to the RCA case.",
    decisionReason:
      "The signal pattern is consistent with bearing wear, but confirmation requires physical inspection.",
  },
  {
    rank: 3,
    failureMode: "shaft_misalignment",
    displayName: "Shaft misalignment",
    probability: 18,
    confidenceLabel: "Medium",
    supportingSignals: [
      "High vibration",
      "Slight RPM drop",
      "Motor current increase",
    ],
    supportingEvidenceIds: [
      "P101-EV-003",
      "P101-EV-004",
    ],
    contradictoryEvidence: [
      "Alignment measurements have not yet been recorded.",
      "Temperature rise points more strongly to bearing friction.",
    ],
    missingTests: [
      "Shaft alignment measurement",
      "Coupling inspection",
    ],
    recommendedNextAction:
      "Perform shaft alignment assessment before returning P-101 to service.",
    decisionReason:
      "Misalignment can explain vibration and current rise, but current evidence supports lubrication and bearing issues more strongly.",
  },
  {
    rank: 4,
    failureMode: "cavitation_or_hydraulic_instability",
    displayName: "Cavitation or hydraulic instability",
    probability: 11,
    confidenceLabel: "Low-Medium",
    supportingSignals: [
      "Vibration",
      "Mechanical noise",
    ],
    supportingEvidenceIds: [
      "P101-EV-003",
    ],
    contradictoryEvidence: [
      "No confirmed suction-pressure anomaly is available.",
      "Bearing temperature increase is more consistent with mechanical friction.",
    ],
    missingTests: [
      "Suction pressure trend review",
      "Flow instability check",
      "Pump operating point verification",
    ],
    recommendedNextAction:
      "Check suction pressure and operating point after bearing and lubrication checks are initiated.",
    decisionReason:
      "Hydraulic instability remains possible, but evidence is weaker than lubrication and bearing hypotheses.",
  },
  {
    rank: 5,
    failureMode: "sensor_fault",
    displayName: "Sensor fault or data-quality issue",
    probability: 5,
    confidenceLabel: "Low",
    supportingSignals: [
      "Telemetry-driven anomaly score",
    ],
    supportingEvidenceIds: [
      "P101-EV-002",
    ],
    contradictoryEvidence: [
      "Independent inspection confirmed abnormal vibration and noise.",
      "Multiple signals changed together instead of one isolated sensor.",
    ],
    missingTests: [
      "Sensor calibration check",
      "Cross-check with handheld vibration reading",
    ],
    recommendedNextAction:
      "Perform calibration check, but do not treat this as the primary cause unless physical checks contradict the mechanical evidence.",
    decisionReason:
      "A pure sensor fault is unlikely because inspection evidence confirms physical symptoms.",
  },
];

function getProbabilityWidth(probability: number): string {
  return `${probability}%`;
}

export function P101FailureHypothesisPanel() {
  return (
    <section className="mt-8 rounded-2xl border border-amber-900/70 bg-amber-950/20 p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-amber-300">
            Day 3 Failure Hypothesis Ranking
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            Evidence-backed diagnostic ranking for P-101
          </h2>

          <p className="mt-4 max-w-4xl text-sm leading-6 text-slate-300">
            PlantMind ranks likely failure modes using anomaly signals,
            RCA evidence, contradictions, and missing tests. The system
            recommends next actions, but does not automatically confirm
            the root cause.
          </p>
        </div>

        <div className="rounded-2xl border border-amber-800 bg-slate-950 p-4 text-sm">
          <p className="text-slate-500">
            Primary hypothesis
          </p>

          <p className="mt-1 font-semibold text-amber-200">
            Lubrication degradation
          </p>

          <p className="mt-3 text-slate-500">
            RCA case
          </p>

          <p className="mt-1 font-semibold text-slate-100">
            RCA-P101-001
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4">
        {HYPOTHESES.map((hypothesis) => (
          <article
            key={hypothesis.failureMode}
            className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-300">
                    Rank {hypothesis.rank}
                  </span>

                  <span className="rounded-full border border-amber-800 bg-amber-950/50 px-3 py-1 text-xs font-semibold text-amber-200">
                    {hypothesis.confidenceLabel} confidence
                  </span>

                  <span className="rounded-full border border-purple-800 bg-purple-950/50 px-3 py-1 text-xs font-semibold text-purple-200">
                    {hypothesis.probability}% probability
                  </span>
                </div>

                <h3 className="mt-4 text-xl font-semibold text-slate-100">
                  {hypothesis.displayName}
                </h3>

                <p className="mt-2 text-xs text-slate-500">
                  {hypothesis.failureMode}
                </p>

                <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-400">
                  {hypothesis.decisionReason}
                </p>
              </div>

              <div className="w-full max-w-sm rounded-2xl border border-slate-800 bg-slate-900 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Ranking score
                </p>

                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-2 rounded-full bg-amber-400"
                    style={{
                      width: getProbabilityWidth(
                        hypothesis.probability
                      ),
                    }}
                  />
                </div>

                <p className="mt-3 text-sm text-slate-400">
                  {hypothesis.probability}% diagnostic probability
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-3">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Supporting signals
                </p>

                <div className="mt-3 flex flex-wrap gap-2">
                  {hypothesis.supportingSignals.map((signal) => (
                    <span
                      key={signal}
                      className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300"
                    >
                      {signal}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Evidence
                </p>

                <div className="mt-3 flex flex-wrap gap-2">
                  {hypothesis.supportingEvidenceIds.map((evidenceId) => (
                    <span
                      key={evidenceId}
                      className="rounded-full border border-cyan-800 bg-cyan-950/40 px-3 py-1 text-xs text-cyan-200"
                    >
                      {evidenceId}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Missing tests
                </p>

                <ul className="mt-3 space-y-2 text-sm text-slate-400">
                  {hypothesis.missingTests.map((test) => (
                    <li key={test}>
                      {test}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <div className="rounded-2xl border border-red-900/70 bg-red-950/20 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-red-300">
                  Contradictions / limitations
                </p>

                <ul className="mt-3 space-y-2 text-sm text-red-100">
                  {hypothesis.contradictoryEvidence.map((item) => (
                    <li key={item}>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-2xl border border-emerald-900/70 bg-emerald-950/20 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">
                  Recommended next action
                </p>

                <p className="mt-3 text-sm leading-6 text-emerald-100">
                  {hypothesis.recommendedNextAction}
                </p>
              </div>
            </div>
          </article>
        ))}
      </div>

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
          Governance note
        </p>

        <p className="mt-3 text-sm leading-6 text-slate-300">
          PlantMind ranks hypotheses and recommends next tests, but it does
          not automatically confirm the root cause or close the
          safety-critical work order. Engineer approval remains mandatory.
        </p>

        <code className="mt-4 block break-all rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-cyan-300">
          GET /demo/p101/failure-hypotheses
        </code>
      </div>
    </section>
  );
}
