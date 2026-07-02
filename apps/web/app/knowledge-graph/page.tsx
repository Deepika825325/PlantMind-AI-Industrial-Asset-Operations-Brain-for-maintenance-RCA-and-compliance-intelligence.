"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet } from "@/lib/api";

type GraphNode = {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
};

type GraphEdge = {
  id: string;
  source: string;
  target: string;
  relationship: string;
  properties: Record<string, unknown>;
};

type KnowledgeGraphResponse = {
  artifact: string;
  generated_at: string;
  node_count: number;
  edge_count: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
};

const assetFilters = ["ALL", "P-101", "C-201", "HX-301"];

function getNodeTypeClass(type: string) {
  if (type === "Asset") {
    return "bg-cyan-100 text-cyan-700 border-cyan-200";
  }

  if (type === "Document") {
    return "bg-emerald-100 text-emerald-700 border-emerald-200";
  }

  if (type === "ComplianceGap") {
    return "bg-red-100 text-red-700 border-red-200";
  }

  if (type === "WorkOrder") {
    return "bg-amber-100 text-amber-700 border-amber-200";
  }

  if (type === "SensorSignal") {
    return "bg-violet-100 text-violet-700 border-violet-200";
  }

  if (type === "Instrument" || type === "Valve") {
    return "bg-blue-100 text-blue-700 border-blue-200";
  }

  return "bg-slate-100 text-slate-700 border-slate-200";
}

function getRelationshipClass(relationship: string) {
  if (relationship.includes("COMPLIANCE")) {
    return "text-red-300";
  }

  if (relationship.includes("WORK_ORDER")) {
    return "text-amber-300";
  }

  if (relationship.includes("SENSOR")) {
    return "text-violet-300";
  }

  if (relationship.includes("CONNECTED") || relationship.includes("FLOWS")) {
    return "text-cyan-300";
  }

  return "text-slate-300";
}

export default function KnowledgeGraphPage() {
  const [graph, setGraph] = useState<KnowledgeGraphResponse | null>(null);
  const [selectedAsset, setSelectedAsset] = useState("ALL");
  const [selectedNodeType, setSelectedNodeType] = useState("ALL");
  const [selectedRelationship, setSelectedRelationship] = useState("ALL");
  const [searchText, setSearchText] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        const result = await apiGet<KnowledgeGraphResponse>("/knowledge-graph");
        setGraph(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load graph");
      } finally {
        setLoading(false);
      }
    }

    loadGraph();
  }, []);

  const nodeTypes = useMemo(() => {
    if (!graph) {
      return [];
    }

    return Array.from(new Set(graph.nodes.map((node) => node.type))).sort();
  }, [graph]);

  const relationshipTypes = useMemo(() => {
    if (!graph) {
      return [];
    }

    return Array.from(new Set(graph.edges.map((edge) => edge.relationship))).sort();
  }, [graph]);

  const filteredGraph = useMemo(() => {
    if (!graph) {
      return {
        nodes: [],
        edges: [],
      };
    }

    let nodes = graph.nodes;
    let edges = graph.edges;

    if (selectedAsset !== "ALL") {
      edges = edges.filter(
        (edge) => edge.source === selectedAsset || edge.target === selectedAsset
      );

      const connectedNodeIds = new Set<string>([selectedAsset]);

      edges.forEach((edge) => {
        connectedNodeIds.add(edge.source);
        connectedNodeIds.add(edge.target);
      });

      nodes = nodes.filter((node) => connectedNodeIds.has(node.id));
    }

    if (selectedNodeType !== "ALL") {
      nodes = nodes.filter((node) => node.type === selectedNodeType);

      const allowedNodeIds = new Set(nodes.map((node) => node.id));

      edges = edges.filter(
        (edge) => allowedNodeIds.has(edge.source) || allowedNodeIds.has(edge.target)
      );
    }

    if (selectedRelationship !== "ALL") {
      edges = edges.filter((edge) => edge.relationship === selectedRelationship);

      const connectedNodeIds = new Set<string>();

      edges.forEach((edge) => {
        connectedNodeIds.add(edge.source);
        connectedNodeIds.add(edge.target);
      });

      nodes = nodes.filter((node) => connectedNodeIds.has(node.id));
    }

    const query = searchText.toLowerCase().trim();

    if (query) {
      nodes = nodes.filter(
        (node) =>
          node.id.toLowerCase().includes(query) ||
          node.label.toLowerCase().includes(query) ||
          node.type.toLowerCase().includes(query)
      );

      const visibleNodeIds = new Set(nodes.map((node) => node.id));

      edges = edges.filter(
        (edge) => visibleNodeIds.has(edge.source) || visibleNodeIds.has(edge.target)
      );
    }

    return {
      nodes,
      edges,
    };
  }, [graph, selectedAsset, selectedNodeType, selectedRelationship, searchText]);

  const assetNodes =
    graph?.nodes.filter((node) => node.type === "Asset") || [];

  const documentNodes =
    graph?.nodes.filter((node) => node.type === "Document") || [];

  const complianceGapNodes =
    graph?.nodes.filter((node) => node.type === "ComplianceGap") || [];

  const workOrderNodes =
    graph?.nodes.filter((node) => node.type === "WorkOrder") || [];

  const sensorNodes =
    graph?.nodes.filter((node) => node.type === "SensorSignal") || [];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Knowledge Graph
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Asset Relationship Intelligence
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Explore how PlantMind AI connects assets, documents, sensors,
            compliance gaps, work orders, valves, instruments, and P&ID process
            relationships.
          </p>
        </div>

        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            Loading knowledge graph...
          </div>
        )}

        {error && (
          <div className="mt-8 rounded-2xl border border-red-800 bg-red-950/40 p-6 text-red-300">
            {error}
          </div>
        )}

        {graph && (
          <>
            <div className="mt-8 grid gap-4 md:grid-cols-3 lg:grid-cols-6">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Nodes</p>
                <p className="mt-3 text-3xl font-semibold text-cyan-400">
                  {graph.node_count}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Edges</p>
                <p className="mt-3 text-3xl font-semibold text-cyan-400">
                  {graph.edge_count}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Assets</p>
                <p className="mt-3 text-3xl font-semibold">{assetNodes.length}</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Documents</p>
                <p className="mt-3 text-3xl font-semibold text-emerald-400">
                  {documentNodes.length}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Gaps</p>
                <p className="mt-3 text-3xl font-semibold text-red-400">
                  {complianceGapNodes.length}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Signals/WOs</p>
                <p className="mt-3 text-3xl font-semibold text-amber-400">
                  {sensorNodes.length + workOrderNodes.length}
                </p>
              </div>
            </div>

            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <label className="text-sm text-slate-400">Search Node</label>
                  <input
                    value={searchText}
                    onChange={(event) => setSearchText(event.target.value)}
                    placeholder="Search node ID, label, type..."
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <label className="text-sm text-slate-400">Asset Subgraph</label>
                  <select
                    value={selectedAsset}
                    onChange={(event) => setSelectedAsset(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    {assetFilters.map((asset) => (
                      <option key={asset} value={asset}>
                        {asset === "ALL" ? "All Assets" : asset}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-sm text-slate-400">Node Type</label>
                  <select
                    value={selectedNodeType}
                    onChange={(event) => setSelectedNodeType(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    <option value="ALL">All Node Types</option>
                    {nodeTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-sm text-slate-400">Relationship</label>
                  <select
                    value={selectedRelationship}
                    onChange={(event) => setSelectedRelationship(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    <option value="ALL">All Relationships</option>
                    {relationshipTypes.map((relationship) => (
                      <option key={relationship} value={relationship}>
                        {relationship}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-2">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Nodes</h2>
                  <span className="text-sm text-slate-500">
                    Showing {filteredGraph.nodes.length}
                  </span>
                </div>

                <div className="mt-6 max-h-[720px] space-y-4 overflow-y-auto pr-2">
                  {filteredGraph.nodes.map((node) => (
                    <div
                      key={node.id}
                      className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                    >
                      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                        <div>
                          <h3 className="font-semibold text-slate-100">
                            {node.label}
                          </h3>
                          <p className="mt-1 text-sm text-slate-500">{node.id}</p>
                        </div>

                        <span
                          className={`rounded-full border px-3 py-1 text-xs font-medium ${getNodeTypeClass(
                            node.type
                          )}`}
                        >
                          {node.type}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Relationships</h2>
                  <span className="text-sm text-slate-500">
                    Showing {filteredGraph.edges.length}
                  </span>
                </div>

                <div className="mt-6 max-h-[720px] space-y-4 overflow-y-auto pr-2">
                  {filteredGraph.edges.map((edge) => (
                    <div
                      key={edge.id}
                      className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                    >
                      <div className="grid gap-3 md:grid-cols-[1fr_auto_1fr] md:items-center">
                        <div className="rounded-xl bg-slate-900 p-3">
                          <p className="text-xs uppercase tracking-wider text-slate-500">
                            Source
                          </p>
                          <p className="mt-1 text-sm font-medium text-slate-200">
                            {edge.source}
                          </p>
                        </div>

                        <div className="text-center">
                          <p
                            className={`text-xs font-semibold uppercase tracking-wider ${getRelationshipClass(
                              edge.relationship
                            )}`}
                          >
                            {edge.relationship}
                          </p>
                          <p className="mt-1 text-slate-600">→</p>
                        </div>

                        <div className="rounded-xl bg-slate-900 p-3">
                          <p className="text-xs uppercase tracking-wider text-slate-500">
                            Target
                          </p>
                          <p className="mt-1 text-sm font-medium text-slate-200">
                            {edge.target}
                          </p>
                        </div>
                      </div>
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