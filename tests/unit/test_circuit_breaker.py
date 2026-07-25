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
from core.providers.breaker_exceptions import CallRejectedError
from core.providers.breaker_policy import BreakerPolicy
from core.providers.breaker_state import CircuitState
from core.providers.manager import ProviderManager
from core.providers.registry import ProviderRegistry

# --- Mock Provider ---


class FailingProvider(ProviderLifecycle):
    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def ready(self):
        return True

    async def health(self):
        return HealthStatus.HEALTHY

    def metrics(self):
        return ProviderMetrics()

    async def call_api(self):
        raise RuntimeError("Cloud service is down")


# --- Tests ---


@pytest.mark.asyncio
async def test_circuit_breaker_flow():
    reg = ProviderRegistry()
    # Policy: Open after 2 failures, recovery after 1 second
    policy = BreakerPolicy(failure_threshold=2, recovery_timeout=1)

    mgr = ProviderManager(registry=reg)
    # Manually inject policy for this test
    mgr._breaker._policies["official:failing"] = policy

    reg.register(
        ProviderMetadata(
            provider_id="failing", name="F", version="1", provider_type="ai"
        ),
        FailingProvider,
    )

    p = await mgr.get_provider("official:failing")

    # 1. State: CLOSED
    assert mgr._breaker.get_state("official:failing") == CircuitState.CLOSED

    # 2. Trigger Failures
    for _ in range(2):
        try:
            await p.call_api()
        except RuntimeError:
            pass

    # 3. State: OPEN
    assert mgr._breaker.get_state("official:failing") == CircuitState.OPEN

    # 4. Request should be rejected
    with pytest.raises(CallRejectedError):
        await p.call_api()

    # 5. Wait for recovery timeout
    time.sleep(1.1)

    # 6. allow_request should transition to HALF_OPEN
    assert mgr._breaker.allow_request("official:failing") == True
    assert mgr._breaker.get_state("official:failing") == CircuitState.HALF_OPEN

    # 7. Successful trial closes circuit
    # We need to simulate a success since our mock always fails.
    # For the sake of this test, we can use a different method that succeeds if we add one.


@pytest.mark.asyncio
async def test_half_open_to_closed():
    class ConditionalProvider(FailingProvider):
        def __init__(self):
            self.fail = True

        async def call_api(self):
            if self.fail:
                raise RuntimeError("Fail")
            return "Success"

    reg = ProviderRegistry()
    policy = BreakerPolicy(
        failure_threshold=1, recovery_timeout=0.1, success_threshold=1
    )
    mgr = ProviderManager(registry=reg)
    mgr._breaker._policies["official:cond"] = policy

    reg.register(
        ProviderMetadata(provider_id="cond", name="C", version="1", provider_type="ai"),
        ConditionalProvider,
    )

    p = await mgr.get_provider("official:cond")

    # Trip it
    try:
        await p.call_api()
    except:
        pass
    assert mgr._breaker.get_state("official:cond") == CircuitState.OPEN

    time.sleep(0.2)

    # Now in HALF_OPEN trial
    p._instance.fail = False  # Reach into proxy to change state for test
    await p.call_api()

    assert mgr._breaker.get_state("official:cond") == CircuitState.CLOSED


if __name__ == "__main__":

    async def run_all():
        print("Running Circuit Breaker tests...")
        await test_circuit_breaker_flow()
        print("✅ Basic flow passed (Closed -> Open -> Half-Open)")
        await test_half_open_to_closed()
        print("✅ Recovery passed (Half-Open -> Closed)")

    asyncio.run(run_all())
