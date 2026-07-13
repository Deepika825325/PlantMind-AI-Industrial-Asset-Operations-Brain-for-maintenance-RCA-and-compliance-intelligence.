from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.observability.metrics import PrometheusMetricStore


client = TestClient(app)


def test_metrics_endpoint_returns_prometheus_text() -> None:
    client.get(
        "/observability/health"
    )

    response = client.get(
        "/metrics"
    )

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    body = response.text

    assert "plantmind_http_requests_total" in body
    assert "plantmind_http_errors_total" in body
    assert "plantmind_http_request_p95_latency_ms" in body
    assert "plantmind_worker_failures_total" in body
    assert "plantmind_queue_depth" in body
    assert "plantmind_retrieval_latency_p95_ms" in body
    assert "plantmind_model_latency_p95_ms" in body
    assert "plantmind_prediction_distribution_total" in body
    assert "plantmind_unsupported_answers_total" in body
    assert "plantmind_active_simulations" in body


def test_metric_store_records_worker_queue_prediction_and_latency_metrics() -> None:
    store = PrometheusMetricStore()

    store.record_worker_failure(
        worker_name="document_extraction_worker",
        failure_type="parse_error",
    )
    store.set_queue_depth(
        queue_name="document_extraction",
        depth=7,
    )
    store.observe_retrieval_latency(
        route="/ask",
        latency_ms=41.0,
    )
    store.observe_retrieval_latency(
        route="/ask",
        latency_ms=84.0,
    )
    store.observe_model_latency(
        model_name="plantmind-p101-anomaly-detector",
        model_version="v0.3.11",
        latency_ms=18.5,
    )
    store.record_prediction(
        model_name="plantmind-p101-anomaly-detector",
        prediction_label="anomaly",
    )
    store.record_unsupported_answer(
        route="/ask",
        reason="insufficient_evidence",
    )
    store.set_active_simulations(
        simulation_type="p101_replay",
        count=2,
    )

    body = store.snapshot_prometheus_text()

    assert 'worker_name="document_extraction_worker"' in body
    assert 'queue_name="document_extraction"' in body
    assert 'route="/ask"' in body
    assert 'model_name="plantmind-p101-anomaly-detector"' in body
    assert 'prediction_label="anomaly"' in body
    assert 'reason="insufficient_evidence"' in body
    assert 'simulation_type="p101_replay"' in body


def test_request_middleware_records_success_and_error_requests() -> None:
    ok_response = client.get(
        "/observability/health"
    )
    missing_response = client.get(
        "/route-that-does-not-exist"
    )
    metrics_response = client.get(
        "/metrics"
    )

    assert ok_response.status_code == 200
    assert missing_response.status_code == 404
    assert metrics_response.status_code == 200

    body = metrics_response.text

    assert 'status_code="200"' in body
    assert 'status_code="404"' in body
    assert "plantmind_http_errors_total" in body