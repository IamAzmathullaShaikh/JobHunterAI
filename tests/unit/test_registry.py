import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio

from core.exceptions import ProviderRegistrationError
from core.providers.base import (HealthStatus, ProviderLifecycle,
                                 ProviderMetadata, ProviderMetrics)
from core.providers.registry import ProviderRegistry


# Mock Provider Implementation
class ValidProvider(ProviderLifecycle):
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


class InvalidProvider:  # Does not inherit
    pass


class PartialProvider(ProviderLifecycle):  # Missing metrics()
    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def ready(self):
        return True

    async def health(self):
        return HealthStatus.HEALTHY


def test_registry_pipeline():
    reg = ProviderRegistry()

    # 1. Test Valid Registration
    meta = ProviderMetadata(
        provider_id="test-provider",
        name="Test Provider",
        version="1.0.0",
        provider_type="ai",
        capabilities=["vision", "streaming"],
    )
    reg.register(meta, ValidProvider)
    assert reg.exists("official:test-provider")
    assert len(reg.get_by_capability("vision")) == 1
    print("✅ Valid registration passed.")

    # 2. Test Duplicate Detection
    try:
        reg.register(meta, ValidProvider)
    except ProviderRegistrationError:
        print("✅ Duplicate detection passed.")

    # 3. Test Inheritance Validation
    try:
        reg.register(
            meta.model_copy(update={"provider_id": "invalid"}), InvalidProvider
        )
    except ProviderRegistrationError:
        print("✅ Inheritance validation passed.")

    # 4. Test Interface Completeness
    try:
        reg.register(
            meta.model_copy(update={"provider_id": "partial"}), PartialProvider
        )
    except ProviderRegistrationError as e:
        print(f"✅ Interface completeness passed (Caught missing: {e.message})")

    # 5. Test Freezing
    reg.freeze()
    try:
        reg.unregister("official:test-provider")
    except RuntimeError:
        print("✅ Registry freezing passed.")


if __name__ == "__main__":
    test_registry_pipeline()
