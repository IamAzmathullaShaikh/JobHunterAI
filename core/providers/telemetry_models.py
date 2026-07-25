from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ProviderStats(BaseModel):
    """Aggregated operational metrics for a single provider."""

    provider_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    # Latency (ms)
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0

    # Usage & Cost
    total_tokens: int = 0
    total_estimated_cost_usd: float = 0.0

    # Lifecycle
    circuit_open_count: int = 0
    availability: float = 1.0  # 0.0 to 1.0
    last_failure_at: Optional[str] = None

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests


class TelemetrySnapshot(BaseModel):
    """A point-in-time state of the entire platform telemetry."""

    global_total_requests: int
    global_success_rate: float
    providers: Dict[str, ProviderStats]
