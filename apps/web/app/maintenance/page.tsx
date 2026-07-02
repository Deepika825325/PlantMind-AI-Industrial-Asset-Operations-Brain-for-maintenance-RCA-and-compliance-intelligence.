"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet } from "@/lib/api";

type MaintenanceEvent = {
  event_id: string;
  asset_id: string;
  asset_name: string;
  event_type: string;
  priority: string;
  status: string;
  created_date: string;
  due_date: string;
  description: string;
  linked_document: string;
  compliance_related: string;
};

type MaintenanceResponse = {
  total: number;
  events: MaintenanceEvent[];
};

function getPriorityClass(priority: string) {
  if (priority === "High") {
    return "bg-red-100 text-red-700 border-red-200";
  }

  if (priority === "Medium") {
    return "bg-amber-100 text-amber-700 border-amber-200";
  }

  return "bg-emerald-100 text-emerald-700 border-emerald-200";
}

function getStatusClass(status: string) {
  if (status === "Open") {
    return "text-red-400";
  }

  if (status === "Delayed") {
    return "text-amber-400";
  }

  if (status === "Planned") {
    return "text-cyan-400";
  }

  return "text-slate-300";
}

export default function MaintenancePage() {
  const [events, setEvents] = useState<MaintenanceEvent[]>([]);
  const [selectedAsset, setSelectedAsset] = useState("ALL");
  const [selectedStatus, setSelectedStatus] = useState("ALL");
  const [selectedPriority, setSelectedPriority] = useState("ALL");
  const [searchText, setSearchText] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadMaintenanceEvents() {
      try {
        setLoading(true);
        const result = await apiGet<MaintenanceResponse>("/maintenance/events");
        setEvents(result.events);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load maintenance events");
      } finally {
        setLoading(false);
      }
    }

    loadMaintenanceEvents();
  }, []);

  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      const matchesAsset =
        selectedAsset === "ALL" || event.asset_id === selectedAsset;

      const matchesStatus =
        selectedStatus === "ALL" || event.status === selectedStatus;

      const matchesPriority =
        selectedPriority === "ALL" || event.priority === selectedPriority;

      const query = searchText.toLowerCase().trim();

      const matchesSearch =
        !query ||
        event.event_id.toLowerCase().includes(query) ||
        event.asset_id.toLowerCase().includes(query) ||
        event.asset_name.toLowerCase().includes(query) ||
        event.event_type.toLowerCase().includes(query) ||
        event.description.toLowerCase().includes(query) ||
        event.linked_document.toLowerCase().includes(query);

      return matchesAsset && matchesStatus && matchesPriority && matchesSearch;
    });
  }, [events, selectedAsset, selectedStatus, selectedPriority, searchText]);

  const openCount = events.filter((event) => event.status === "Open").length;
  const delayedCount = events.filter((event) => event.status === "Delayed").length;
  const highPriorityCount = events.filter((event) => event.priority === "High").length;
  const complianceRelatedCount = events.filter(
    (event) => event.compliance_related === "Yes"
  ).length;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Maintenance Events
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Work Orders and Maintenance Actions
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Track open, delayed, planned, and compliance-related work orders
            connected to asset risk, RCA findings, and evidence gaps.
          </p>
        </div>

        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            Loading maintenance events...
          </div>
        )}

        {error && (
          <div className="mt-8 rounded-2xl border border-red-800 bg-red-950/40 p-6 text-red-300">
            {error}
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="mt-8 grid gap-4 md:grid-cols-4">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Total Work Orders</p>
                <p className="mt-3 text-3xl font-semibold">{events.length}</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Open</p>
                <p className="mt-3 text-3xl font-semibold text-red-400">
                  {openCount}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Delayed</p>
                <p className="mt-3 text-3xl font-semibold text-amber-400">
                  {delayedCount}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Compliance Related</p>
                <p className="mt-3 text-3xl font-semibold text-cyan-400">
                  {complianceRelatedCount}
                </p>
              </div>
            </div>

            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <label className="text-sm text-slate-400">Search</label>
                  <input
                    value={searchText}
                    onChange={(event) => setSearchText(event.target.value)}
                    placeholder="Search work order, asset, description..."
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <label className="text-sm text-slate-400">Asset</label>
                  <select
                    value={selectedAsset}
                    onChange={(event) => setSelectedAsset(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    <option value="ALL">All Assets</option>
                    <option value="P-101">P-101</option>
                    <option value="C-201">C-201</option>
                    <option value="HX-301">HX-301</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm text-slate-400">Status</label>
                  <select
                    value={selectedStatus}
                    onChange={(event) => setSelectedStatus(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    <option value="ALL">All Statuses</option>
                    <option value="Open">Open</option>
                    <option value="Delayed">Delayed</option>
                    <option value="Planned">Planned</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm text-slate-400">Priority</label>
                  <select
                    value={selectedPriority}
                    onChange={(event) => setSelectedPriority(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    <option value="ALL">All Priorities</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Maintenance Timeline</h2>
                <span className="text-sm text-slate-500">
                  Showing {filteredEvents.length} events
                </span>
              </div>

              <div className="mt-6 space-y-4">
                {filteredEvents.map((event) => (
                  <div
                    key={event.event_id}
                    className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold">{event.event_id}</h3>

                          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                            {event.asset_id}
                          </span>

                          <span
                            className={`rounded-full border px-3 py-1 text-xs font-medium ${getPriorityClass(
                              event.priority
                            )}`}
                          >
                            {event.priority}
                          </span>
                        </div>

                        <p className="mt-3 text-slate-100">{event.event_type}</p>

                        <p className="mt-2 text-sm text-slate-400">
                          {event.asset_name}
                        </p>
                      </div>

                      <div className="text-left md:text-right">
                        <p className={`font-medium ${getStatusClass(event.status)}`}>
                          {event.status}
                        </p>
                        <p className="mt-1 text-sm text-slate-500">
                          Due: {event.due_date}
                        </p>
                      </div>
                    </div>

                    <p className="mt-5 text-sm leading-6 text-slate-300">
                      {event.description}
                    </p>

                    <div className="mt-5 grid gap-4 md:grid-cols-3">
                      <div className="rounded-xl bg-slate-900 p-4">
                        <p className="text-xs uppercase tracking-wider text-slate-500">
                          Created
                        </p>
                        <p className="mt-2 text-sm text-slate-300">
                          {event.created_date}
                        </p>
                      </div>

                      <div className="rounded-xl bg-slate-900 p-4">
                        <p className="text-xs uppercase tracking-wider text-slate-500">
                          Linked Document
                        </p>
                        <p className="mt-2 text-sm text-slate-300">
                          {event.linked_document}
                        </p>
                      </div>

                      <div className="rounded-xl bg-slate-900 p-4">
                        <p className="text-xs uppercase tracking-wider text-slate-500">
                          Compliance Related
                        </p>
                        <p className="mt-2 text-sm text-slate-300">
                          {event.compliance_related}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </section>
    </main>
  );
}