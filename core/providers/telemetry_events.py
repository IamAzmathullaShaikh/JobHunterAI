import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TelemetryEventType(str, Enum):
    PROVIDER_INITIALIZED = "provider_initialized"
    PROVIDER_SHUTDOWN = "provider_shutdown"
    PROVIDER_RELOADED = "provider_reloaded"
    PROVIDER_INVOCATION_STARTED = "provider_invocation_started"
    PROVIDER_INVOCATION_COMPLETED = "provider_invocation_completed"
    PROVIDER_INVOCATION_FAILED = "provider_invocation_failed"
    CIRCUIT_STATE_CHANGED = "circuit_state_changed"
    PROVIDER_REGISTERED = "provider_registered"
    PROVIDER_UNREGISTERED = "provider_unregistered"
    APP_STARTING = "app_starting"
    APP_READY = "app_ready"
    APP_STOPPING = "app_stopping"


class BaseTelemetryEvent(BaseModel):
    """Base class for all telemetry events."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: TelemetryEventType
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None
    provider_id: str


# --- Lifecycle Events ---


class ProviderInitialized(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.PROVIDER_INITIALIZED
    initialization_time_ms: float


class ProviderShutdown(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.PROVIDER_SHUTDOWN


class ProviderReloaded(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.PROVIDER_RELOADED


# --- Invocation Events ---


class ProviderInvocationStarted(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.PROVIDER_INVOCATION_STARTED
    method: str


class ProviderInvocationCompleted(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.PROVIDER_INVOCATION_COMPLETED
    method: str
    latency_ms: float
    token_usage: Optional[int] = None
    estimated_cost_usd: Optional[float] = None


class ProviderInvocationFailed(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.PROVIDER_INVOCATION_FAILED
    method: str
    error_type: str
    error_message: str
    latency_ms: float


# --- Circuit Events ---


class CircuitStateChanged(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.CIRCUIT_STATE_CHANGED
    old_state: str
    new_state: str


# --- Registry Events ---


class ProviderRegistered(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.PROVIDER_REGISTERED
    provider_type: str


class ProviderUnregistered(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.PROVIDER_UNREGISTERED


# --- Application Lifecycle Events ---


class ApplicationStarting(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.APP_STARTING
    provider_id: str = "system"


class ApplicationReady(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.APP_READY
    provider_id: str = "system"


class ApplicationStopping(BaseTelemetryEvent):
    event_type: TelemetryEventType = TelemetryEventType.APP_STOPPING
    provider_id: str = "system"
