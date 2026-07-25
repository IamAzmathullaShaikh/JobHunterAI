import logging
import statistics
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.providers.telemetry_dispatcher import dispatcher
from core.providers.telemetry_events import (BaseTelemetryEvent,
                                             CircuitStateChanged,
                                             ProviderInvocationCompleted,
                                             ProviderInvocationFailed,
                                             TelemetryEventType)
from core.providers.telemetry_models import ProviderStats, TelemetrySnapshot
from core.providers.telemetry_subscriber import BaseTelemetrySubscriber

logger = logging.getLogger(__name__)


class TelemetryEngine(BaseTelemetrySubscriber):
    """
    Main aggregator for provider platform observability.
    Calculates live metrics from the event stream.
    """

    def __init__(self):
        self._provider_data: Dict[str, ProviderStats] = {}
        self._latencies: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def on_event(self, event: BaseTelemetryEvent) -> None:
        """Processes incoming events and updates aggregated metrics."""
        with self._lock:
            if event.provider_id not in self._provider_data:
                self._provider_data[event.provider_id] = ProviderStats(
                    provider_id=event.provider_id
                )
                self._latencies[event.provider_id] = []

            stats = self._provider_data[event.provider_id]

            if event.event_type == TelemetryEventType.PROVIDER_INVOCATION_STARTED:
                stats.total_requests += 1

            elif isinstance(event, ProviderInvocationCompleted):
                stats.successful_requests += 1
                self._update_latency(event.provider_id, event.latency_ms)
                if event.token_usage:
                    stats.total_tokens += event.token_usage
                if event.estimated_cost_usd:
                    stats.total_estimated_cost_usd += event.estimated_cost_usd

            elif isinstance(event, ProviderInvocationFailed):
                stats.failed_requests += 1
                stats.last_failure_at = event.timestamp.isoformat()
                self._update_latency(event.provider_id, event.latency_ms)

            elif isinstance(event, CircuitStateChanged):
                if event.new_state == "open":
                    stats.circuit_open_count += 1

    def _update_latency(self, provider_id: str, latency_ms: float) -> None:
        """Internal helper to calculate percentiles."""
        history = self._latencies[provider_id]
        history.append(latency_ms)

        # Keep window of last 1000 requests for percentile accuracy without memory bloat
        if len(history) > 1000:
            history.pop(0)

        stats = self._provider_data[provider_id]
        stats.average_latency_ms = sum(history) / len(history)

        if len(history) >= 10:
            sorted_latencies = sorted(history)
            stats.p95_latency_ms = sorted_latencies[int(len(history) * 0.95)]
            stats.p99_latency_ms = sorted_latencies[int(len(history) * 0.99)]

    def get_metrics(self, provider_id: str) -> Optional[ProviderStats]:
        """Returns current stats for a specific provider."""
        with self._lock:
            return self._provider_data.get(provider_id)

    def snapshot(self) -> TelemetrySnapshot:
        """Returns a complete platform metrics view."""
        with self._lock:
            total_reqs = sum(p.total_requests for p in self._provider_data.values())
            total_success = sum(
                p.successful_requests for p in self._provider_data.values()
            )
            success_rate = total_success / total_reqs if total_reqs > 0 else 1.0

            return TelemetrySnapshot(
                global_total_requests=total_reqs,
                global_success_rate=success_rate,
                providers={
                    pid: stats.model_copy()
                    for pid, stats in self._provider_data.items()
                },
            )

    def reset(self) -> None:
        """Clears all accumulated metrics."""
        with self._lock:
            self._provider_data.clear()
            self._latencies.clear()


# Initialize global engine and register with dispatcher
engine = TelemetryEngine()
dispatcher.subscribe(engine)
