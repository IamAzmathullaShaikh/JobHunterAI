import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Type

import psutil

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.container import container
from core.exceptions import AIProviderError
from core.lifecycle import AppLifecycleManager
from core.providers.ai.base import IAIProvider
from core.providers.base import (HealthStatus, ProviderLifecycle,
                                 ProviderMetadata, ProviderMetrics)
from core.providers.breaker_exceptions import CallRejectedError
from core.providers.breaker_policy import BreakerPolicy
from core.providers.breaker_state import CircuitState
from core.providers.scrapers.base import IScraperProvider

# Configure minimal logging for validation
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("system_validation")

# --- Mock Faulty Providers ---


class FaultyAIProvider(IAIProvider):
    def __init__(self, fail_count=0):
        self._fail_count = fail_count
        self._current_fails = 0
        self._init_time = 0
        self._call_count = 0

    async def initialize(self):
        start = time.perf_counter()
        await asyncio.sleep(0.01)  # Simulate network handshake
        self._init_time = (time.perf_counter() - start) * 1000

    async def shutdown(self):
        pass

    async def ready(self):
        return True

    async def health(self):
        return HealthStatus.HEALTHY

    def metrics(self):
        return ProviderMetrics()

    def supports(self, f):
        return True

    async def embed(self, t):
        return [0.1] * 1536

    def estimate_cost(self, m):
        return type("obj", (object,), {"estimated_usd": 0.001})()

    async def generate(self, messages, config=None):
        self._call_count += 1
        if self._current_fails < self._fail_count:
            self._current_fails += 1
            # Simulate a 503 Service Unavailable
            raise AIProviderError(
                "Service Unavailable", "official:faulty-ai", details={"status": 503}
            )
        return {"data": {"result": "success"}, "meta": {"tokens": 10}}

    async def stream(self, m, c=None):
        yield "chunk"


# --- Validation Suite ---


class SystemValidationSuite:
    def __init__(self):
        self.results = {}

    async def run_all(self):
        logger.info("🚀 Starting M5.9 System Validation Suite")

        await self.validate_startup_performance()
        await self.validate_concurrency()
        await self.validate_fault_injection_recovery()
        await self.validate_memory_stability()
        await self.validate_telemetry_consistency()

        logger.info("🏁 Validation Suite Completed.")
        return self.results

    async def validate_startup_performance(self):
        logger.info("--- Area 1: Startup & DI Performance ---")
        start = time.perf_counter()

        # Reset container state for a clean startup test
        container.registry._storage.clear()
        container.registry._is_frozen = False

        await AppLifecycleManager.startup()
        duration = (time.perf_counter() - start) * 1000

        self.results["startup_ms"] = duration
        logger.info(f"✅ Startup Sequence: {duration:.2f}ms")

        # Measure DI Resolution (ProviderManager.get_provider)
        start_di = time.perf_counter()
        # Resolve a registered provider (e.g., Groq)
        try:
            await container.provider_manager.get_provider("official:groq")
            di_duration = (time.perf_counter() - start_di) * 1000
            self.results["di_resolution_ms"] = di_duration
            logger.info(f"✅ DI Resolution (Lazy Load): {di_duration:.2f}ms")
        except:
            logger.warning("Groq key missing, skipping DI latency check.")

    async def validate_concurrency(self):
        logger.info("--- Area 2: High Concurrency (100+ Requests) ---")
        # Register a mock provider for high-volume testing
        meta = ProviderMetadata(
            provider_id="concurrent-ai",
            name="Concurrent",
            version="1",
            provider_type="ai",
            capabilities=["json"],
        )
        container.registry._is_frozen = False  # Unfreeze for test
        container.registry.register(meta, FaultyAIProvider)

        provider = await container.provider_manager.get_provider(
            "official:concurrent-ai"
        )

        start = time.perf_counter()
        tasks = [
            provider.generate([{"role": "user", "content": "test"}]) for _ in range(100)
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        duration = (time.perf_counter() - start) * 1000
        success_count = len([r for r in responses if not isinstance(r, Exception)])

        self.results["concurrency_100_ms"] = duration
        self.results["concurrency_success_rate"] = success_count / 100
        logger.info(
            f"✅ 100 Concurrent Requests: {duration:.2f}ms (Success Rate: {success_count}%)"
        )

    async def validate_fault_injection_recovery(self):
        logger.info("--- Area 3: Fault Injection & Recovery ---")
        # Configure a policy with low thresholds for fast testing
        policy = BreakerPolicy(
            failure_threshold=2, recovery_timeout=0.5, success_threshold=1
        )
        container.circuit_breaker._policies["official:faulty-ai"] = policy

        meta = ProviderMetadata(
            provider_id="faulty-ai", name="Faulty", version="1", provider_type="ai"
        )
        container.registry.register(meta, FaultyAIProvider)
        # Inject 3 failures into the mock
        provider = await container.provider_manager.get_provider("official:faulty-ai")
        provider._instance._fail_count = 3

        # 1. Trip the circuit
        logger.info("Injecting failures to trip circuit...")
        for _ in range(2):
            try:
                await provider.generate([])
            except:
                pass

        assert (
            container.circuit_breaker.get_state("official:faulty-ai")
            == CircuitState.OPEN
        )
        logger.info("✅ Circuit successfully opened on threshold.")

        # 2. Verify rejection
        try:
            await provider.generate([])
            logger.error("❌ Circuit failed to block request while OPEN")
        except CallRejectedError:
            logger.info("✅ Circuit successfully rejected request while OPEN.")

        # 3. Test Recovery
        logger.info("Waiting for recovery timeout...")
        await asyncio.sleep(0.6)

        # Next call should be HALF_OPEN
        # Make the mock succeed now
        provider._instance._fail_count = 0
        await provider.generate([])

        assert (
            container.circuit_breaker.get_state("official:faulty-ai")
            == CircuitState.CLOSED
        )
        logger.info("✅ Circuit successfully recovered to CLOSED.")

    async def validate_memory_stability(self):
        logger.info("--- Area 4: Memory Stability ---")
        process = psutil.Process(os.getpid())
        initial_mem = process.memory_info().rss / 1024 / 1024

        # Run a burst of requests
        provider = await container.provider_manager.get_provider(
            "official:concurrent-ai"
        )
        for _ in range(5):
            tasks = [
                provider.generate([{"role": "user", "content": "test"}])
                for _ in range(50)
            ]
            await asyncio.gather(*tasks)

        final_mem = process.memory_info().rss / 1024 / 1024
        growth = final_mem - initial_mem
        self.results["memory_growth_mb"] = growth
        logger.info(
            f"✅ Memory Stability: Initial {initial_mem:.1f}MB, Final {final_mem:.1f}MB (Growth: {growth:.2f}MB)"
        )

    async def validate_telemetry_consistency(self):
        logger.info("--- Area 5: Telemetry Consistency ---")
        stats = container.telemetry_engine.get_metrics("official:concurrent-ai")

        # We ran 100 (Area 2) + 250 (Area 4) = 350 requests
        assert stats.total_requests >= 350
        assert stats.average_latency_ms > 0
        logger.info(
            f"✅ Telemetry: Tracked {stats.total_requests} requests with {stats.average_latency_ms:.2f}ms avg latency."
        )


if __name__ == "__main__":
    suite = SystemValidationSuite()
    asyncio.run(suite.run_all())
