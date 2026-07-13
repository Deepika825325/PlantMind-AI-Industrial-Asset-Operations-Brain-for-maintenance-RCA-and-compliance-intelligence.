from __future__ import annotations

import math
import threading
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from time import perf_counter
from typing import DefaultDict


@dataclass
class PrometheusMetricStore:
    request_count: Counter[str] = field(default_factory=Counter)
    error_count: Counter[str] = field(default_factory=Counter)
    request_latencies_ms: DefaultDict[str, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    worker_failures: Counter[str] = field(default_factory=Counter)
    queue_depth: dict[str, float] = field(default_factory=dict)
    retrieval_latencies_ms: DefaultDict[str, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    model_latencies_ms: DefaultDict[str, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    prediction_distribution: Counter[str] = field(default_factory=Counter)
    unsupported_answer_count: Counter[str] = field(default_factory=Counter)
    active_simulations: dict[str, float] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def record_request(
        self,
        *,
        method: str,
        path: str,
        status_code: int,
        latency_ms: float,
    ) -> None:
        normalized_path = self._normalize_path(
            path
        )

        labels = self._labels(
            method=method,
            path=normalized_path,
            status_code=str(status_code),
        )

        with self.lock:
            self.request_count[labels] += 1
            self.request_latencies_ms[
                self._labels(
                    method=method,
                    path=normalized_path,
                )
            ].append(
                latency_ms
            )

            if status_code >= 400:
                self.error_count[labels] += 1

    def record_worker_failure(
        self,
        *,
        worker_name: str,
        failure_type: str,
    ) -> None:
        with self.lock:
            self.worker_failures[
                self._labels(
                    worker_name=worker_name,
                    failure_type=failure_type,
                )
            ] += 1

    def set_queue_depth(
        self,
        *,
        queue_name: str,
        depth: float,
    ) -> None:
        with self.lock:
            self.queue_depth[
                self._labels(
                    queue_name=queue_name,
                )
            ] = depth

    def observe_retrieval_latency(
        self,
        *,
        route: str,
        latency_ms: float,
    ) -> None:
        with self.lock:
            self.retrieval_latencies_ms[
                self._labels(
                    route=route,
                )
            ].append(
                latency_ms
            )

    def observe_model_latency(
        self,
        *,
        model_name: str,
        model_version: str,
        latency_ms: float,
    ) -> None:
        with self.lock:
            self.model_latencies_ms[
                self._labels(
                    model_name=model_name,
                    model_version=model_version,
                )
            ].append(
                latency_ms
            )

    def record_prediction(
        self,
        *,
        model_name: str,
        prediction_label: str,
    ) -> None:
        with self.lock:
            self.prediction_distribution[
                self._labels(
                    model_name=model_name,
                    prediction_label=prediction_label,
                )
            ] += 1

    def record_unsupported_answer(
        self,
        *,
        route: str,
        reason: str,
    ) -> None:
        with self.lock:
            self.unsupported_answer_count[
                self._labels(
                    route=route,
                    reason=reason,
                )
            ] += 1

    def set_active_simulations(
        self,
        *,
        simulation_type: str,
        count: float,
    ) -> None:
        with self.lock:
            self.active_simulations[
                self._labels(
                    simulation_type=simulation_type,
                )
            ] = count

    def snapshot_prometheus_text(self) -> str:
        with self.lock:
            lines: list[str] = []

            self._write_counter(
                lines=lines,
                name="plantmind_http_requests_total",
                help_text="Total HTTP requests processed by PlantMind.",
                values=self.request_count,
            )

            self._write_counter(
                lines=lines,
                name="plantmind_http_errors_total",
                help_text="Total HTTP error responses emitted by PlantMind.",
                values=self.error_count,
            )

            self._write_gauge_from_latency(
                lines=lines,
                name="plantmind_http_request_p95_latency_ms",
                help_text="HTTP request p95 latency in milliseconds.",
                values=self.request_latencies_ms,
            )

            self._write_counter(
                lines=lines,
                name="plantmind_worker_failures_total",
                help_text="Total worker failures grouped by worker and failure type.",
                values=self.worker_failures,
            )

            self._write_gauge(
                lines=lines,
                name="plantmind_queue_depth",
                help_text="Current queue depth grouped by queue.",
                values=self.queue_depth,
            )

            self._write_gauge_from_latency(
                lines=lines,
                name="plantmind_retrieval_latency_p95_ms",
                help_text="Retrieval p95 latency in milliseconds.",
                values=self.retrieval_latencies_ms,
            )

            self._write_gauge_from_latency(
                lines=lines,
                name="plantmind_model_latency_p95_ms",
                help_text="Model inference p95 latency in milliseconds.",
                values=self.model_latencies_ms,
            )

            self._write_counter(
                lines=lines,
                name="plantmind_prediction_distribution_total",
                help_text="Prediction distribution grouped by model and prediction label.",
                values=self.prediction_distribution,
            )

            self._write_counter(
                lines=lines,
                name="plantmind_unsupported_answers_total",
                help_text="Unsupported or insufficient-evidence answer count.",
                values=self.unsupported_answer_count,
            )

            self._write_gauge(
                lines=lines,
                name="plantmind_active_simulations",
                help_text="Currently active simulations.",
                values=self.active_simulations,
            )

            return "\n".join(lines).rstrip() + "\n"

    def seed_demo_metrics(self) -> None:
        self.set_queue_depth(
            queue_name="document_extraction",
            depth=2,
        )
        self.set_queue_depth(
            queue_name="telemetry_replay",
            depth=1,
        )
        self.observe_retrieval_latency(
            route="/ask",
            latency_ms=42.5,
        )
        self.observe_model_latency(
            model_name="plantmind-p101-anomaly-detector",
            model_version="v0.3.11",
            latency_ms=18.0,
        )
        self.record_prediction(
            model_name="plantmind-p101-anomaly-detector",
            prediction_label="anomaly",
        )
        self.record_prediction(
            model_name="plantmind-p101-anomaly-detector",
            prediction_label="normal",
        )
        self.record_unsupported_answer(
            route="/ask",
            reason="insufficient_evidence",
        )
        self.set_active_simulations(
            simulation_type="p101_replay",
            count=1,
        )

    def _write_counter(
        self,
        *,
        lines: list[str],
        name: str,
        help_text: str,
        values: Counter[str],
    ) -> None:
        lines.append(
            f"# HELP {name} {help_text}"
        )
        lines.append(
            f"# TYPE {name} counter"
        )

        if not values:
            lines.append(
                f"{name} 0"
            )
            return

        for labels, value in sorted(
            values.items()
        ):
            lines.append(
                f"{name}{labels} {float(value)}"
            )

    def _write_gauge(
        self,
        *,
        lines: list[str],
        name: str,
        help_text: str,
        values: dict[str, float],
    ) -> None:
        lines.append(
            f"# HELP {name} {help_text}"
        )
        lines.append(
            f"# TYPE {name} gauge"
        )

        if not values:
            lines.append(
                f"{name} 0"
            )
            return

        for labels, value in sorted(
            values.items()
        ):
            lines.append(
                f"{name}{labels} {float(value)}"
            )

    def _write_gauge_from_latency(
        self,
        *,
        lines: list[str],
        name: str,
        help_text: str,
        values: DefaultDict[str, list[float]],
    ) -> None:
        lines.append(
            f"# HELP {name} {help_text}"
        )
        lines.append(
            f"# TYPE {name} gauge"
        )

        if not values:
            lines.append(
                f"{name} 0"
            )
            return

        for labels, samples in sorted(
            values.items()
        ):
            lines.append(
                f"{name}{labels} {self._p95(samples)}"
            )

    def _p95(
        self,
        samples: list[float],
    ) -> float:
        if not samples:
            return 0.0

        sorted_samples = sorted(
            samples
        )
        index = math.ceil(
            0.95 * len(sorted_samples)
        ) - 1

        return round(
            sorted_samples[
                max(
                    0,
                    min(
                        index,
                        len(sorted_samples) - 1,
                    ),
                )
            ],
            4,
        )

    def _labels(
        self,
        **labels: str,
    ) -> str:
        if not labels:
            return ""

        rendered = ",".join(
            f'{key}="{self._escape(value)}"'
            for key, value in sorted(
                labels.items()
            )
        )

        return "{" + rendered + "}"

    def _escape(
        self,
        value: str,
    ) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace("\n", "\\n")
            .replace('"', '\\"')
        )

    def _normalize_path(
        self,
        path: str,
    ) -> str:
        if not path:
            return "/"

        if path.startswith(
            "/docs"
        ) or path.startswith(
            "/openapi"
        ):
            return path

        parts = []

        for part in path.split(
            "/"
        ):
            if not part:
                continue

            if part.upper().startswith(
                "P-"
            ):
                parts.append(
                    "{asset_id}"
                )
            elif part.startswith(
                "WO-"
            ) or part.startswith(
                "MWO-"
            ):
                parts.append(
                    "{work_order_id}"
                )
            elif part.startswith(
                "RCA-"
            ):
                parts.append(
                    "{rca_case_id}"
                )
            else:
                parts.append(
                    part
                )

        return "/" + "/".join(
            parts
        )


metrics_store = PrometheusMetricStore()
metrics_store.seed_demo_metrics()


class Timer:
    def __init__(
        self,
    ) -> None:
        self.start = perf_counter()

    def elapsed_ms(
        self,
    ) -> float:
        return (
            perf_counter() - self.start
        ) * 1000.0