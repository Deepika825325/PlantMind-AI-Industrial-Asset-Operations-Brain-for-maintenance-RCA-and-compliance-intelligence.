"use client";

import { useEffect, useState } from "react";

import PidViewer from "@/components/pid/PidViewer";
import { apiGet } from "@/lib/api";
import type { PidResponse } from "@/lib/types";

export default function PidPage() {
  const [data, setData] = useState<PidResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadPid() {
      try {
        setLoading(true);
        setError("");

        const result = await apiGet<PidResponse>("/pid/PID-001");

        setData(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load P&ID"
        );
      } finally {
        setLoading(false);
      }
    }

    loadPid();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-[1600px] px-6 py-10">
        <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
          Interactive P&amp;ID
        </p>

        <h1 className="mt-4 text-4xl font-semibold tracking-tight">
          Process and Equipment Intelligence
        </h1>

        <p className="mt-3 max-w-3xl text-slate-400">
          Explore the PlantMind process line, inspect equipment health,
          identify risk hotspots, and navigate directly to asset evidence.
        </p>

        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            Loading interactive P&amp;ID...
          </div>
        )}

        {error && (
          <div className="mt-8 rounded-2xl border border-red-800 bg-red-950/40 p-6 text-red-300">
            {error}
          </div>
        )}

        {data && (
          <div className="mt-8">
            <PidViewer data={data} />
          </div>
        )}
      </section>
    </main>
  );
}