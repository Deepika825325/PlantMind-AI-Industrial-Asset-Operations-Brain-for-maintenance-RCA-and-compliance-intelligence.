from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app


def test_p101_failure_hypotheses_endpoint() -> None:
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:
        response = client.get(
            "/demo/p101/failure-hypotheses"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["asset_id"] == "P-101"
    assert payload["rca_case_id"] == "RCA-P101-001"
    assert payload["primary_hypothesis"] == "lubrication_degradation"
    assert payload["governance_note"]
    assert payload["judge_message"]

    hypotheses = payload["hypotheses"]

    assert len(hypotheses) == 5
    assert [
        hypothesis["rank"]
        for hypothesis in hypotheses
    ] == [1, 2, 3, 4, 5]

    modes = {
        hypothesis["failure_mode"]
        for hypothesis in hypotheses
    }

    assert "lubrication_degradation" in modes
    assert "bearing_damage" in modes
    assert "shaft_misalignment" in modes
    assert "cavitation_or_hydraulic_instability" in modes
    assert "sensor_fault" in modes

    top = hypotheses[0]

    assert top["probability"] >= 0.30
    assert top["human_approval_required"] is True
    assert "P101-EV-001" in top["supporting_evidence_ids"]
    assert top["contradictory_evidence"]
    assert top["missing_tests"]
    assert top["recommended_next_action"]
