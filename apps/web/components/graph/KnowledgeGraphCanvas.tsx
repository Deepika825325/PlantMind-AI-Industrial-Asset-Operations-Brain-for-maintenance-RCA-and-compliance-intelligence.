"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge as FlowEdge,
  type Node as FlowNode,
} from "@xyflow/react";

import type {
  GraphEdge,
  GraphNode,
  KnowledgeGraphResponse,
} from "@/lib/types";

type KnowledgeGraphCanvasProps = {
  graph: KnowledgeGraphResponse;
};

type FlowNodeData = {
  label: string;
  nodeType: string;
};

type PlantFlowNode = FlowNode<FlowNodeData>;
type PlantFlowEdge = FlowEdge;

const TYPE_ORDER = [
  "Project",
  "RiskClass",
  "Asset",
  "SensorSignal",
  "ComplianceGap",
  "WorkOrder",
  "Document",
  "Valve",
  "Instrument",
];

function getNodeColor(type: string) {
  if (type === "Asset") {
    return "#22d3ee";
  }

  if (type === "Document") {
    return "#34d399";
  }

  if (type === "ComplianceGap") {
    return "#f87171";
  }

  if (type === "WorkOrder") {
    return "#fbbf24";
  }

  if (type === "SensorSignal") {
    return "#a78bfa";
  }

  if (type === "Valve") {
    return "#38bdf8";
  }

  if (type === "Instrument") {
    return "#818cf8";
  }

  if (type === "RiskClass") {
    return "#fb7185";
  }

  return "#94a3b8";
}

function getNodeStyle(type: string) {
  const color = getNodeColor(type);

  return {
    border: `2px solid ${color}`,
    background: "#0f172a",
    color: "#f8fafc",
    borderRadius: "14px",
    width: 220,
    padding: "12px",
    fontSize: "12px",
    boxShadow: `0 0 20px ${color}22`,
  };
}

function buildFlowElements(
  graphNodes: GraphNode[],
  graphEdges: GraphEdge[]
): {
  nodes: PlantFlowNode[];
  edges: PlantFlowEdge[];
} {
  const groupedNodes = new Map<string, GraphNode[]>();

  graphNodes.forEach((node) => {
    const existing = groupedNodes.get(node.type) || [];
    existing.push(node);
    groupedNodes.set(node.type, existing);
  });

  const availableTypes = Array.from(groupedNodes.keys()).sort(
    (first, second) => {
      const firstIndex = TYPE_ORDER.indexOf(first);
      const secondIndex = TYPE_ORDER.indexOf(second);

      if (firstIndex === -1 && secondIndex === -1) {
        return first.localeCompare(second);
      }

      if (firstIndex === -1) {
        return 1;
      }

      if (secondIndex === -1) {
        return -1;
      }

      return firstIndex - secondIndex;
    }
  );

  const nodes: PlantFlowNode[] = [];

  availableTypes.forEach((type, columnIndex) => {
    const typeNodes = groupedNodes.get(type) || [];

    typeNodes.forEach((node, rowIndex) => {
      nodes.push({
        id: node.id,
        position: {
          x: columnIndex * 300,
          y: rowIndex * 130,
        },
        data: {
          label: node.label,
          nodeType: node.type,
        },
        style: getNodeStyle(node.type),
      });
    });
  });

  const showEdgeLabels = graphEdges.length <= 35;

  const edges: PlantFlowEdge[] = graphEdges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: showEdgeLabels ? edge.relationship : undefined,
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
    style: {
      stroke: "#64748b",
      strokeWidth: 1.5,
    },
    labelStyle: {
      fill: "#cbd5e1",
      fontSize: 9,
    },
  }));

  return {
    nodes,
    edges,
  };
}

function formatProperty(value: unknown) {
  if (value === null || value === undefined) {
    return "Not available";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

export default function KnowledgeGraphCanvas({
  graph,
}: KnowledgeGraphCanvasProps) {
  const [selectedAsset, setSelectedAsset] = useState("ALL");
  const [selectedNodeType, setSelectedNodeType] = useState("ALL");
  const [selectedRelationship, setSelectedRelationship] =
    useState("ALL");
  const [searchText, setSearchText] = useState("");
  const [selectedNode, setSelectedNode] =
    useState<GraphNode | null>(null);

  const nodeTypes = useMemo(
    () =>
      Array.from(
        new Set(graph.nodes.map((node) => node.type))
      ).sort(),
    [graph.nodes]
  );

  const relationshipTypes = useMemo(
    () =>
      Array.from(
        new Set(
          graph.edges.map((edge) => edge.relationship)
        )
      ).sort(),
    [graph.edges]
  );

  const assetIds = useMemo(
    () =>
      graph.nodes
        .filter((node) => node.type === "Asset")
        .map((node) => node.id)
        .sort(),
    [graph.nodes]
  );

  const filteredGraph = useMemo(() => {
    let activeEdges = [...graph.edges];
    let activeNodeIds = new Set(
      graph.nodes.map((node) => node.id)
    );

    if (selectedAsset !== "ALL") {
      activeEdges = activeEdges.filter(
        (edge) =>
          edge.source === selectedAsset ||
          edge.target === selectedAsset
      );

      activeNodeIds = new Set([selectedAsset]);

      activeEdges.forEach((edge) => {
        activeNodeIds.add(edge.source);
        activeNodeIds.add(edge.target);
      });
    }

    if (selectedRelationship !== "ALL") {
      activeEdges = activeEdges.filter(
        (edge) =>
          edge.relationship === selectedRelationship
      );

      activeNodeIds = new Set();

      activeEdges.forEach((edge) => {
        activeNodeIds.add(edge.source);
        activeNodeIds.add(edge.target);
      });
    }

    if (selectedNodeType !== "ALL") {
      const anchorIds = new Set(
        graph.nodes
          .filter(
            (node) =>
              activeNodeIds.has(node.id) &&
              node.type === selectedNodeType
          )
          .map((node) => node.id)
      );

      activeEdges = activeEdges.filter(
        (edge) =>
          anchorIds.has(edge.source) ||
          anchorIds.has(edge.target)
      );

      activeNodeIds = new Set(anchorIds);

      activeEdges.forEach((edge) => {
        activeNodeIds.add(edge.source);
        activeNodeIds.add(edge.target);
      });
    }

    const query = searchText.trim().toLowerCase();

    if (query) {
      const matchingIds = new Set(
        graph.nodes
          .filter(
            (node) =>
              activeNodeIds.has(node.id) &&
              (
                node.id.toLowerCase().includes(query) ||
                node.label.toLowerCase().includes(query) ||
                node.type.toLowerCase().includes(query)
              )
          )
          .map((node) => node.id)
      );

      activeEdges = activeEdges.filter(
        (edge) =>
          matchingIds.has(edge.source) ||
          matchingIds.has(edge.target)
      );

      activeNodeIds = new Set(matchingIds);

      activeEdges.forEach((edge) => {
        activeNodeIds.add(edge.source);
        activeNodeIds.add(edge.target);
      });
    }

    const nodes = graph.nodes.filter((node) =>
      activeNodeIds.has(node.id)
    );

    const visibleIds = new Set(
      nodes.map((node) => node.id)
    );

    const edges = activeEdges.filter(
      (edge) =>
        visibleIds.has(edge.source) &&
        visibleIds.has(edge.target)
    );

    return {
      nodes,
      edges,
    };
  }, [
    graph,
    selectedAsset,
    selectedNodeType,
    selectedRelationship,
    searchText,
  ]);

  const flowElements = useMemo(
    () =>
      buildFlowElements(
        filteredGraph.nodes,
        filteredGraph.edges
      ),
    [filteredGraph]
  );

  const [nodes, setNodes, onNodesChange] =
    useNodesState<PlantFlowNode>(flowElements.nodes);

  const [edges, setEdges, onEdgesChange] =
    useEdgesState<PlantFlowEdge>(flowElements.edges);

  useEffect(() => {
    setNodes(flowElements.nodes);
    setEdges(flowElements.edges);
  }, [flowElements, setEdges, setNodes]);

  const selectedNodeRelationships = useMemo(() => {
    if (!selectedNode) {
      return [];
    }

    return graph.edges.filter(
      (edge) =>
        edge.source === selectedNode.id ||
        edge.target === selectedNode.id
    );
  }, [graph.edges, selectedNode]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <label className="text-sm text-slate-400">
              Search node
            </label>

            <input
              value={searchText}
              onChange={(event) =>
                setSearchText(event.target.value)
              }
              placeholder="ID, label or node type"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label className="text-sm text-slate-400">
              Asset subgraph
            </label>

            <select
              value={selectedAsset}
              onChange={(event) =>
                setSelectedAsset(event.target.value)
              }
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            >
              <option value="ALL">All assets</option>

              {assetIds.map((assetId) => (
                <option key={assetId} value={assetId}>
                  {assetId}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-400">
              Node type
            </label>

            <select
              value={selectedNodeType}
              onChange={(event) =>
                setSelectedNodeType(event.target.value)
              }
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            >
              <option value="ALL">All node types</option>

              {nodeTypes.map((nodeType) => (
                <option key={nodeType} value={nodeType}>
                  {nodeType}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-400">
              Relationship
            </label>

            <select
              value={selectedRelationship}
              onChange={(event) =>
                setSelectedRelationship(event.target.value)
              }
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            >
              <option value="ALL">
                All relationships
              </option>

              {relationshipTypes.map((relationship) => (
                <option
                  key={relationship}
                  value={relationship}
                >
                  {relationship}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
          <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
            <h2 className="font-semibold">
              Interactive Graph
            </h2>

            <p className="text-sm text-slate-500">
              {filteredGraph.nodes.length} nodes ·{" "}
              {filteredGraph.edges.length} edges
            </p>
          </div>

          <div className="h-[720px]">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={(_, flowNode) => {
                const originalNode = graph.nodes.find(
                  (node) => node.id === flowNode.id
                );

                setSelectedNode(originalNode || null);
              }}
              fitView
              fitViewOptions={{
                padding: 0.2,
              }}
              minZoom={0.15}
              maxZoom={2}
              nodesConnectable={false}
            >
              <MiniMap
                nodeColor={(node) =>
                  getNodeColor(
                    String(node.data.nodeType)
                  )
                }
                maskColor="rgba(2, 6, 23, 0.75)"
              />

              <Controls />

              <Background gap={24} size={1} />
            </ReactFlow>
          </div>
        </div>

        <aside className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          {!selectedNode && (
            <>
              <h2 className="text-xl font-semibold">
                Node Inspector
              </h2>

              <p className="mt-4 text-sm leading-6 text-slate-500">
                Click a graph node to inspect its metadata,
                connected entities, and relationships.
              </p>
            </>
          )}

          {selectedNode && (
            <>
              <p className="text-xs font-medium uppercase tracking-[0.25em] text-cyan-400">
                {selectedNode.type}
              </p>

              <h2 className="mt-3 text-2xl font-semibold">
                {selectedNode.label}
              </h2>

              <p className="mt-2 break-all text-sm text-slate-500">
                {selectedNode.id}
              </p>

              <div className="mt-6">
                <h3 className="font-semibold">
                  Properties
                </h3>

                <div className="mt-3 space-y-3">
                  {Object.entries(
                    selectedNode.properties
                  ).map(([key, value]) => (
                    <div
                      key={key}
                      className="rounded-xl border border-slate-800 bg-slate-950 p-3"
                    >
                      <p className="text-xs uppercase tracking-wider text-slate-500">
                        {key.replaceAll("_", " ")}
                      </p>

                      <p className="mt-2 break-words text-sm text-slate-300">
                        {formatProperty(value)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-6">
                <h3 className="font-semibold">
                  Direct Relationships
                </h3>

                <div className="mt-3 space-y-3">
                  {selectedNodeRelationships.map(
                    (relationship) => (
                      <div
                        key={relationship.id}
                        className="rounded-xl border border-slate-800 bg-slate-950 p-3 text-sm"
                      >
                        <p className="text-slate-300">
                          {relationship.source}
                        </p>

                        <p className="my-1 text-xs font-medium text-cyan-400">
                          {relationship.relationship}
                        </p>

                        <p className="text-slate-300">
                          {relationship.target}
                        </p>
                      </div>
                    )
                  )}
                </div>
              </div>
            </>
          )}
        </aside>
      </div>
    </div>
  );
}