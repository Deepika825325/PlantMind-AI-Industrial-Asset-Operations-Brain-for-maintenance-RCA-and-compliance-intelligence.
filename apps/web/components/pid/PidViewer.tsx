"use client";

import Image, { type ImageLoader } from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";

import { apiUrl } from "@/lib/api";
import type { PidNode, PidResponse } from "@/lib/types";

type PidViewerProps = {
  data: PidResponse;
};

const pidImageLoader: ImageLoader = ({
  src,
}) => src;

function getNodeClass(node: PidNode) {
  if (node.type === "Asset" && node.risk_level === "High") {
    return "border-red-400 bg-red-500 text-white shadow-red-500/30";
  }

  if (node.type === "Asset" && node.risk_level === "Medium") {
    return "border-amber-300 bg-amber-400 text-slate-950 shadow-amber-400/30";
  }

  if (node.type === "Instrument") {
    return "border-violet-300 bg-violet-500 text-white shadow-violet-500/30";
  }

  if (node.type === "Valve") {
    return "border-cyan-300 bg-cyan-500 text-slate-950 shadow-cyan-500/30";
  }

  return "border-slate-300 bg-slate-600 text-white shadow-slate-500/20";
}

function getStatusClass(status: string) {
  if (status === "Critical") {
    return "text-red-400";
  }

  if (status === "Warning") {
    return "text-amber-400";
  }

  return "text-emerald-400";
}

export default function PidViewer({ data }: PidViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [selectedNode, setSelectedNode] = useState<PidNode | null>(
    data.nodes.find((node) => node.id === "P-101") || null
  );
  const [selectedRisk, setSelectedRisk] = useState("ALL");

  const visibleNodes = useMemo(() => {
    if (selectedRisk === "ALL") {
      return data.nodes;
    }

    return data.nodes.filter(
      (node) => node.risk_level === selectedRisk
    );
  }, [data.nodes, selectedRisk]);

  const connectedRelationships = useMemo(() => {
    if (!selectedNode) {
      return [];
    }

    return data.connections.filter(
      (connection) =>
        connection.source === selectedNode.id ||
        connection.target === selectedNode.id
    );
  }, [data.connections, selectedNode]);

  function increaseZoom() {
    setZoom((current) => Math.min(current + 0.15, 2));
  }

  function decreaseZoom() {
    setZoom((current) => Math.max(current - 0.15, 0.6));
  }

  function resetZoom() {
    setZoom(1);
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-xl font-semibold">{data.title}</h2>
            <p className="mt-1 text-sm text-slate-400">
              Click an equipment marker to inspect its status.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={selectedRisk}
              onChange={(event) => setSelectedRisk(event.target.value)}
              className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-cyan-400"
            >
              <option value="ALL">All risk levels</option>
              <option value="High">High risk</option>
              <option value="Medium">Medium risk</option>
              <option value="Low">Low risk</option>
            </select>

            <button
              type="button"
              onClick={decreaseZoom}
              className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm hover:border-cyan-400"
            >
              −
            </button>

            <button
              type="button"
              onClick={resetZoom}
              className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm hover:border-cyan-400"
            >
              {Math.round(zoom * 100)}%
            </button>

            <button
              type="button"
              onClick={increaseZoom}
              className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm hover:border-cyan-400"
            >
              +
            </button>
          </div>
        </div>

        <div className="mt-5 max-h-[720px] overflow-auto rounded-2xl border border-slate-800 bg-white p-4">
          <div
            className="relative min-w-[1000px] origin-top-left transition-transform duration-200"
            style={{ transform: `scale(${zoom})` }}
          >
            <Image
              loader={pidImageLoader}
              src={apiUrl(data.image_url)}
              alt={data.title}
              width={1600}
              height={900}
              unoptimized
              className="block h-auto w-full rounded-xl"
            />

            <div className="absolute inset-0">
              {visibleNodes.map((node) => (
                <button
                  key={node.id}
                  type="button"
                  onClick={() => setSelectedNode(node)}
                  title={node.label}
                  className={`absolute -translate-x-1/2 -translate-y-1/2 rounded-full border-2 px-3 py-2 text-xs font-semibold shadow-lg transition hover:scale-110 ${getNodeClass(
                    node
                  )} ${
                    selectedNode?.id === node.id
                      ? "ring-4 ring-white/70"
                      : ""
                  }`}
                  style={{
                    left: `${node.x_percent}%`,
                    top: `${node.y_percent}%`,
                  }}
                >
                  {node.id}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-red-500" />
            High-risk asset
          </span>

          <span className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-amber-400" />
            Medium-risk asset
          </span>

          <span className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-violet-500" />
            Instrument
          </span>

          <span className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-cyan-500" />
            Valve
          </span>
        </div>
      </div>

      <aside className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        {!selectedNode && (
          <p className="text-sm text-slate-500">
            Select an equipment marker to see its details.
          </p>
        )}

        {selectedNode && (
          <>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
                  {selectedNode.type}
                </p>

                <h2 className="mt-3 text-2xl font-semibold">
                  {selectedNode.id}
                </h2>

                <p className="mt-1 text-sm text-slate-400">
                  {selectedNode.label}
                </p>
              </div>

              <span className="rounded-full bg-slate-950 px-3 py-1 text-xs text-slate-300">
                {selectedNode.risk_level}
              </span>
            </div>

            <div className="mt-6 rounded-xl bg-slate-950 p-4">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Current Status
              </p>

              <p
                className={`mt-2 text-xl font-semibold ${getStatusClass(
                  selectedNode.status
                )}`}
              >
                {selectedNode.status}
              </p>
            </div>

            <p className="mt-6 text-sm leading-7 text-slate-300">
              {selectedNode.description}
            </p>

            <div className="mt-6">
              <h3 className="font-semibold">Relationships</h3>

              <div className="mt-3 space-y-3">
                {connectedRelationships.map((connection) => (
                  <div
                    key={`${connection.source}-${connection.relationship}-${connection.target}`}
                    className="rounded-xl border border-slate-800 bg-slate-950 p-3 text-sm"
                  >
                    <p className="text-slate-300">
                      {connection.source}
                    </p>

                    <p className="my-1 text-xs font-medium text-cyan-400">
                      {connection.relationship}
                    </p>

                    <p className="text-slate-300">
                      {connection.target}
                    </p>
                  </div>
                ))}

                {!connectedRelationships.length && (
                  <p className="text-sm text-slate-500">
                    No direct relationships found.
                  </p>
                )}
              </div>
            </div>

            {selectedNode.asset_id && (
              <div className="mt-6 space-y-3">
                <Link
                  href={`/assets/${selectedNode.asset_id}`}
                  className="block rounded-xl bg-cyan-400 px-4 py-3 text-center text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
                >
                  Open Asset 360
                </Link>

                <Link
                  href={`/ask?asset=${selectedNode.asset_id}`}
                  className="block rounded-xl border border-slate-700 px-4 py-3 text-center text-sm text-slate-300 transition hover:border-cyan-400 hover:text-white"
                >
                  Ask PlantMind
                </Link>

                <Link
                  href={`/compliance?asset=${selectedNode.asset_id}`}
                  className="block rounded-xl border border-slate-700 px-4 py-3 text-center text-sm text-slate-300 transition hover:border-cyan-400 hover:text-white"
                >
                  View Compliance
                </Link>
              </div>
            )}
          </>
        )}
      </aside>
    </div>
  );
}
