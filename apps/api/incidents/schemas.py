from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


IncidentSourceType = Literal[
    "sensor_anomaly",
    "manual_operator_report",
    "inspection_finding",
    "compliance_event",
]

IncidentSeverity = Literal[
    "low",
    "medium",
    "high",
    "critical",
]

IncidentStatus = Literal[
    "detected",
    "acknowledged",
    "investigating",
    "mitigated",
    "resolved",
    "closed",
]

IncidentEventType = Literal[
    "created",
    "grouped_source",
    "status_changed",
    "rca_linked",
    "note_added",
]


class IncidentSource(BaseModel):
    source_id: str
    source_type: IncidentSourceType
    asset_id: str
    title: str
    description: str
    severity: IncidentSeverity
    detected_at: str
    failure_mode: str | None = None
    anomaly_rule_id: str | None = None
    compliance_rule_id: str | None = None
    inspection_id: str | None = None


class CreateIncidentRequest(BaseModel):
    source: IncidentSource
    linked_rca_case_id: str | None = None


class UpdateIncidentStatusRequest(BaseModel):
    status: IncidentStatus
    note: str | None = None
    changed_at: str


class LinkIncidentRcaRequest(BaseModel):
    rca_case_id: str
    linked_at: str
    note: str | None = None


class IncidentTimelineEvent(BaseModel):
    event_id: str
    event_type: IncidentEventType
    timestamp: str
    title: str
    description: str
    from_status: IncidentStatus | None = None
    to_status: IncidentStatus | None = None
    source_id: str | None = None
    rca_case_id: str | None = None


class IndustrialIncident(BaseModel):
    incident_id: str
    asset_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: str
    updated_at: str
    linked_rca_case_id: str | None = None
    source_ids: list[str]
    source_types: list[IncidentSourceType]
    related_failure_modes: list[str]
    timeline: list[IncidentTimelineEvent]


class IncidentListResponse(BaseModel):
    total_incidents: int
    incidents: list[IndustrialIncident]


class IncidentCreateResponse(BaseModel):
    incident: IndustrialIncident
    grouped_into_existing: bool


class IncidentStatisticsResponse(BaseModel):
    total_incidents: int
    open_incidents: int
    closed_incidents: int
    status_counts: dict[str, int]
    severity_counts: dict[str, int]
    asset_counts: dict[str, int]