"use client";

import { useCallback, useEffect, useState } from "react";

import CausalChain from "@/components/rca/CausalChain";
import CorrectiveActions from "@/components/rca/CorrectiveActions";
import EvidenceTimeline from "@/components/rca/EvidenceTimeline";
import IncidentSelector from "@/components/rca/IncidentSelector";
import IncidentSummary from "@/components/rca/IncidentSummary";
import RootCauseRanking from "@/components/rca/RootCauseRanking";
import {
  getRcaCase,
  getRcaCases,
  getRcaStatistics,
} from "@/lib/api";
import type {
  RcaCase,
  RcaCaseSummary,
  RcaStatistics,
} from "@/lib/types";

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred while loading RCA data.";
}

export default function RcaWorkspacePage() {
  const [caseSummaries, setCaseSummaries] = useState<
    RcaCaseSummary[]
  >([]);

  const [statistics, setStatistics] =
    useState<RcaStatistics | null>(null);

  const [selectedCaseId, setSelectedCaseId] =
    useState("");

  const [selectedCase, setSelectedCase] =
    useState<RcaCase | null>(null);

  const [isWorkspaceLoading, setIsWorkspaceLoading] =
    useState(true);

  const [isCaseLoading, setIsCaseLoading] =
    useState(false);

  const [workspaceError, setWorkspaceError] =
    useState<string | null>(null);

  const [caseError, setCaseError] =
    useState<string | null>(null);

  const loadWorkspace = useCallback(async () => {
    setIsWorkspaceLoading(true);
    setWorkspaceError(null);

    try {
      const [caseListResponse, statisticsResponse] =
        await Promise.all([
          getRcaCases(),
          getRcaStatistics(),
        ]);

      setCaseSummaries(caseListResponse.cases);
      setStatistics(statisticsResponse);

      setSelectedCaseId((currentCaseId) => {
        const currentCaseStillExists =
          caseListResponse.cases.some(
            (incident) =>
              incident.case_id === currentCaseId
          );

        if (currentCaseStillExists) {
          return currentCaseId;
        }

        return (
          caseListResponse.cases[0]?.case_id ?? ""
        );
      });
    } catch (error) {
      setWorkspaceError(getErrorMessage(error));
      setCaseSummaries([]);
      setStatistics(null);
      setSelectedCaseId("");
      setSelectedCase(null);
    } finally {
      setIsWorkspaceLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);

  useEffect(() => {
    if (!selectedCaseId) {
      setSelectedCase(null);
      setCaseError(null);
      return;
    }

    let isCancelled = false;

    async function loadSelectedCase() {
      setIsCaseLoading(true);
      setCaseError(null);

      try {
        const incident = await getRcaCase(
          selectedCaseId
        );

        if (!isCancelled) {
          setSelectedCase(incident);
        }
      } catch (error) {
        if (!isCancelled) {
          setCaseError(getErrorMessage(error));
          setSelectedCase(null);
        }
      } finally {
        if (!isCancelled) {
          setIsCaseLoading(false);
        }
      }
    }

    void loadSelectedCase();

    return () => {
      isCancelled = true;
    };
  }, [selectedCaseId]);

  function handleSelectCase(caseId: string) {
    setSelectedCaseId(caseId);
    setSelectedCase(null);
    setCaseError(null);
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-[1600px] px-4 py-8 sm:px-6 lg:px-8">
        <header className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900">
          <div className="relative px-6 py-8 sm:px-8 lg:px-10 lg:py-10">
            <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />

            <div className="relative flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
              <div className="max-w-4xl">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-400">
                  PlantMind Intelligence
                </p>

                <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                  Root Cause Analysis Workspace
                </h1>

                <p className="mt-4 max-w-3xl text-base leading-8 text-slate-400">
                  Investigate industrial incidents using
                  traceable evidence, chronological event
                  reconstruction, causal reasoning, ranked
                  failure hypotheses and corrective actions.
                </p>
              </div>

              <button
                type="button"
                onClick={() => void loadWorkspace()}
                disabled={
                  isWorkspaceLoading || isCaseLoading
                }
                className="inline-flex items-center justify-center rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-5 py-3 text-sm font-semibold text-cyan-300 transition hover:border-cyan-400 hover:bg-cyan-500/15 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isWorkspaceLoading
                  ? "Refreshing..."
                  : "Refresh RCA Data"}
              </button>
            </div>
          </div>

          <div className="grid border-t border-slate-800 sm:grid-cols-2 xl:grid-cols-5">
            <div className="border-b border-slate-800 p-5 sm:border-r xl:border-b-0">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                RCA Cases
              </p>

              <p className="mt-2 text-3xl font-semibold text-white">
                {statistics?.total_cases ?? "—"}
              </p>
            </div>

            <div className="border-b border-slate-800 p-5 xl:border-b-0 xl:border-r">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Average Confidence
              </p>

              <p className="mt-2 text-3xl font-semibold text-cyan-300">
                {statistics
                  ? formatConfidence(
                      statistics.average_confidence
                    )
                  : "—"}
              </p>
            </div>

            <div className="border-b border-slate-800 p-5 sm:border-r xl:border-b-0">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Root Causes
              </p>

              <p className="mt-2 text-3xl font-semibold text-white">
                {statistics?.total_root_causes ?? "—"}
              </p>
            </div>

            <div className="border-b border-slate-800 p-5 xl:border-b-0 xl:border-r">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Corrective Actions
              </p>

              <p className="mt-2 text-3xl font-semibold text-white">
                {statistics?.total_corrective_actions ??
                  "—"}
              </p>
            </div>

            <div className="p-5">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Evidence Items
              </p>

              <p className="mt-2 text-3xl font-semibold text-white">
                {statistics?.total_evidence_items ?? "—"}
              </p>
            </div>
          </div>
        </header>

        {workspaceError && (
          <section className="mt-6 rounded-2xl border border-red-500/30 bg-red-500/10 p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-red-300">
              RCA workspace unavailable
            </p>

            <p className="mt-3 text-sm leading-6 text-red-100">
              {workspaceError}
            </p>

            <p className="mt-2 text-xs text-red-300/80">
              Confirm that the FastAPI backend is running
              on http://127.0.0.1:8000.
            </p>
          </section>
        )}

        {isWorkspaceLoading && (
          <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <div className="flex items-center gap-4">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-400" />

              <div>
                <p className="font-semibold text-slate-200">
                  Loading RCA workspace
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Retrieving incident summaries and RCA
                  statistics.
                </p>
              </div>
            </div>
          </section>
        )}

        {!isWorkspaceLoading &&
          !workspaceError &&
          caseSummaries.length === 0 && (
            <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
              <p className="text-lg font-semibold text-slate-200">
                No RCA cases available
              </p>

              <p className="mt-2 text-sm text-slate-500">
                Add an RCA case to the backend dataset and
                refresh this workspace.
              </p>
            </section>
          )}

        {!workspaceError &&
          caseSummaries.length > 0 && (
            <div className="mt-6 space-y-6">
              <IncidentSelector
                cases={caseSummaries}
                selectedCaseId={selectedCaseId}
                onSelectCase={handleSelectCase}
                disabled={
                  isWorkspaceLoading || isCaseLoading
                }
              />

              {caseError && (
                <section className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6">
                  <p className="text-sm font-semibold text-red-200">
                    The selected RCA case could not be
                    loaded.
                  </p>

                  <p className="mt-2 text-sm text-red-100">
                    {caseError}
                  </p>
                </section>
              )}

              {isCaseLoading && (
                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
                  <div className="flex items-center gap-4">
                    <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-400" />

                    <div>
                      <p className="font-semibold text-slate-200">
                        Loading incident analysis
                      </p>

                      <p className="mt-1 text-sm text-slate-500">
                        Retrieving evidence, causal steps and
                        corrective actions.
                      </p>
                    </div>
                  </div>
                </section>
              )}

              {!isCaseLoading &&
                !caseError &&
                selectedCase && (
                  <>
                    <IncidentSummary
                      incident={selectedCase}
                    />

                    <EvidenceTimeline
                      timeline={selectedCase.timeline}
                      evidence={selectedCase.evidence}
                    />

                    <CausalChain
                      steps={selectedCase.causal_chain}
                      evidence={selectedCase.evidence}
                    />

                    <RootCauseRanking
                      causes={selectedCase.root_causes}
                      evidence={selectedCase.evidence}
                    />

                    <CorrectiveActions
                      actions={
                        selectedCase.corrective_actions
                      }
                      rootCauses={
                        selectedCase.root_causes
                      }
                    />
                  </>
                )}
            </div>
          )}
      </div>
    </main>
  );
}