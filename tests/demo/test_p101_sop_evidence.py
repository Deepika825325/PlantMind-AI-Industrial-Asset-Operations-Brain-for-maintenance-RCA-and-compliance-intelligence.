from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app


def test_p101_sop_evidence_endpoint() -> None:
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:
        response = client.get(
            "/demo/p101/sop-evidence"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["asset_id"] == "P-101"
    assert payload["rca_case_id"] == "RCA-P101-001"
    assert payload["rag_status"] == "grounded_with_citations"
    assert payload["confidence"] >= 0.90
    assert payload["answer"]
    assert payload["maintenance_decision"]
    assert payload["governance_note"]
    assert payload["judge_message"]

    assert payload["sop_evidence"]
    assert payload["inspection_evidence"]
    assert payload["incident_evidence"]
    assert payload["compliance_evidence"]
    assert payload["citation_trail"]

    citation_text = " ".join(
        payload["citation_trail"]
    )

    assert "SOP-P101-001" in citation_text
    assert "IR-P101-001" in citation_text
    assert "COMP-001" in citation_text

    sop_document_ids = {
        item["document_id"]
        for item in payload["sop_evidence"]
    }

    assert "SOP-P101-001_Pump_Lubrication_and_Bearing_Check" in sop_document_ids
    assert "SOP-P101-002_Pump_Vibration_Inspection" in sop_document_ids
