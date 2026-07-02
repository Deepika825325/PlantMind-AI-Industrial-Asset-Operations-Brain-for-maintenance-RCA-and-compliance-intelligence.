"use client";

import { useEffect, useState } from "react";

import KnowledgeGraphCanvas from "@/components/graph/KnowledgeGraphCanvas";
import { apiGet } from "@/lib/api";
import type { KnowledgeGraphResponse } from "@/lib/types";

export default function KnowledgeGraphPage() {
  const [graph, setGraph] =
    useState<KnowledgeGraphResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        setError("");

        const result =
          await apiGet<KnowledgeGraphResponse>(
            "/knowledge-graph"
          );

        setGraph(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load knowledge graph"
        );
      } finally {
        setLoading(false);
      }
    }

    loadGraph();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-[1600px] px-6 py-10">
        <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
          Visual Knowledge Graph
        </p>

        <h1 className="mt-4 text-4xl font-semibold tracking-tight">
          Asset Relationship Intelligence
        </h1>

        <p className="mt-3 max-w-3xl text-slate-400">
          Explore relationships between assets, documents,
          sensor signals, compliance gaps, work orders,
          instruments, valves, and process connections.
        </p>

        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            Loading visual knowledge graph...
          </div>
        )}

        {error && (
          <div className="mt-8 rounded-2xl border border-red-800 bg-red-950/40 p-6 text-red-300">
            {error}
          </div>
        )}

        {graph && (
          <>
            <div className="mt-8 grid gap-4 md:grid-cols-4">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Total Nodes
                </p>

                <p className="mt-3 text-3xl font-semibold text-cyan-400">
                  {graph.node_count}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Relationships
                </p>

                <p className="mt-3 text-3xl font-semibold text-cyan-400">
                  {graph.edge_count}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Asset Nodes
                </p>

                <p className="mt-3 text-3xl font-semibold text-emerald-400">
                  {
                    graph.nodes.filter(
                      (node) => node.type === "Asset"
                    ).length
                  }
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Evidence Nodes
                </p>

                <p className="mt-3 text-3xl font-semibold text-amber-400">
                  {
                    graph.nodes.filter(
                      (node) =>
                        node.type === "Document" ||
                        node.type === "ComplianceGap" ||
                        node.type === "WorkOrder"
                    ).length
                  }
                </p>
              </div>
            </div>

            <div className="mt-8">
              <KnowledgeGraphCanvas graph={graph} />
            </div>
          </>
        )}
      </section>
    </main>
  );
}