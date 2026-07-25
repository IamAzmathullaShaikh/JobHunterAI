from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Represents the operational state of a provider."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"


class ProviderMetrics(BaseModel):
    """Tracks operational performance metrics for a provider."""

    latency_ms: float = 0.0
    request_count: int = 0
    failure_count: int = 0
    last_failure_at: Optional[datetime] = None
    average_latency_ms: float = 0.0


class ProviderMetadata(BaseModel):
    """Static metadata about a specific provider."""

    provider_id: str
    namespace: str = "official"
    name: str
    version: str
    interface_version: int = 1
    sdk_version: Optional[str] = None
    api_version: Optional[str] = None
    provider_type: str  # e.g., "ai", "scraper"
    priority: int = 100
    enabled: bool = True
    capabilities: List[str] = Field(default_factory=list)
    region: Optional[str] = "global"

    @property
    def full_id(self) -> str:
        return f"{self.namespace}:{self.provider_id}"


class ProviderCostEstimate(BaseModel):
    """Projected cost for a specific operation."""

    estimated_usd: float
    token_count: Optional[int] = None
    is_cached: bool = False


class RateLimitStatus(BaseModel):
    """Information about current provider quotas and throttling."""

    remaining: Optional[int] = None
    limit: Optional[int] = None
    reset_at: Optional[datetime] = None
    is_throttled: bool = False


class ProviderLifecycle(ABC):
    """
    Mandatory lifecycle hooks that every cloud service provider must implement.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Sets up internal clients, connection pools, and credentials."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully closes all connections and cleans up resources."""
        pass

    @abstractmethod
    async def ready(self) -> bool:
        """Quick check to see if the provider is initialized and authenticated."""
        pass

    @abstractmethod
    async def health(self) -> HealthStatus:
        """Performs a detailed health check (e.g., ping or quota check)."""
        pass

    @abstractmethod
    def metrics(self) -> ProviderMetrics:
        """Returns the current operational metrics for this provider."""
        pass
