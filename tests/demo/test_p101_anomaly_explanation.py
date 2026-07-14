from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app


def test_p101_anomaly_explanation_endpoint() -> None:
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:
        response = client.get(
            "/demo/p101/anomaly-explanation"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["asset_id"] == "P-101"
    assert payload["model_name"] == "plantmind-p101-anomaly-detector"
    assert payload["model_version"] == "v0.3.11"
    assert payload["anomaly_label"] == "critical"
    assert payload["anomaly_score"] >= 0.75
    assert payload["human_review_required"] is True
    assert "P101-EV-001" in payload["supporting_evidence_ids"]
    assert "RCA-P101-001" in payload["supporting_evidence_ids"]

    signal_names = {
        signal["signal_name"]
        for signal in payload["signal_contributions"]
    }

    assert "vibration_mm_s" in signal_names
    assert "bearing_temperature_deg_c" in signal_names
