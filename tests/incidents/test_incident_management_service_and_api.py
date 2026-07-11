from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi.testclient import TestClient

from apps.api.incidents.schemas import (
    CreateIncidentRequest,
    IncidentSource,
    LinkIncidentRcaRequest,
    UpdateIncidentStatusRequest,
)
from apps.api.incidents.service import IncidentManagementService
from apps.api.main import app
from apps.api.routes import incidents as incident_route


client = TestClient(app)


def _source(
    source_id: str,
    *,
    source_type: str = "sensor_anomaly",
    asset_id: str = "P-101",
    severity: str = "high",
    detected_at: str = "2026-07-10T09:00:00+00:00",
    failure_mode: str | None = "bearing_damage",
) -> IncidentSource:
    return IncidentSource(
        source_id=source_id,
        source_type=source_type,
        asset_id=asset_id,
        title=f"{asset_id} {source_type} {source_id}",
        description=(
            f"{asset_id} source {source_id} indicates "
            f"{failure_mode or source_type}."
        ),
        severity=severity,
        detected_at=detected_at,
        failure_mode=failure_mode,
        anomaly_rule_id=(
            "RULE-VIB-CRITICAL-THRESHOLD"
            if source_type == "sensor_anomaly"
            else None
        ),
        compliance_rule_id=(
            "C001"
            if source_type == "compliance_event"
            else None
        ),
        inspection_id=(
            "IR-P101-001"
            if source_type == "inspection_finding"
            else None
        ),
    )


def _dependency_for(
    endpoint_name: str,
) -> Any:
    endpoint = getattr(
        incident_route,
        endpoint_name,
    )

    user_parameter = inspect.signature(
        endpoint
    ).parameters["user"]

    return user_parameter.default.dependency


@contextmanager
def authorized_user(
    endpoint_name: str,
) -> Iterator[None]:
    dependency = _dependency_for(
        endpoint_name
    )

    app.dependency_overrides[dependency] = lambda: {
        "user_id": "incident-tester",
        "email": "incident@plantmind.local",
        "role": "maintenance_engineer",
    }

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            dependency,
            None,
        )


@contextmanager
def isolated_incident_service() -> Iterator[IncidentManagementService]:
    original_service = incident_route.incident_service
    service = IncidentManagementService()
    incident_route.incident_service = service

    try:
        yield service
    finally:
        incident_route.incident_service = original_service


def test_sensor_anomaly_creates_incident_linked_to_asset_and_rca() -> None:
    service = IncidentManagementService()

    response = service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "ANOM-P101-001",
                detected_at="2026-07-10T09:00:00+00:00",
            ),
            linked_rca_case_id="RCA-P101-001",
        )
    )

    incident = response.incident

    assert response.grouped_into_existing is False
    assert incident.asset_id == "P-101"
    assert incident.linked_rca_case_id == "RCA-P101-001"
    assert incident.status == "detected"
    assert incident.source_ids == ["ANOM-P101-001"]
    assert incident.source_types == ["sensor_anomaly"]
    assert incident.related_failure_modes == ["bearing_damage"]
    assert [
        event.event_type
        for event in incident.timeline
    ] == [
        "created",
        "rca_linked",
    ]


def test_multiple_related_p101_anomalies_group_into_one_incident() -> None:
    service = IncidentManagementService()

    first = service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "ANOM-P101-001",
                severity="medium",
                detected_at="2026-07-10T09:00:00+00:00",
            )
        )
    )

    second = service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "ANOM-P101-002",
                severity="critical",
                detected_at="2026-07-10T09:00:30+00:00",
            )
        )
    )

    assert second.grouped_into_existing is True
    assert (
        second.incident.incident_id
        == first.incident.incident_id
    )
    assert second.incident.severity == "critical"
    assert second.incident.source_ids == [
        "ANOM-P101-001",
        "ANOM-P101-002",
    ]
    assert second.incident.asset_id == "P-101"
    assert [
        event.event_type
        for event in second.incident.timeline
    ] == [
        "created",
        "grouped_source",
    ]


def test_incidents_can_be_created_from_all_required_source_types() -> None:
    service = IncidentManagementService()

    sources = [
        _source(
            "ANOM-P101-001",
            source_type="sensor_anomaly",
            asset_id="P-101",
            failure_mode="bearing_damage",
        ),
        _source(
            "MAN-C201-001",
            source_type="manual_operator_report",
            asset_id="C-201",
            failure_mode="shaft_misalignment",
        ),
        _source(
            "IR-HX301-001",
            source_type="inspection_finding",
            asset_id="HX-301",
            failure_mode="fouling",
        ),
        _source(
            "COMP-P101-001",
            source_type="compliance_event",
            asset_id="P-101",
            failure_mode="lubrication_degradation",
            detected_at="2026-07-11T09:00:00+00:00",
        ),
    ]

    for source in sources:
        service.create_from_source(
            CreateIncidentRequest(
                source=source,
            )
        )

    incidents = service.list_incidents().incidents
    source_types = {
        source_type
        for incident in incidents
        for source_type in incident.source_types
    }

    assert source_types == {
        "sensor_anomaly",
        "manual_operator_report",
        "inspection_finding",
        "compliance_event",
    }


def test_lifecycle_status_updates_create_timeline_events() -> None:
    service = IncidentManagementService()

    incident = service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "ANOM-P101-001",
            )
        )
    ).incident

    incident_id = incident.incident_id

    lifecycle = [
        "acknowledged",
        "investigating",
        "mitigated",
        "resolved",
        "closed",
    ]

    for index, status in enumerate(
        lifecycle,
        start=1,
    ):
        updated = service.update_status(
            incident_id=incident_id,
            request=UpdateIncidentStatusRequest(
                status=status,
                note=f"Moved to {status}.",
                changed_at=f"2026-07-10T09:0{index}:00+00:00",
            ),
        )

        assert updated is not None
        assert updated.status == status

    final = service.get_incident(
        incident_id,
    )

    assert final is not None
    assert final.status == "closed"
    assert [
        event.to_status
        for event in final.timeline
        if event.event_type == "status_changed"
    ] == lifecycle


def test_closed_incident_does_not_group_new_anomaly() -> None:
    service = IncidentManagementService()

    first = service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "ANOM-P101-001",
                detected_at="2026-07-10T09:00:00+00:00",
            )
        )
    ).incident

    service.update_status(
        incident_id=first.incident_id,
        request=UpdateIncidentStatusRequest(
            status="closed",
            note="Closed after mitigation.",
            changed_at="2026-07-10T10:00:00+00:00",
        ),
    )

    second = service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "ANOM-P101-002",
                detected_at="2026-07-10T10:05:00+00:00",
            )
        )
    )

    assert second.grouped_into_existing is False
    assert second.incident.incident_id != first.incident_id


def test_incident_links_to_rca_after_creation() -> None:
    service = IncidentManagementService()

    incident = service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "ANOM-P101-001",
            )
        )
    ).incident

    linked = service.link_rca(
        incident_id=incident.incident_id,
        request=LinkIncidentRcaRequest(
            rca_case_id="RCA-P101-001",
            linked_at="2026-07-10T09:10:00+00:00",
            note="Linked to P-101 vibration RCA.",
        ),
    )

    assert linked is not None
    assert linked.linked_rca_case_id == "RCA-P101-001"
    assert linked.timeline[-1].event_type == "rca_linked"
    assert linked.timeline[-1].rca_case_id == "RCA-P101-001"


def test_incident_statistics_counts_open_closed_and_assets() -> None:
    service = IncidentManagementService()

    first = service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "ANOM-P101-001",
                asset_id="P-101",
            )
        )
    ).incident

    service.create_from_source(
        CreateIncidentRequest(
            source=_source(
                "MAN-C201-001",
                source_type="manual_operator_report",
                asset_id="C-201",
                failure_mode="shaft_misalignment",
            )
        )
    )

    service.update_status(
        incident_id=first.incident_id,
        request=UpdateIncidentStatusRequest(
            status="closed",
            note="Closed.",
            changed_at="2026-07-10T10:00:00+00:00",
        ),
    )

    stats = service.statistics()

    assert stats.total_incidents == 2
    assert stats.open_incidents == 1
    assert stats.closed_incidents == 1
    assert stats.asset_counts["P-101"] == 1
    assert stats.asset_counts["C-201"] == 1


def test_incident_api_create_group_list_link_status_and_statistics() -> None:
    with isolated_incident_service():
        with authorized_user("create_incident"):
            first_response = client.post(
                "/incidents",
                json={
                    "source": _source(
                        "ANOM-P101-001",
                        detected_at="2026-07-10T09:00:00+00:00",
                    ).model_dump(),
                    "linked_rca_case_id": "RCA-P101-001",
                },
            )

        assert first_response.status_code == 200
        assert first_response.json()["grouped_into_existing"] is False

        incident_id = first_response.json()["incident"]["incident_id"]

        with authorized_user("create_incident"):
            second_response = client.post(
                "/incidents",
                json={
                    "source": _source(
                        "ANOM-P101-002",
                        severity="critical",
                        detected_at="2026-07-10T09:00:30+00:00",
                    ).model_dump(),
                },
            )

        assert second_response.status_code == 200
        assert second_response.json()["grouped_into_existing"] is True
        assert (
            second_response.json()["incident"]["incident_id"]
            == incident_id
        )

        with authorized_user("list_incidents"):
            list_response = client.get(
                "/incidents?asset_id=P-101"
            )

        assert list_response.status_code == 200
        assert list_response.json()["total_incidents"] == 1
        assert (
            list_response.json()["incidents"][0]["asset_id"]
            == "P-101"
        )

        with authorized_user("get_incident"):
            get_response = client.get(
                f"/incidents/{incident_id}"
            )

        assert get_response.status_code == 200
        assert get_response.json()["linked_rca_case_id"] == "RCA-P101-001"
        assert len(get_response.json()["timeline"]) >= 2

        with authorized_user("update_incident_status"):
            status_response = client.post(
                f"/incidents/{incident_id}/status",
                json={
                    "status": "acknowledged",
                    "note": "Operator acknowledged incident.",
                    "changed_at": "2026-07-10T09:05:00+00:00",
                },
            )

        assert status_response.status_code == 200
        assert status_response.json()["status"] == "acknowledged"

        with authorized_user("link_incident_rca"):
            rca_response = client.post(
                f"/incidents/{incident_id}/rca",
                json={
                    "rca_case_id": "RCA-P101-001",
                    "linked_at": "2026-07-10T09:10:00+00:00",
                    "note": "Confirm RCA link.",
                },
            )

        assert rca_response.status_code == 200
        assert rca_response.json()["linked_rca_case_id"] == "RCA-P101-001"

        with authorized_user("get_incident_statistics"):
            stats_response = client.get(
                "/incidents/statistics"
            )

        assert stats_response.status_code == 200
        assert stats_response.json()["total_incidents"] == 1


def test_incident_api_requires_authentication() -> None:
    response = client.get(
        "/incidents"
    )

    assert response.status_code == 401