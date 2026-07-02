"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { apiGet } from "@/lib/api";

type ComplianceGap = {
  gap_id: string;
  asset_id: string;
  requirement: string;
  expected_evidence: string;
  current_status: string;
  evidence_file: string;
  gap_severity: string;
  recommended_action: string;
  source_document: string;
};

type AssetComplianceSummary = {
  asset_id: string;
  total_gaps: number;
  high_severity_gaps: number;
  medium_severity_gaps: number;
  compliance_status: string;
  gap_ids: string[];
};

type ComplianceResponse = {
  artifact: string;
  generated_at: string;
  asset_compliance_summary: AssetComplianceSummary[];
  gaps: ComplianceGap[];
};

function getSeverityClass(severity: string) {
  if (severity === "High") {
    return "bg-red-100 text-red-700 border-red-200";
  }

  if (severity === "Medium") {
    return "bg-amber-100 text-amber-700 border-amber-200";
  }

  return "bg-slate-100 text-slate-700 border-slate-200";
}

function getStatusClass(status: string) {
  if (status === "Missing") {
    return "text-red-400";
  }

  if (status === "Delayed" || status === "Overdue") {
    return "text-amber-400";
  }

  return "text-slate-300";
}

export default function CompliancePage() {
  const searchParams = useSearchParams();
  const initialAsset = searchParams.get("asset") || "ALL";

  const [data, setData] = useState<ComplianceResponse | null>(null);
  const [selectedAsset, setSelectedAsset] = useState(initialAsset);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadCompliance() {
      try {
        setLoading(true);
        const result = await apiGet<ComplianceResponse>("/compliance");
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load compliance data");
      } finally {
        setLoading(false);
      }
    }

    loadCompliance();
  }, []);

  const filteredGaps = useMemo(() => {
    if (!data) {
      return [];
    }

    if (selectedAsset === "ALL") {
      return data.gaps;
    }

    return data.gaps.filter((gap) => gap.asset_id === selectedAsset);
  }, [data, selectedAsset]);

  const totalHighSeverity = data?.gaps.filter((gap) => gap.gap_severity === "High").length || 0;
  const totalMediumSeverity = data?.gaps.filter((gap) => gap.gap_severity === "Medium").length || 0;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Compliance Center
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Evidence Gap Detection
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Track missing, delayed, and overdue maintenance evidence across assets.
            This page converts raw compliance records into actionable evidence gaps.
          </p>
        </div>

        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            Loading compliance data...
          </div>
        )}

        {error && (
          <div className="mt-8 rounded-2xl border border-red-800 bg-red-950/40 p-6 text-red-300">
            {error}
          </div>
        )}

        {data && (
          <>
            <div className="mt-8 grid gap-4 md:grid-cols-4">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Total Gaps</p>
                <p className="mt-3 text-3xl font-semibold">{data.gaps.length}</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">High Severity</p>
                <p className="mt-3 text-3xl font-semibold text-red-400">
                  {totalHighSeverity}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Medium Severity</p>
                <p className="mt-3 text-3xl font-semibold text-amber-400">
                  {totalMediumSeverity}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Assets Affected</p>
                <p className="mt-3 text-3xl font-semibold text-cyan-400">
                  {data.asset_compliance_summary.length}
                </p>
              </div>
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-3">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <h2 className="text-xl font-semibold">Asset Compliance</h2>

                <div className="mt-5">
                  <label className="text-sm text-slate-400">Filter Asset</label>

                  <select
                    value={selectedAsset}
                    onChange={(event) => setSelectedAsset(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    <option value="ALL">All Assets</option>
                    <option value="P-101">P-101 Pump</option>
                    <option value="C-201">C-201 Compressor</option>
                    <option value="HX-301">HX-301 Heat Exchanger</option>
                  </select>
                </div>

                <div className="mt-6 space-y-4">
                  {data.asset_compliance_summary.map((summary) => (
                    <button
                      key={summary.asset_id}
                      onClick={() => setSelectedAsset(summary.asset_id)}
                      className="w-full rounded-2xl border border-slate-800 bg-slate-950 p-4 text-left transition hover:border-cyan-500"
                    >
                      <div className="flex items-center justify-between">
                        <p className="font-semibold">{summary.asset_id}</p>
                        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                          {summary.total_gaps} gaps
                        </span>
                      </div>

                      <p className="mt-2 text-sm text-slate-400">
                        {summary.compliance_status}
                      </p>

                      <div className="mt-3 flex gap-2 text-xs">
                        <span className="rounded-full bg-red-950 px-3 py-1 text-red-300">
                          High: {summary.high_severity_gaps}
                        </span>

                        <span className="rounded-full bg-amber-950 px-3 py-1 text-amber-300">
                          Medium: {summary.medium_severity_gaps}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Evidence Gaps</h2>
                  <span className="text-sm text-slate-500">
                    Showing {filteredGaps.length} gaps
                  </span>
                </div>

                <div className="mt-6 space-y-4">
                  {filteredGaps.map((gap) => (
                    <div
                      key={gap.gap_id}
                      className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                    >
                      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="text-lg font-semibold">{gap.gap_id}</h3>

                            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                              {gap.asset_id}
                            </span>

                            <span
                              className={`rounded-full border px-3 py-1 text-xs font-medium ${getSeverityClass(
                                gap.gap_severity
                              )}`}
                            >
                              {gap.gap_severity}
                            </span>
                          </div>

                          <p className="mt-3 text-slate-100">
                            {gap.requirement}
                          </p>
                        </div>

                        <p className={`text-sm font-medium ${getStatusClass(gap.current_status)}`}>
                          {gap.current_status}
                        </p>
                      </div>

                      <div className="mt-5 grid gap-4 md:grid-cols-2">
                        <div className="rounded-xl bg-slate-900 p-4">
                          <p className="text-xs uppercase tracking-wider text-slate-500">
                            Expected Evidence
                          </p>
                          <p className="mt-2 text-sm text-slate-300">
                            {gap.expected_evidence}
                          </p>
                        </div>

                        <div className="rounded-xl bg-slate-900 p-4">
                          <p className="text-xs uppercase tracking-wider text-slate-500">
                            Evidence File
                          </p>
                          <p className="mt-2 text-sm text-slate-300">
                            {gap.evidence_file || "Not available"}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5 rounded-xl border border-slate-800 bg-slate-900 p-4">
                        <p className="text-xs uppercase tracking-wider text-slate-500">
                          Recommended Action
                        </p>
                        <p className="mt-2 text-sm leading-6 text-slate-300">
                          {gap.recommended_action}
                        </p>
                      </div>

                      <p className="mt-4 text-xs text-slate-500">
                        Source: {gap.source_document}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </section>
    </main>
  );
}