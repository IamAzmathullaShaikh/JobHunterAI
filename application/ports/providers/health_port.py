from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ComponentStatus:
    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float
    details: Dict[str, Any]


class IHealthProvider(ABC):
    """
    Interface for checking the health of system components and providers.
    """

    @abstractmethod
    async def check_all(self) -> List[ComponentStatus]:
        pass

    @abstractmethod
    async def check_component(self, component_id: str) -> ComponentStatus:
        pass
