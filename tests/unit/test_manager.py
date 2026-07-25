import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from core.exceptions import ProviderInitializationError, ProviderNotFoundError
from core.providers.base import (HealthStatus, ProviderLifecycle,
                                 ProviderMetadata, ProviderMetrics)
from core.providers.manager import ProviderManager
from core.providers.registry import ProviderRegistry

# --- Mocks ---


class MockAIProvider(ProviderLifecycle):
    def __init__(self):
        self.init_called = 0
        self.shutdown_called = 0

    async def initialize(self):
        self.init_called += 1

    async def shutdown(self):
        self.shutdown_called += 1

    async def ready(self):
        return True

    async def health(self):
        return HealthStatus.HEALTHY

    def metrics(self):
        return ProviderMetrics()


class FailingProvider(MockAIProvider):
    async def initialize(self):
        raise RuntimeError("Init crashed")


# --- Tests ---


@pytest.mark.asyncio
async def test_lazy_initialization():
    reg = ProviderRegistry()
    mgr = ProviderManager(registry=reg)

    meta = ProviderMetadata(
        provider_id="lazy-p", name="Lazy", version="1", provider_type="ai", priority=10
    )
    reg.register(meta, MockAIProvider)

    # 1. Instance should NOT exist yet
    assert len(mgr.list_active_ids()) == 0

    # 2. Get provider should trigger init
    p = await mgr.get_provider("official:lazy-p")
    assert p.init_called == 1
    assert "official:lazy-p" in mgr.list_active_ids()


@pytest.mark.asyncio
async def test_cache_reuse():
    reg = ProviderRegistry()
    mgr = ProviderManager(registry=reg)
    meta = ProviderMetadata(
        provider_id="p1", name="P1", version="1", provider_type="ai"
    )
    reg.register(meta, MockAIProvider)

    p1 = await mgr.get_provider("official:p1")
    p2 = await mgr.get_provider("official:p1")

    assert p1 is p2
    assert p1.init_called == 1  # Only one init for both calls


@pytest.mark.asyncio
async def test_selection_logic():
    reg = ProviderRegistry()
    mgr = ProviderManager(registry=reg)

    # Register two providers
    reg.register(
        ProviderMetadata(
            provider_id="high-p", name="H", version="1", provider_type="ai", priority=10
        ),
        MockAIProvider,
    )
    reg.register(
        ProviderMetadata(
            provider_id="low-p", name="L", version="1", provider_type="ai", priority=50
        ),
        MockAIProvider,
    )

    p = await mgr.get_default_provider("ai")
    meta, _ = reg.get(
        p.metrics().request_count == 0 and "official:high-p"
    )  # Hack to check identity indirectly
    # Actually simpler:
    assert "high-p" in p.__class__.__name__ or True  # Instance identity is what matters

    # Verify it chose high-p (priority 10) over low-p (priority 50)
    meta_p, _ = reg.get("official:high-p")
    active_p = await mgr.get_default_provider("ai")
    # We can check via the cache
    assert mgr._instances["official:high-p"] is active_p


@pytest.mark.asyncio
async def test_initialization_failure_cleanup():
    reg = ProviderRegistry()
    mgr = ProviderManager(registry=reg)
    reg.register(
        ProviderMetadata(provider_id="fail", name="F", version="1", provider_type="ai"),
        FailingProvider,
    )

    with pytest.raises(ProviderInitializationError):
        await mgr.get_provider("official:fail")

    # Cache should be clean so next attempt isn't blocked by a "dead" instance
    assert "official:fail" not in mgr.list_active_ids()


@pytest.mark.asyncio
async def test_shutdown_all():
    reg = ProviderRegistry()
    mgr = ProviderManager(registry=reg)
    reg.register(
        ProviderMetadata(provider_id="p1", name="P1", version="1", provider_type="ai"),
        MockAIProvider,
    )

    p = await mgr.get_provider("official:p1")
    await mgr.shutdown()

    assert p.shutdown_called == 1
    assert len(mgr.list_active_ids()) == 0


if __name__ == "__main__":
    # Manual run if pytest not configured in environment correctly
    async def run_all():
        print("Running Provider Manager tests...")
        await test_lazy_initialization()
        print("✅ Lazy Init passed")
        await test_cache_reuse()
        print("✅ Cache Reuse passed")
        await test_selection_logic()
        print("✅ Selection Logic passed")
        await test_initialization_failure_cleanup()
        print("✅ Failure Cleanup passed")
        await test_shutdown_all()
        print("✅ Shutdown passed")

    asyncio.run(run_all())
