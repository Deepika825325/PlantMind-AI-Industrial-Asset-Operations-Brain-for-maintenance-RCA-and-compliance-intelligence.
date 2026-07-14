from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app


def test_p101_closed_loop_demo_reset_and_run() -> None:
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:
        reset_response = client.post(
            "/demo/p101/reset"
        )

        assert reset_response.status_code == 200

        reset_payload = reset_response.json()

        assert reset_payload["asset_id"] == "P-101"
        assert reset_payload["status"] == "not_started"
        assert reset_payload["completed_steps"] == 0
        assert len(reset_payload["steps"]) == 7

        run_response = client.post(
            "/demo/p101/run-closed-loop"
        )

        assert run_response.status_code == 200

        run_payload = run_response.json()[
            "state"
        ]

        assert run_payload["status"] == "completed"
        assert run_payload["completed_steps"] == 7
        assert run_payload["total_steps"] == 7
        assert all(
            step["status"] == "passed"
            for step in run_payload["steps"]
        )
        assert any(
            "RCA-P101-001" in step["evidence_used"]
            for step in run_payload["steps"]
        )


def test_p101_closed_loop_timeline_endpoint() -> None:
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:
        client.post(
            "/demo/p101/run-closed-loop"
        )

        response = client.get(
            "/demo/p101/timeline"
        )

        assert response.status_code == 200

        payload = response.json()

        assert payload["demo_id"] == "p101-closed-loop-demo"
        assert payload["asset_id"] == "P-101"
        assert len(payload["timeline"]) == 7
