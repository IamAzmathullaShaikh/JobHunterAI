import sys
import time
from pathlib import Path

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio

import pytest

from core.providers.base import (HealthStatus, ProviderLifecycle,
                                 ProviderMetadata, ProviderMetrics)
from core.providers.manager import ProviderManager
from core.providers.registry import ProviderRegistry
from core.providers.telemetry import engine
from core.providers.telemetry_dispatcher import dispatcher
from core.providers.telemetry_events import (CircuitStateChanged,
                                             ProviderInvocationCompleted,
                                             ProviderInvocationFailed)
from core.providers.telemetry_subscriber import BaseTelemetrySubscriber

# --- Mock Subscriber ---


class MockSubscriber(BaseTelemetrySubscriber):
    def __init__(self):
        self.received_events = []

    def on_event(self, event):
        self.received_events.append(event)


# --- Tests ---


@pytest.mark.asyncio
async def test_event_publication():
    sub = MockSubscriber()
    dispatcher.subscribe(sub)

    event = ProviderInvocationCompleted(
        provider_id="test-p", method="generate", latency_ms=100.0
    )
    dispatcher.publish(event)

    assert len(sub.received_events) == 1
    assert sub.received_events[0].provider_id == "test-p"

    dispatcher.unsubscribe(sub)
    dispatcher.publish(event)
    assert len(sub.received_events) == 1  # No new event after unsubscribe


@pytest.mark.asyncio
async def test_metrics_aggregation():
    engine.reset()

    # Simulate 3 successful requests with varying latencies
    latencies = [100.0, 200.0, 300.0]
    for lat in latencies:
        dispatcher.publish(
            ProviderInvocationCompleted(
                provider_id="agg-p", method="search", latency_ms=lat
            )
        )

    stats = engine.get_metrics("agg-p")
    assert stats.successful_requests == 3
    assert stats.average_latency_ms == 200.0

    # Simulate a failure
    dispatcher.publish(
        ProviderInvocationFailed(
            provider_id="agg-p",
            method="search",
            latency_ms=50.0,
            error_type="Timeout",
            error_message="Service timed out",
        )
    )

    stats = engine.get_metrics("agg-p")
    assert stats.failed_requests == 1
    assert (
        stats.total_requests == 0
    )  # Started events increment this, we only sent Completed/Failed here

    # Add a started event
    from core.providers.telemetry_events import ProviderInvocationStarted

    dispatcher.publish(ProviderInvocationStarted(provider_id="agg-p", method="search"))
    assert engine.get_metrics("agg-p").total_requests == 1


@pytest.mark.asyncio
async def test_snapshot_generation():
    engine.reset()
    dispatcher.publish(
        ProviderInvocationCompleted(provider_id="p1", method="m", latency_ms=10)
    )
    dispatcher.publish(
        ProviderInvocationCompleted(provider_id="p2", method="m", latency_ms=20)
    )

    snap = engine.snapshot()
    assert len(snap.providers) == 2
    assert snap.global_success_rate == 1.0


if __name__ == "__main__":

    async def run_all():
        print("Running Telemetry tests...")
        await test_event_publication()
        print("✅ Event Pub/Sub passed")
        await test_metrics_aggregation()
        print("✅ Metrics Aggregation passed")
        await test_snapshot_generation()
        print("✅ Snapshot passed")

    asyncio.run(run_all())
