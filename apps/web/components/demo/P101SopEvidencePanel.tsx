type EvidenceItem = {
  evidenceId: string;
  documentId: string;
  documentTitle: string;
  documentType: string;
  citationLabel: string;
  excerpt: string;
  relevance: string;
  supportsDecision: string;
  requiredAction: string;
  verificationRequirement: string;
};

type EvidenceGroup = {
  title: string;
  description: string;
  items: EvidenceItem[];
};

const evidenceGroups: EvidenceGroup[] = [
  {
    title: "SOP evidence",
    description:
      "Procedures that define what maintenance team must do before safely closing P-101 work.",
    items: [
      {
        evidenceId: "SOP-P101-001-CIT-001",
        documentId: "SOP-P101-001_Pump_Lubrication_and_Bearing_Check",
        documentTitle: "SOP-P101-001: Pump Lubrication and Bearing Check",
        documentType: "SOP / Manual",
        citationLabel: "[SOP-P101-001]",
        excerpt:
          "Defines inspection of lubricant condition, bearing health, and safe maintenance steps for P-101.",
        relevance:
          "Directly supports the lubrication degradation hypothesis and work order.",
        supportsDecision:
          "Inspect and restore P-101 bearing lubrication.",
        requiredAction:
          "Verify lubricant condition, lubricant quantity, bearing housing condition, and attach evidence.",
        verificationRequirement:
          "Lubrication completion evidence must be attached before closing maintenance action.",
      },
      {
        evidenceId: "SOP-P101-002-CIT-001",
        documentId: "SOP-P101-002_Pump_Vibration_Inspection",
        documentTitle: "SOP-P101-002: Pump Vibration Inspection",
        documentType: "SOP / Manual",
        citationLabel: "[SOP-P101-002]",
        excerpt:
          "Defines post-maintenance vibration assessment and acceptable return-to-service checks.",
        relevance:
          "Supports post-maintenance verification after bearing or lubrication corrective action.",
        supportsDecision:
          "Run vibration verification before returning P-101 to service.",
        requiredAction:
          "Perform vibration inspection and compare against approved operating limits.",
        verificationRequirement:
          "Vibration must return to acceptable range before work order closure.",
      },
    ],
  },
  {
    title: "Inspection evidence",
    description:
      "Physical inspection findings that ground the anomaly and RCA decision.",
    items: [
      {
        evidenceId: "IR-P101-001-CIT-001",
        documentId: "IR-P101-001_Pump_Vibration_Inspection",
        documentTitle: "IR-P101-001: Pump Vibration Inspection",
        documentType: "Inspection Report",
        citationLabel: "[IR-P101-001]",
        excerpt:
          "Inspection identified high vibration and abnormal mechanical noise near the bearing housing.",
        relevance:
          "Confirms anomaly is supported by physical inspection, not only telemetry.",
        supportsDecision:
          "Prioritize bearing and lubrication inspection.",
        requiredAction:
          "Inspect bearing housing and perform vibration spectrum assessment.",
        verificationRequirement:
          "Attach post-maintenance inspection readings.",
      },
      {
        evidenceId: "IR-P101-002-CIT-001",
        documentId: "IR-P101-002_Pump_Bearing_Temperature_Check",
        documentTitle: "IR-P101-002: Pump Bearing Temperature Check",
        documentType: "Inspection Report",
        citationLabel: "[IR-P101-002]",
        excerpt:
          "Bearing temperature was reported in warning range with an increasing trend.",
        relevance:
          "Supports bearing-friction and lubrication-degradation explanation.",
        supportsDecision:
          "Check bearing temperature trend after maintenance.",
        requiredAction:
          "Validate bearing temperature after lubrication or bearing corrective action.",
        verificationRequirement:
          "Bearing temperature must return to acceptable range.",
      },
    ],
  },
  {
    title: "Incident and compliance evidence",
    description:
      "Operational context and audit evidence that explain why closure must be governed.",
    items: [
      {
        evidenceId: "INC-P101-001-CIT-001",
        documentId: "INC-P101-001_High_Vibration_Event",
        documentTitle: "INC-P101-001: High Vibration Event",
        documentType: "Incident Report",
        citationLabel: "[INC-P101-001]",
        excerpt:
          "P-101 high vibration event was opened for RCA after vibration, temperature, and abnormal noise were observed.",
        relevance:
          "Links anomaly and RCA workflow to original incident context.",
        supportsDecision:
          "Keep incident open until RCA evidence and maintenance verification are complete.",
        requiredAction:
          "Link RCA, work order, and verification results to the incident.",
        verificationRequirement:
          "Incident closure requires RCA and post-maintenance evidence.",
      },
      {
        evidenceId: "COMP-001-CIT-001",
        documentId: "COMP-001_Compliance_Checklist",
        documentTitle: "COMP-001: PlantMind Demo Compliance Checklist",
        documentType: "Compliance Checklist",
        citationLabel: "[COMP-001]",
        excerpt:
          "Lubrication completion evidence for P-101 was not available during compliance review.",
        relevance:
          "Explains why missing lubrication evidence increases maintenance and audit risk.",
        supportsDecision:
          "Require evidence attachment before closure.",
        requiredAction:
          "Attach lubrication evidence, safety checklist, and post-maintenance verification.",
        verificationRequirement:
          "Compliance package must show completed evidence before final closure.",
      },
    ],
  },
];

const citationTrail = [
  "[SOP-P101-001] defines lubrication and bearing check.",
  "[SOP-P101-002] defines vibration verification.",
  "[IR-P101-001] confirms high vibration and abnormal noise.",
  "[IR-P101-002] confirms bearing temperature warning trend.",
  "[INC-P101-001] links symptoms to the incident.",
  "[COMP-001] confirms missing lubrication evidence.",
];

export function P101SopEvidencePanel() {
  return (
    <section className="mt-8 rounded-2xl border border-cyan-900/70 bg-cyan-950/20 p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-cyan-300">
            Day 4 SOP / RAG Evidence Demo
          </p>

          <h2 className="mt-3 text-2xl font-semibold text-slate-100">
            What evidence supports the P-101 maintenance decision?
          </h2>

          <p className="mt-4 max-w-4xl text-sm leading-6 text-slate-300">
            PlantMind answers the maintenance question using SOPs, inspection
            reports, incident context, and compliance evidence. The result is a
            citation-style trail that explains why lubrication, bearing
            inspection, alignment verification, and post-maintenance checks are
            required before closure.
          </p>
        </div>

        <div className="rounded-2xl border border-cyan-800 bg-slate-950 p-4 text-sm">
          <p className="text-slate-500">
            RAG status
          </p>

          <p className="mt-1 font-semibold text-cyan-200">
            grounded_with_citations
          </p>

          <p className="mt-3 text-slate-500">
            Confidence
          </p>

          <p className="mt-1 font-semibold text-slate-100">
            92%
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
          Answer
        </p>

        <p className="mt-3 text-sm leading-6 text-slate-300">
          The P-101 maintenance decision is supported by the pump lubrication
          SOP, vibration inspection SOP, inspection reports confirming high
          vibration and bearing-temperature increase, the high-vibration
          incident report, and the compliance checklist showing missing
          lubrication evidence.
        </p>

        <p className="mt-4 text-sm leading-6 text-cyan-100">
          Decision: inspect and restore bearing lubrication, inspect bearing
          condition, verify alignment, and run post-maintenance vibration and
          temperature checks.
        </p>
      </div>

      <div className="mt-6 grid gap-4">
        {evidenceGroups.map((group) => (
          <div
            key={group.title}
            className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
          >
            <div>
              <h3 className="text-xl font-semibold text-slate-100">
                {group.title}
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                {group.description}
              </p>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              {group.items.map((item) => (
                <article
                  key={item.evidenceId}
                  className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full border border-cyan-800 bg-cyan-950/40 px-3 py-1 text-xs font-semibold text-cyan-200">
                      {item.citationLabel}
                    </span>

                    <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-300">
                      {item.documentType}
                    </span>
                  </div>

                  <h4 className="mt-4 text-lg font-semibold text-slate-100">
                    {item.documentTitle}
                  </h4>

                  <p className="mt-1 break-all text-xs text-slate-500">
                    {item.documentId}
                  </p>

                  <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                      Excerpt
                    </p>

                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      {item.excerpt}
                    </p>
                  </div>

                  <div className="mt-4 grid gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                        Relevance
                      </p>

                      <p className="mt-2 text-sm leading-6 text-slate-400">
                        {item.relevance}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                        Supports decision
                      </p>

                      <p className="mt-2 text-sm leading-6 text-slate-300">
                        {item.supportsDecision}
                      </p>
                    </div>

                    <div className="rounded-xl border border-emerald-900/70 bg-emerald-950/20 p-4">
                      <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">
                        Verification requirement
                      </p>

                      <p className="mt-2 text-sm leading-6 text-emerald-100">
                        {item.verificationRequirement}
                      </p>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Citation trail
          </p>

          <ol className="mt-3 space-y-2 text-sm text-slate-300">
            {citationTrail.map((citation) => (
              <li key={citation}>
                {citation}
              </li>
            ))}
          </ol>
        </div>

        <div className="rounded-2xl border border-amber-900/70 bg-amber-950/20 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-amber-300">
            Governance note
          </p>

          <p className="mt-3 text-sm leading-6 text-amber-100">
            The answer is evidence-grounded and citation-backed, but PlantMind
            still requires engineer approval before confirming RCA or closing
            the work order.
          </p>

          <code className="mt-4 block break-all rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-cyan-300">
            GET /demo/p101/sop-evidence
          </code>
        </div>
      </div>
    </section>
  );
}
