"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import AssetAuditSummary from "@/components/compliance/AssetAuditSummary";
import AuditReadinessScore from "@/components/compliance/AuditReadinessScore";
import ComplianceFilters from "@/components/compliance/ComplianceFilters";
import ComplianceGapList from "@/components/compliance/ComplianceGapList";
import ComplianceKpiCards from "@/components/compliance/ComplianceKpiCards";
import EvidencePackageView from "@/components/compliance/EvidencePackageView";
import GapSeverityDistribution from "@/components/compliance/GapSeverityDistribution";
import DecisionTracePanel from "@/components/trust/DecisionTracePanel";
import { apiGet } from "@/lib/api";

import type {
  ComplianceAuditPackage,
  ComplianceFilterState,
  ComplianceGapsResponse,
  ComplianceOverview,
  ComplianceRulesResponse,
} from "@/lib/types";

const initialFilters: ComplianceFilterState = {
  assetId: "ALL",
  severity: "ALL",
  status: "ALL",
  ruleId: "ALL",
  evidenceAvailability: "ALL",
  auditPackage: "ALL",
};

function buildGapQuery(
  filters: ComplianceFilterState
) {
  const query = new URLSearchParams();

  if (filters.assetId !== "ALL") {
    query.set("asset_id", filters.assetId);
  }

  if (filters.severity !== "ALL") {
    query.set("severity", filters.severity);
  }

  if (filters.status !== "ALL") {
    query.set("status", filters.status);
  }

  if (filters.ruleId !== "ALL") {
    query.set("rule_id", filters.ruleId);
  }

  if (filters.evidenceAvailability !== "ALL") {
    query.set(
      "evidence_availability",
      filters.evidenceAvailability
    );
  }

  const queryString = query.toString();

  return queryString
    ? `/compliance/gaps?${queryString}`
    : "/compliance/gaps";
}

export default function CompliancePage() {
  const [overview, setOverview] =
    useState<ComplianceOverview | null>(null);

  const [rulesData, setRulesData] =
    useState<ComplianceRulesResponse | null>(null);

  const [gapsData, setGapsData] =
    useState<ComplianceGapsResponse | null>(null);

  const [auditPackage, setAuditPackage] =
    useState<ComplianceAuditPackage | null>(null);

  const [filters, setFilters] =
    useState<ComplianceFilterState>(
      initialFilters
    );

  const [selectedAssetId, setSelectedAssetId] =
    useState("");

  const [loadingOverview, setLoadingOverview] =
    useState(true);

  const [loadingGaps, setLoadingGaps] =
    useState(true);

  const [loadingPackage, setLoadingPackage] =
    useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadInitialData() {
      try {
        setLoadingOverview(true);
        setError("");

        const [overviewResult, rulesResult] =
          await Promise.all([
            apiGet<ComplianceOverview>(
              "/compliance"
            ),
            apiGet<ComplianceRulesResponse>(
              "/compliance/rules"
            ),
          ]);

        setOverview(overviewResult);
        setRulesData(rulesResult);

        const searchParams =
          new URLSearchParams(
            window.location.search
          );

        const requestedAsset =
          searchParams.get("asset");

        const availableAssetIds =
          overviewResult.asset_compliance_summary.map(
            (asset) => asset.asset_id
          );

        const initialAsset =
          requestedAsset &&
          availableAssetIds.includes(
            requestedAsset.toUpperCase()
          )
            ? requestedAsset.toUpperCase()
            : availableAssetIds[0] || "";

        setSelectedAssetId(initialAsset);

        if (requestedAsset) {
          setFilters((currentFilters) => ({
            ...currentFilters,
            assetId: initialAsset,
          }));
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load compliance intelligence"
        );
      } finally {
        setLoadingOverview(false);
      }
    }

    loadInitialData();
  }, []);

  useEffect(() => {
    async function loadGaps() {
      try {
        setLoadingGaps(true);

        const result =
          await apiGet<ComplianceGapsResponse>(
            buildGapQuery(filters)
          );

        setGapsData(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load compliance gaps"
        );
      } finally {
        setLoadingGaps(false);
      }
    }

    loadGaps();
  }, [
    filters.assetId,
    filters.severity,
    filters.status,
    filters.ruleId,
    filters.evidenceAvailability,
  ]);

  useEffect(() => {
    if (!selectedAssetId) {
      setAuditPackage(null);
      return;
    }

    async function loadAuditPackage() {
      try {
        setLoadingPackage(true);

        const result =
          await apiGet<ComplianceAuditPackage>(
            `/compliance/assets/${encodeURIComponent(
              selectedAssetId
            )}/audit-package`
          );

        setAuditPackage(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load audit package"
        );
      } finally {
        setLoadingPackage(false);
      }
    }

    loadAuditPackage();
  }, [selectedAssetId]);

  const assetIds = useMemo(
    () =>
      overview?.asset_compliance_summary.map(
        (asset) => asset.asset_id
      ) || [],
    [overview]
  );

  const visibleAssets = useMemo(() => {
    if (!overview) {
      return [];
    }

    let assets =
      overview.asset_compliance_summary;

    if (filters.assetId !== "ALL") {
      assets = assets.filter(
        (asset) =>
          asset.asset_id === filters.assetId
      );
    }

    if (
      filters.auditPackage === "WITH_GAPS"
    ) {
      assets = assets.filter(
        (asset) => asset.open_gaps > 0
      );
    }

    if (filters.auditPackage === "READY") {
      assets = assets.filter(
        (asset) =>
          asset.audit_readiness_score >= 85 &&
          asset.open_gaps === 0
      );
    }

    return assets;
  }, [
    overview,
    filters.assetId,
    filters.auditPackage,
  ]);

  function handleFilterChange(
    nextFilters: ComplianceFilterState
  ) {
    setFilters(nextFilters);

    if (
      nextFilters.assetId !== "ALL" &&
      nextFilters.assetId !== selectedAssetId
    ) {
      handleAssetSelect(
        nextFilters.assetId
      );
    }
  }

  function handleAssetSelect(assetId: string) {
    setSelectedAssetId(assetId);

    setFilters((currentFilters) => ({
      ...currentFilters,
      assetId,
    }));

    const url = new URL(
      window.location.href
    );

    url.searchParams.set("asset", assetId);

    window.history.replaceState(
      {},
      "",
      url.toString()
    );
  }

  function handleResetFilters() {
    setFilters(initialFilters);

    if (
      overview?.asset_compliance_summary.length
    ) {
      const firstAsset =
        overview.asset_compliance_summary[0]
          .asset_id;

      setSelectedAssetId(firstAsset);

      const url = new URL(
        window.location.href
      );

      url.searchParams.delete("asset");

      window.history.replaceState(
        {},
        "",
        url.toString()
      );
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <header>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Compliance Intelligence
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Audit Readiness and Evidence Control
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Evaluate explicit compliance rules,
            identify missing evidence and connect
            every gap to assets, inspections,
            work orders, RCA cases and remediation
            actions.
          </p>
        </header>

        {error && (
          <section className="mt-8 rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-red-300">
            {error}
          </section>
        )}

        {loadingOverview && (
          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            Loading compliance intelligence...
          </section>
        )}

        {overview && rulesData && (
          <>
            <div className="mt-8">
              <ComplianceKpiCards
                overview={overview}
              />
            </div>

            <div className="mt-8">
              <ComplianceFilters
                filters={filters}
                assetIds={assetIds}
                rules={rulesData.rules}
                onChange={handleFilterChange}
                onReset={handleResetFilters}
              />
            </div>

            <div className="mt-8 grid gap-6 xl:grid-cols-[1fr_1.4fr]">
              <AssetAuditSummary
                assets={visibleAssets}
                selectedAssetId={
                  selectedAssetId
                }
                onSelect={handleAssetSelect}
              />

              <GapSeverityDistribution
                distribution={
                  overview.severity_distribution
                }
              />
            </div>

            {loadingPackage && (
              <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
                Loading asset audit package...
              </section>
            )}

            {!loadingPackage &&
              auditPackage && (
                <>
                  <div className="mt-8">
                    <AuditReadinessScore
                      score={
                        auditPackage.audit_readiness_score
                      }
                      breakdown={
                        auditPackage.scoring_breakdown
                      }
                    />
                  </div>

                  {auditPackage.decision_trace && (
                    <DecisionTracePanel
                      trace={
                        auditPackage.decision_trace
                      }
                      title="Compliance Decision Trace"
                      className="mt-8"
                    />
                  )}

                  <div className="mt-8">
                    <EvidencePackageView
                      auditPackage={
                        auditPackage
                      }
                    />
                  </div>
                </>
              )}

            <div className="mt-8">
              <ComplianceGapList
                gaps={gapsData?.gaps || []}
                loading={loadingGaps}
              />
            </div>
          </>
        )}
      </section>
    </main>
  );
}