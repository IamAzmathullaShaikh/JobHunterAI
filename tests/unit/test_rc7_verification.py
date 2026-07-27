import pytest
import asyncio
from core.ai.smart_router import route
from core.privacy import redactor
from core.providers.apify.registry import ApifyActorRegistry
from core.providers.apify.selector import ApifyActorSelector

@pytest.mark.asyncio
async def test_n_tier_routing_logic():
    async def t1(**kw): raise ValueError("fail")
    async def t2(**kw): return "success"
    res = await route(t1, t2)
    assert res == "success"

def test_pii_atomic_redaction():
    text = "Contact john.doe@example.com"
    redacted, mapping = redactor.redact(text)
    assert "john.doe@example.com" not in redacted
    assert "[[REDACTED_EMAIL_" in redacted
    restored = redactor.restore(redacted, mapping)
    assert restored == text

def test_apify_selector_priority():
    # Minimal mock registry
    class MockReg:
        def get_enabled_actors(self):
            return [
                {"id": "a", "priority": 10, "capabilities": ["linkedin"]},
                {"id": "b", "priority": 1, "capabilities": ["google"]}
            ]
        def is_actor_healthy(self, id): return True

    sel = ApifyActorSelector(MockReg())
    best = sel.select_actor("search")
    assert best["id"] == "b" # Highest priority (1 < 10)
