"use client";

import { useMemo, useState } from "react";

type EvidenceStatus =
  | "satisfied"
  | "failed"
  | "missing"
  | "warning"
  | "not_applicable";

type AuditReadinessStatus = "ready" | "partially_ready" | "blocked";

type EvidenceSourceType =
  | "document"
  | "work_order"
  | "approval"
  | "post_maintenance_verification"
  | "decision"
  | "compliance_rule";

type AuditEvidenceReference = {
  evidence_id: string;
  source_type: EvidenceSourceType;
  title: string;
  status: EvidenceStatus;
  source_id?: string | null;
  immutable_hash?: string | null;
  explanation: string;
};

type ComplianceRequirementPackage = {
  requirement_id: string;
  title: string;
  category: string;
  severity: "critical" | "high" | "medium" | "low";
  status: EvidenceStatus;
  explanation: string;
  applicable_documents: AuditEvidenceReference[];
  completed_work_orders: AuditEvidenceReference[];
  approvals: AuditEvidenceReference[];
  post_maintenance_verifications: AuditEvidenceReference[];
  missing_evidence: AuditEvidenceReference[];
  decision_history: AuditEvidenceReference[];
  readiness_impact: string;
};

type ComplianceAuditPackageSummary = {
  asset_id: string;
  package_id: string;
  package_version: string;
  generated_at: string;
  readiness_status: AuditReadinessStatus;
  readiness_score: number;
  requirement_count: number;
  satisfied_count: number;
  failed_count: number;
  missing_count: number;
  warning_count: number;
  immutable_evidence_hash: string;
};

type ComplianceAuditPackage = {
  summary: ComplianceAuditPackageSummary;
  requirements: ComplianceRequirementPackage[];
  applicable_documents: AuditEvidenceReference[];
  completed_work_orders: AuditEvidenceReference[];
  approvals: AuditEvidenceReference[];
  post_maintenance_verifications: AuditEvidenceReference[];
  missing_evidence: AuditEvidenceReference[];
  decision_history: AuditEvidenceReference[];
  failed_requirement_explanations: string[];
  package_notes: string[];
};

function label(value: string): string {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function shortHash(value?: string | null): string {
  if (!value) {
    return "Not available";
  }

  return `${value.slice(0, 10)}...${value.slice(-6)}`;
}

function fallbackPackage(): ComplianceAuditPackage {
  return {
    summary: {
      asset_id: "P-101",
      package_id: "AUDIT-P-101-DEMO",
      package_version: "audit-ready-compliance-evidence-package-v1.0.0",
      generated_at: "2026-07-11T10:00:00+00:00",
      readiness_status: "blocked",
      readiness_score: 66.67,
      requirement_count: 3,
      satisfied_count: 2,
      failed_count: 0,
      missing_count: 1,
      warning_count: 0,
      immutable_evidence_hash:
        "9f3b8c8b0b20d28a509evidencepackagehashdemo9f3b8c8b0b20d28a509",
    },
    requirements: [
      {
        requirement_id: "P101-DOC-CONTROL",
        title: "Applicable maintenance procedure must be linked",
        category: "document_control",
        severity: "high",
        status: "satisfied",
        explanation:
          "P-101 maintenance procedure and LOTO checklist are linked.",
        applicable_documents: [
          {
            evidence_id: "EV-DOC-SOP-P101-001",
            source_type: "document",
            source_id: "SOP-P101-001",
            title: "P-101 maintenance procedure and LOTO checklist",
            status: "satisfied",
            immutable_hash:
              "docp1010019f3b8c8b0b20d28a509evidencehashdemo000001",
            explanation:
              "Applicable controlled document linked to P-101 maintenance.",
          },
        ],
        completed_work_orders: [],
        approvals: [],
        post_maintenance_verifications: [],
        missing_evidence: [],
        decision_history: [],
        readiness_impact: "Supports compliance readiness.",
      },
      {
        requirement_id: "P101-WO-CLOSURE",
        title: "Corrective maintenance work order must be completed",
        category: "maintenance_execution",
        severity: "high",
        status: "satisfied",
        explanation:
          "A completed P-101 work order is available for audit review.",
        applicable_documents: [],
        completed_work_orders: [
          {
            evidence_id: "EV-WO-WO-P101-COMPLETE-001",
            source_type: "work_order",
            source_id: "WO-P101-COMPLETE-001",
            title: "Conduct post-maintenance vibration test",
            status: "satisfied",
            immutable_hash:
              "wop101complete9f3b8c8b0b20d28a509evidencehashdemo001",
            explanation:
              "Completed or recovery-stage work order evidence for P-101.",
          },
        ],
        approvals: [
          {
            evidence_id: "EV-APPROVAL-APP-P101-001",
            source_type: "approval",
            source_id: "APP-P101-001",
            title: "P-101 high-risk maintenance approval",
            status: "satisfied",
            immutable_hash:
              "approvalp1019f3b8c8b0b20d28a509evidencehashdemo0001",
            explanation:
              "High-risk P-101 maintenance approval is available.",
          },
        ],
        post_maintenance_verifications: [],
        missing_evidence: [],
        decision_history: [],
        readiness_impact: "Resolved work orders improve audit readiness.",
      },
      {
        requirement_id: "P101-PMV-REQUIRED",
        title: "Post-maintenance verification must confirm recovery",
        category: "maintenance_recovery",
        severity: "high",
        status: "missing",
        explanation:
          "Post-maintenance recovery cannot be accepted because successful verification evidence is missing.",
        applicable_documents: [],
        completed_work_orders: [],
        approvals: [],
        post_maintenance_verifications: [],
        missing_evidence: [
          {
            evidence_id: "P-101-PMV-MISSING",
            source_type: "compliance_rule",
            source_id: "P-101-PMV-MISSING",
            title: "Post-maintenance verification missing",
            status: "missing",
            immutable_hash:
              "missingpmvp1019f3b8c8b0b20d28a509evidencehashdemo01",
            explanation:
              "P-101 has completed maintenance evidence, but no successful post-maintenance verification evidence.",
          },
        ],
        decision_history: [],
        readiness_impact: "Prevents full compliance readiness.",
      },
    ],
    applicable_documents: [
      {
        evidence_id: "EV-DOC-SOP-P101-001",
        source_type: "document",
        source_id: "SOP-P101-001",
        title: "P-101 maintenance procedure and LOTO checklist",
        status: "satisfied",
        immutable_hash:
          "docp1010019f3b8c8b0b20d28a509evidencehashdemo000001",
        explanation: "Applicable controlled document linked to P-101.",
      },
    ],
    completed_work_orders: [
      {
        evidence_id: "EV-WO-WO-P101-COMPLETE-001",
        source_type: "work_order",
        source_id: "WO-P101-COMPLETE-001",
        title: "Conduct post-maintenance vibration test",
        status: "satisfied",
        immutable_hash:
          "wop101complete9f3b8c8b0b20d28a509evidencehashdemo001",
        explanation: "Completed work order evidence included.",
      },
    ],
    approvals: [
      {
        evidence_id: "EV-APPROVAL-APP-P101-001",
        source_type: "approval",
        source_id: "APP-P101-001",
        title: "P-101 high-risk maintenance approval",
        status: "satisfied",
        immutable_hash:
          "approvalp1019f3b8c8b0b20d28a509evidencehashdemo0001",
        explanation: "Approval evidence included.",
      },
    ],
    post_maintenance_verifications: [],
    missing_evidence: [
      {
        evidence_id: "P-101-PMV-MISSING",
        source_type: "compliance_rule",
        source_id: "P-101-PMV-MISSING",
        title: "Post-maintenance verification missing",
        status: "missing",
        immutable_hash:
          "missingpmvp1019f3b8c8b0b20d28a509evidencehashdemo01",
        explanation:
          "Missing successful post-maintenance verification blocks full compliance readiness.",
      },
    ],
    decision_history: [
      {
        evidence_id: "EV-DECISION-P101-PACKAGE",
        source_type: "decision",
        source_id: "P-101-AUDIT-PACKAGE",
        title: "Compliance audit package generated",
        status: "satisfied",
        immutable_hash:
          "decisionp1019f3b8c8b0b20d28a509evidencehashdemo0001",
        explanation:
          "Audit package generated using documents, work orders, approvals, and verification evidence.",
      },
      {
        evidence_id: "EV-DECISION-P101-PMV-BLOCK",
        source_type: "decision",
        source_id: "P-101-PMV-BLOCK",
        title: "Missing verification blocks readiness",
        status: "failed",
        immutable_hash: null,
        explanation:
          "Completed maintenance is not enough for full compliance readiness without successful post-maintenance verification.",
      },
    ],
    failed_requirement_explanations: [
      "P101-PMV-REQUIRED: Post-maintenance recovery cannot be accepted because successful verification evidence is missing.",
    ],
    package_notes: [
      "The package hash is computed from canonical evidence content so audit reviewers can detect changes.",
      "Resolved and verified work orders improve readiness; missing post-maintenance verification blocks full compliance readiness.",
    ],
  };
}

function evidenceListTitle(sourceType: EvidenceSourceType): string {
  if (sourceType === "post_maintenance_verification") {
    return "Post-maintenance verification";
  }

  return label(sourceType);
}

export function ComplianceAuditPackagePanel() {
  const [assetId, setAssetId] = useState("P-101");
  const [auditPackage, setAuditPackage] = useState<ComplianceAuditPackage>(() =>
    fallbackPackage(),
  );
  const [status, setStatus] = useState(
    "Using local P-101 audit package preview.",
  );

  const blockedRequirements = useMemo(
    () =>
      auditPackage.requirements.filter((requirement) =>
        ["failed", "missing"].includes(requirement.status),
      ),
    [auditPackage.requirements],
  );

  async function loadAuditPackage() {
    setStatus(`Loading audit package for ${assetId}...`);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
      const response = await fetch(
        `${baseUrl}/compliance/audit-packages/assets/${encodeURIComponent(assetId)}`,
        {
          headers: {
            Accept: "application/json",
          },
        },
      );

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload = (await response.json()) as ComplianceAuditPackage;
      setAuditPackage(payload);
      setStatus(`Loaded immutable audit package ${payload.summary.package_id}.`);
    } catch {
      setAuditPackage(fallbackPackage());
      setStatus(
        "Backend unavailable or authentication required. Showing local P-101 audit package preview.",
      );
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Compliance evidence package
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">
          Audit-ready compliance package
        </h1>
        <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-600">
          This package consolidates requirement status, applicable documents,
          completed work orders, approvals, post-maintenance verification,
          missing evidence, decision history, and an immutable evidence hash.
        </p>

        <div className="mt-5 flex flex-col gap-3 sm:flex-row">
          <input
            value={assetId}
            onChange={(event) => setAssetId(event.target.value)}
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-slate-500"
            aria-label="Asset ID"
          />
          <button
            type="button"
            onClick={loadAuditPackage}
            className="rounded-xl bg-slate-950 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-800"
          >
            Load audit package
          </button>
        </div>

        <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          {status}
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Readiness summary
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            {label(auditPackage.summary.readiness_status)}
          </h2>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-3xl font-semibold text-slate-950">
                {auditPackage.summary.readiness_score}
              </p>
              <p className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
                Readiness score
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-3xl font-semibold text-slate-950">
                {auditPackage.summary.requirement_count}
              </p>
              <p className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
                Requirements
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-3xl font-semibold text-slate-950">
                {auditPackage.summary.satisfied_count}
              </p>
              <p className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
                Satisfied
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-3xl font-semibold text-slate-950">
                {auditPackage.summary.missing_count}
              </p>
              <p className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
                Missing
              </p>
            </div>
          </div>

          <div className="mt-6 space-y-3 text-sm text-slate-700">
            <p>
              <span className="font-semibold">Package:</span>{" "}
              {auditPackage.summary.package_id}
            </p>
            <p>
              <span className="font-semibold">Asset:</span>{" "}
              {auditPackage.summary.asset_id}
            </p>
            <p>
              <span className="font-semibold">Immutable hash:</span>{" "}
              {shortHash(auditPackage.summary.immutable_evidence_hash)}
            </p>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Failed requirement explanations
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Why full compliance is blocked
          </h2>

          <div className="mt-6 space-y-3">
            {blockedRequirements.length === 0 ? (
              <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
                No failed or missing requirements. The package is audit-ready.
              </p>
            ) : (
              blockedRequirements.map((requirement) => (
                <div
                  key={requirement.requirement_id}
                  className="rounded-xl border border-slate-200 p-4"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {label(requirement.status)}
                    </span>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {label(requirement.severity)}
                    </span>
                  </div>
                  <p className="mt-3 font-semibold text-slate-950">
                    {requirement.requirement_id}: {requirement.title}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    {requirement.explanation}
                  </p>
                  <p className="mt-2 text-sm font-medium text-slate-700">
                    {requirement.readiness_impact}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Requirement status
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-slate-950">
          Evidence-backed controls
        </h2>

        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Requirement</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Missing evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {auditPackage.requirements.map((requirement) => (
                <tr key={requirement.requirement_id}>
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-950">
                      {requirement.requirement_id}
                    </p>
                    <p className="mt-1 text-slate-600">{requirement.title}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {label(requirement.category)}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {label(requirement.severity)}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {label(requirement.status)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {requirement.missing_evidence.length}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        {[
          ...auditPackage.applicable_documents,
          ...auditPackage.completed_work_orders,
          ...auditPackage.approvals,
          ...auditPackage.post_maintenance_verifications,
          ...auditPackage.missing_evidence,
        ].map((evidence) => (
          <div
            key={evidence.evidence_id}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              {evidenceListTitle(evidence.source_type)}
            </p>
            <h3 className="mt-2 font-semibold text-slate-950">
              {evidence.title}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {evidence.explanation}
            </p>
            <p className="mt-4 text-xs text-slate-500">
              Evidence ID: {evidence.evidence_id}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Hash: {shortHash(evidence.immutable_hash)}
            </p>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Decision history
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-slate-950">
          Audit decisions
        </h2>

        <div className="mt-6 space-y-3">
          {auditPackage.decision_history.map((decision) => (
            <div
              key={decision.evidence_id}
              className="rounded-xl border border-slate-200 p-4"
            >
              <p className="font-semibold text-slate-950">{decision.title}</p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {decision.explanation}
              </p>
              <p className="mt-2 text-xs text-slate-500">
                Status: {label(decision.status)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}