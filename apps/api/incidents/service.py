from __future__ import annotations

import hashlib
from collections import Counter

from apps.api.incidents.schemas import (
    CreateIncidentRequest,
    IncidentCreateResponse,
    IncidentListResponse,
    IncidentSource,
    IncidentStatisticsResponse,
    IncidentTimelineEvent,
    IndustrialIncident,
    LinkIncidentRcaRequest,
    UpdateIncidentStatusRequest,
)


OPEN_STATUSES = {
    "detected",
    "acknowledged",
    "investigating",
    "mitigated",
    "resolved",
}

CLOSED_STATUSES = {
    "closed",
}

SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


class IncidentManagementService:
    def __init__(self) -> None:
        self._incidents: dict[
            str,
            IndustrialIncident,
        ] = {}

    def create_from_source(
        self,
        request: CreateIncidentRequest,
    ) -> IncidentCreateResponse:
        existing = self._find_groupable_incident(
            request.source,
        )

        if existing:
            updated = self._group_source(
                incident=existing,
                source=request.source,
                linked_rca_case_id=request.linked_rca_case_id,
            )

            self._incidents[updated.incident_id] = updated

            return IncidentCreateResponse(
                incident=updated,
                grouped_into_existing=True,
            )

        incident = self._new_incident(
            source=request.source,
            linked_rca_case_id=request.linked_rca_case_id,
        )

        self._incidents[incident.incident_id] = incident

        return IncidentCreateResponse(
            incident=incident,
            grouped_into_existing=False,
        )

    def list_incidents(
        self,
        *,
        asset_id: str | None = None,
        status: str | None = None,
    ) -> IncidentListResponse:
        incidents = list(
            self._incidents.values()
        )

        if asset_id:
            incidents = [
                incident
                for incident in incidents
                if incident.asset_id == asset_id
            ]

        if status:
            incidents = [
                incident
                for incident in incidents
                if incident.status == status
            ]

        incidents = sorted(
            incidents,
            key=lambda incident: incident.updated_at,
            reverse=True,
        )

        return IncidentListResponse(
            total_incidents=len(incidents),
            incidents=incidents,
        )

    def get_incident(
        self,
        incident_id: str,
    ) -> IndustrialIncident | None:
        return self._incidents.get(
            incident_id,
        )

    def update_status(
        self,
        *,
        incident_id: str,
        request: UpdateIncidentStatusRequest,
    ) -> IndustrialIncident | None:
        incident = self._incidents.get(
            incident_id,
        )

        if not incident:
            return None

        timeline = [
            *incident.timeline,
            IncidentTimelineEvent(
                event_id=self._event_id(
                    incident_id=incident_id,
                    timestamp=request.changed_at,
                    title=f"status:{request.status}",
                ),
                event_type="status_changed",
                timestamp=request.changed_at,
                title=f"Status changed to {request.status}",
                description=request.note
                or f"Incident moved from {incident.status} to {request.status}.",
                from_status=incident.status,
                to_status=request.status,
            ),
        ]

        updated = incident.model_copy(
            update={
                "status": request.status,
                "updated_at": request.changed_at,
                "timeline": timeline,
            }
        )

        self._incidents[incident_id] = updated

        return updated

    def link_rca(
        self,
        *,
        incident_id: str,
        request: LinkIncidentRcaRequest,
    ) -> IndustrialIncident | None:
        incident = self._incidents.get(
            incident_id,
        )

        if not incident:
            return None

        timeline = [
            *incident.timeline,
            IncidentTimelineEvent(
                event_id=self._event_id(
                    incident_id=incident_id,
                    timestamp=request.linked_at,
                    title=f"rca:{request.rca_case_id}",
                ),
                event_type="rca_linked",
                timestamp=request.linked_at,
                title=f"Linked RCA {request.rca_case_id}",
                description=request.note
                or f"Incident linked to RCA case {request.rca_case_id}.",
                rca_case_id=request.rca_case_id,
            ),
        ]

        updated = incident.model_copy(
            update={
                "linked_rca_case_id": request.rca_case_id,
                "updated_at": request.linked_at,
                "timeline": timeline,
            }
        )

        self._incidents[incident_id] = updated

        return updated

    def statistics(self) -> IncidentStatisticsResponse:
        incidents = list(
            self._incidents.values()
        )

        status_counts = Counter(
            incident.status
            for incident in incidents
        )
        severity_counts = Counter(
            incident.severity
            for incident in incidents
        )
        asset_counts = Counter(
            incident.asset_id
            for incident in incidents
        )

        return IncidentStatisticsResponse(
            total_incidents=len(incidents),
            open_incidents=sum(
                1
                for incident in incidents
                if incident.status in OPEN_STATUSES
            ),
            closed_incidents=sum(
                1
                for incident in incidents
                if incident.status in CLOSED_STATUSES
            ),
            status_counts=dict(status_counts),
            severity_counts=dict(severity_counts),
            asset_counts=dict(asset_counts),
        )

    def _new_incident(
        self,
        *,
        source: IncidentSource,
        linked_rca_case_id: str | None,
    ) -> IndustrialIncident:
        incident_id = self._incident_id(
            source,
        )

        timeline = [
            IncidentTimelineEvent(
                event_id=self._event_id(
                    incident_id=incident_id,
                    timestamp=source.detected_at,
                    title="created",
                ),
                event_type="created",
                timestamp=source.detected_at,
                title="Incident detected",
                description=(
                    f"Incident created from {source.source_type}: "
                    f"{source.title}"
                ),
                to_status="detected",
                source_id=source.source_id,
            )
        ]

        if linked_rca_case_id:
            timeline.append(
                IncidentTimelineEvent(
                    event_id=self._event_id(
                        incident_id=incident_id,
                        timestamp=source.detected_at,
                        title=f"rca:{linked_rca_case_id}",
                    ),
                    event_type="rca_linked",
                    timestamp=source.detected_at,
                    title=f"Linked RCA {linked_rca_case_id}",
                    description=(
                        f"Incident linked to RCA case {linked_rca_case_id}."
                    ),
                    rca_case_id=linked_rca_case_id,
                )
            )

        return IndustrialIncident(
            incident_id=incident_id,
            asset_id=source.asset_id,
            title=source.title,
            description=source.description,
            severity=source.severity,
            status="detected",
            created_at=source.detected_at,
            updated_at=source.detected_at,
            linked_rca_case_id=linked_rca_case_id,
            source_ids=[
                source.source_id,
            ],
            source_types=[
                source.source_type,
            ],
            related_failure_modes=self._failure_modes(
                [
                    source,
                ]
            ),
            timeline=timeline,
        )

    def _group_source(
        self,
        *,
        incident: IndustrialIncident,
        source: IncidentSource,
        linked_rca_case_id: str | None,
    ) -> IndustrialIncident:
        source_ids = list(
            dict.fromkeys(
                [
                    *incident.source_ids,
                    source.source_id,
                ]
            )
        )

        source_types = list(
            dict.fromkeys(
                [
                    *incident.source_types,
                    source.source_type,
                ]
            )
        )

        severity = self._highest_severity(
            incident.severity,
            source.severity,
        )

        timeline = [
            *incident.timeline,
            IncidentTimelineEvent(
                event_id=self._event_id(
                    incident_id=incident.incident_id,
                    timestamp=source.detected_at,
                    title=f"grouped:{source.source_id}",
                ),
                event_type="grouped_source",
                timestamp=source.detected_at,
                title="Related source grouped",
                description=(
                    f"Grouped related {source.source_type} source "
                    f"{source.source_id} into this incident."
                ),
                source_id=source.source_id,
            ),
        ]

        final_rca = linked_rca_case_id or incident.linked_rca_case_id

        if linked_rca_case_id and linked_rca_case_id != incident.linked_rca_case_id:
            timeline.append(
                IncidentTimelineEvent(
                    event_id=self._event_id(
                        incident_id=incident.incident_id,
                        timestamp=source.detected_at,
                        title=f"rca:{linked_rca_case_id}",
                    ),
                    event_type="rca_linked",
                    timestamp=source.detected_at,
                    title=f"Linked RCA {linked_rca_case_id}",
                    description=(
                        f"Incident linked to RCA case {linked_rca_case_id}."
                    ),
                    rca_case_id=linked_rca_case_id,
                )
            )

        return incident.model_copy(
            update={
                "description": (
                    f"{incident.description}\n\nRelated source: "
                    f"{source.title} — {source.description}"
                ),
                "severity": severity,
                "updated_at": source.detected_at,
                "linked_rca_case_id": final_rca,
                "source_ids": source_ids,
                "source_types": source_types,
                "related_failure_modes": list(
                    dict.fromkeys(
                        [
                            *incident.related_failure_modes,
                            *self._failure_modes(
                                [
                                    source,
                                ]
                            ),
                        ]
                    )
                ),
                "timeline": timeline,
            }
        )

    def _find_groupable_incident(
        self,
        source: IncidentSource,
    ) -> IndustrialIncident | None:
        for incident in self._incidents.values():
            if incident.asset_id != source.asset_id:
                continue

            if incident.status == "closed":
                continue

            if source.source_id in incident.source_ids:
                return incident

            if (
                source.failure_mode
                and source.failure_mode in incident.related_failure_modes
            ):
                return incident

            if (
                source.source_type == "sensor_anomaly"
                and "sensor_anomaly" in incident.source_types
            ):
                return incident

        return None

    def _incident_id(
        self,
        source: IncidentSource,
    ) -> str:
        digest = hashlib.sha256(
            (
                f"{source.asset_id}:"
                f"{source.failure_mode or source.source_type}:"
                f"{source.detected_at[:10]}:"
                f"{source.source_id}"
            ).encode("utf-8")
        ).hexdigest()[:10]

        return f"INC-{source.asset_id}-{digest}".replace(
            "--",
            "-",
        )

    def _event_id(
        self,
        *,
        incident_id: str,
        timestamp: str,
        title: str,
    ) -> str:
        digest = hashlib.sha256(
            f"{incident_id}:{timestamp}:{title}".encode("utf-8")
        ).hexdigest()[:12]

        return f"EVT-{digest}"

    def _failure_modes(
        self,
        sources: list[IncidentSource],
    ) -> list[str]:
        return [
            source.failure_mode
            for source in sources
            if source.failure_mode
        ]

    def _highest_severity(
        self,
        left: str,
        right: str,
    ) -> str:
        if SEVERITY_RANK[right] > SEVERITY_RANK[left]:
            return right

        return left