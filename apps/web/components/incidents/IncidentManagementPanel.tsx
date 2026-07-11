"use client";

import { useMemo, useState } from "react";

import { apiPost } from "@/lib/api";

type IncidentSourceType =
  | "sensor_anomaly"
  | "manual_operator_report"
  | "inspection_finding"
  | "compliance_event";

type IncidentSeverity = "low" | "medium" | "high" | "critical";

type IncidentStatus =
  | "detected"
  | "acknowledged"
  | "investigating"
  | "mitigated"
  | "resolved"
  | "closed";

type IncidentEventType =
  | "created"
  | "grouped_source"
  | "status_changed"
  | "rca_linked"
  | "note_added";

type IncidentSource = {
  source_id: string;
  source_type: IncidentSourceType;
  asset_id: string;
  title: string;
  description: string;
  severity: IncidentSeverity;
  detected_at: string;
  failure_mode?: string | null;
  anomaly_rule_id?: string | null;
  compliance_rule_id?: string | null;
  inspection_id?: string | null;
};

type IncidentTimelineEvent = {
  event_id: string;
  event_type: IncidentEventType;
  timestamp: string;
  title: string;
  description: string;
  from_status?: IncidentStatus | null;
  to_status?: IncidentStatus | null;
  source_id?: string | null;
  rca_case_id?: string | null;
};

type IndustrialIncident = {
  incident_id: string;
  asset_id: string;
  title: string;
  description: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  created_at: string;
  updated_at: string;
  linked_rca_case_id?: string | null;
  source_ids: string[];
  source_types: IncidentSourceType[];
  related_failure_modes: string[];
  timeline: IncidentTimelineEvent[];
};

type IncidentCreateResponse = {
  incident: IndustrialIncident;
  grouped_into_existing: boolean;
};

type CreateIncidentRequest = {
  source: IncidentSource;
  linked_rca_case_id?: string | null;
};

type UpdateIncidentStatusRequest = {
  status: IncidentStatus;
  note?: string | null;
  changed_at: string;
};

const demoTimes = [
  "2026-07-10T09:00:00+00:00",
  "2026-07-10T09:00:30+00:00",
  "2026-07-10T09:05:00+00:00",
  "2026-07-10T09:15:00+00:00",
  "2026-07-10T09:30:00+00:00",
];

const demoSources: IncidentSource[] = [
  {
    source_id: "ANOM-P101-001",
    source_type: "sensor_anomaly",
    asset_id: "P-101",
    title: "P-101 critical vibration anomaly",
    description:
      "Vibration crossed critical threshold and aligns with bearing damage symptoms.",
    severity: "high",
    detected_at: demoTimes[0],
    failure_mode: "bearing_damage",
    anomaly_rule_id: "RULE-VIB-CRITICAL-THRESHOLD",
  },
  {
    source_id: "ANOM-P101-002",
    source_type: "sensor_anomaly",
    asset_id: "P-101",
    title: "P-101 bearing temperature escalation",
    description:
      "Bearing temperature increased shortly after vibration escalation.",
    severity: "critical",
    detected_at: demoTimes[1],
    failure_mode: "bearing_damage",
    anomaly_rule_id: "RULE-COMBINED-VIB-TEMP",
  },
  {
    source_id: "MAN-P101-001",
    source_type: "manual_operator_report",
    asset_id: "P-101",
    title: "Operator reports abnormal pump noise",
    description:
      "Operator reported abnormal drive-end noise during field round.",
    severity: "medium",
    detected_at: demoTimes[2],
    failure_mode: "bearing_damage",
  },
];

function fallbackIncident(): IndustrialIncident {
  return {
    incident_id: "INC-P-101-DEMO",
    asset_id: "P-101",
    title: "P-101 critical vibration anomaly",
    description:
      "Grouped incident from vibration anomaly, temperature escalation, and operator report.",
    severity: "critical",
    status: "investigating",
    created_at: demoTimes[0],
    updated_at: demoTimes[3],
    linked_rca_case_id: "RCA-P101-001",
    source_ids: ["ANOM-P101-001", "ANOM-P101-002", "MAN-P101-001"],
    source_types: ["sensor_anomaly", "manual_operator_report"],
    related_failure_modes: ["bearing_damage"],
    timeline: [
      {
        event_id: "EVT-DEMO-001",
        event_type: "created",
        timestamp: demoTimes[0],
        title: "Incident detected",
        description:
          "Incident created from sensor anomaly ANOM-P101-001.",
        to_status: "detected",
        source_id: "ANOM-P101-001",
      },
      {
        event_id: "EVT-DEMO-002",
        event_type: "grouped_source",
        timestamp: demoTimes[1],
        title: "Related anomaly grouped",
        description:
          "ANOM-P101-002 grouped into the same P-101 bearing damage incident.",
        source_id: "ANOM-P101-002",
      },
      {
        event_id: "EVT-DEMO-003",
        event_type: "grouped_source",
        timestamp: demoTimes[2],
        title: "Operator report grouped",
        description:
          "Manual operator report grouped with related P-101 anomaly pattern.",
        source_id: "MAN-P101-001",
      },
      {
        event_id: "EVT-DEMO-004",
        event_type: "status_changed",
        timestamp: demoTimes[3],
        title: "Status changed to investigating",
        description:
          "Engineer moved incident from acknowledged to investigating.",
        from_status: "acknowledged",
        to_status: "investigating",
      },
      {
        event_id: "EVT-DEMO-005",
        event_type: "rca_linked",
        timestamp: demoTimes[4],
        title: "Linked RCA RCA-P101-001",
        description:
          "Incident linked to P-101 high vibration and bearing temperature RCA.",
        rca_case_id: "RCA-P101-001",
      },
    ],
  };
}

function label(value: string): string {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

export function IncidentManagementPanel() {
  const [incident, setIncident] = useState<IndustrialIncident>(() =>
    fallbackIncident(),
  );
  const [status, setStatus] = useState(
    "Using local incident preview with grouped P-101 anomalies.",
  );

  const timeline = useMemo(() => {
    return [...incident.timeline].sort((left, right) =>
      left.timestamp.localeCompare(right.timestamp),
    );
  }, [incident.timeline]);

  async function runBackendWorkflow() {
    setStatus("Creating and grouping incident through backend...");

    try {
      let latestIncident: IndustrialIncident | null = null;

      for (const [index, source] of demoSources.entries()) {
        const response = await apiPost<CreateIncidentRequest, IncidentCreateResponse>(
          "/incidents",
          {
            source,
            linked_rca_case_id: index === 0 ? "RCA-P101-001" : null,
          },
        );

        latestIncident = response.incident;
      }

      if (!latestIncident) {
        throw new Error("Incident creation failed.");
      }

      const updated = await apiPost<
        UpdateIncidentStatusRequest,
        IndustrialIncident
      >(
        `/incidents/${latestIncident.incident_id}/status`,
        {
          status: "investigating",
          note: "Engineer started investigation after grouped P-101 anomalies.",
          changed_at: demoTimes[3],
        },
      );

      setIncident(updated);
      setStatus("Backend incident workflow completed successfully.");
    } catch {
      setIncident(fallbackIncident());
      setStatus(
        "Backend unavailable. Showing local grouped-incident timeline preview.",
      );
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Incident Management
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">
              Industrial incident closed-loop workflow
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              Create incidents from sensor anomalies, manual reports,
              inspection findings, and compliance events. Related P-101
              anomalies are grouped into one incident with a visible timeline,
              lifecycle status, asset link, and RCA link.
            </p>
          </div>

          <button
            type="button"
            onClick={runBackendWorkflow}
            className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
          >
            Run backend workflow
          </button>
        </div>

        <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          {status}
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Incident summary
          </p>

          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            {incident.title}
          </h2>

          <div className="mt-6 grid gap-3 text-sm text-slate-700">
            <p>
              <span className="font-semibold">Incident ID:</span>{" "}
              {incident.incident_id}
            </p>
            <p>
              <span className="font-semibold">Asset:</span>{" "}
              {incident.asset_id}
            </p>
            <p>
              <span className="font-semibold">Status:</span>{" "}
              {label(incident.status)}
            </p>
            <p>
              <span className="font-semibold">Severity:</span>{" "}
              {label(incident.severity)}
            </p>
            <p>
              <span className="font-semibold">Linked RCA:</span>{" "}
              {incident.linked_rca_case_id ?? "Not linked"}
            </p>
            <p>
              <span className="font-semibold">Failure modes:</span>{" "}
              {incident.related_failure_modes.length > 0
                ? incident.related_failure_modes.map(label).join(", ")
                : "None"}
            </p>
          </div>

          <div className="mt-6 rounded-xl bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-950">
              Grouped sources
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {incident.source_ids.map((sourceId) => (
                <span
                  key={sourceId}
                  className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200"
                >
                  {sourceId}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Incident timeline
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Every grouped source and lifecycle change is visible
          </h2>

          <div className="mt-6 space-y-4">
            {timeline.map((event) => (
              <div
                key={event.event_id}
                className="rounded-xl border border-slate-200 p-4"
              >
                <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p className="font-semibold text-slate-950">
                      {event.title}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {label(event.event_type)} · {event.timestamp}
                    </p>
                  </div>

                  {(event.source_id || event.rca_case_id || event.to_status) && (
                    <p className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                      {event.source_id ??
                        event.rca_case_id ??
                        label(event.to_status ?? "")}
                    </p>
                  )}
                </div>

                <p className="mt-3 text-sm leading-6 text-slate-600">
                  {event.description}
                </p>

                {event.from_status && event.to_status && (
                  <p className="mt-3 text-xs font-medium text-slate-500">
                    {label(event.from_status)} → {label(event.to_status)}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}