import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio

import pytest

from core.container import container
from core.lifecycle import AppLifecycleManager
from core.providers.telemetry_events import TelemetryEventType


@pytest.mark.asyncio
async def test_container_singleton():
    from core.container import DIContainer

    c1 = DIContainer.get_instance()
    c2 = DIContainer.get_instance()
    assert c1 is c2
    assert c1.settings is not None
    print("✅ DI Container singleton verified.")


@pytest.mark.asyncio
async def test_lifecycle_startup_shutdown():
    # Capture events to verify publication
    events = []

    def subscriber(event):
        events.append(event)

    # We can't easily mock the whole class in a simple script without a full framework,
    # but we can subscribe to the real dispatcher.
    from core.providers.telemetry_subscriber import BaseTelemetrySubscriber

    class MockSub(BaseTelemetrySubscriber):
        def on_event(self, e):
            events.append(e)

    sub = MockSub()
    container.telemetry_dispatcher.subscribe(sub)

    # 1. Test Startup
    # We need to bypass actual DB init for a unit test if possible, or just let it hit the test db
    await AppLifecycleManager.startup()

    # Verify events
    types = [e.event_type for e in events]
    assert "app_starting" in types
    assert "app_ready" in types
    assert container.registry._is_frozen == True
    print("✅ Lifecycle Startup verified.")

    # 2. Test Shutdown
    await AppLifecycleManager.shutdown()
    types = [e.event_type for e in events]
    assert "app_stopping" in types
    print("✅ Lifecycle Shutdown verified.")


if __name__ == "__main__":

    async def run_all():
        print("Running DI & Lifecycle tests...")
        await test_container_singleton()
        await test_lifecycle_startup_shutdown()
        print("🎉 All M5.8 Unit Tests Passed.")

    asyncio.run(run_all())
