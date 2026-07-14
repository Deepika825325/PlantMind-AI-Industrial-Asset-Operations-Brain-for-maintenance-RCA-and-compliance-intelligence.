from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app


def test_p101_evaluation_summary_endpoint() -> None:
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:
        response = client.get(
            "/demo/p101/evaluation-summary"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["asset_id"] == "P-101"
    assert payload["demo_name"]
    assert payload["evaluation_version"] == "demo-eval-v1"
    assert payload["overall_score"] >= 0.90
    assert payload["readiness_level"] == "judge_ready"
    assert payload["metrics"]
    assert payload["passed_checks"]
    assert payload["open_gaps"]
    assert payload["recommended_demo_order"]
    assert payload["endpoints_validated"]
    assert payload["governance_note"]
    assert payload["judge_message"]

    metric_names = {
        metric["metric_name"]
        for metric in payload["metrics"]
    }

    assert "closed_loop_completion" in metric_names
    assert "anomaly_explanation_coverage" in metric_names
    assert "failure_hypothesis_quality" in metric_names
    assert "rag_evidence_grounding" in metric_names
    assert "governance_and_safety" in metric_names
    assert "demo_readiness" in metric_names

    assert "/demo/p101/evaluation-summary" in payload["endpoints_validated"]

    assert all(
        metric["score"] >= 0.90
        for metric in payload["metrics"]
    )
