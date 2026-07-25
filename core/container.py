import logging
from threading import Lock
from typing import Optional

from core.config.settings import Settings
from core.config.settings import settings as app_settings
from core.providers.circuit_breaker import CircuitBreaker
from core.providers.circuit_breaker import breaker as app_circuit_breaker
from core.providers.manager import ProviderManager
from core.providers.manager import manager as app_provider_manager
from core.providers.registry import ProviderRegistry
from core.providers.registry import registry as app_registry
from core.providers.telemetry import TelemetryEngine
from core.providers.telemetry import engine as app_telemetry_engine
from core.providers.telemetry_dispatcher import TelemetryDispatcher
from core.providers.telemetry_dispatcher import dispatcher as app_dispatcher

logger = logging.getLogger(__name__)


class DIContainer:
    """
    Composition Root for the JobHunterAI platform.
    Manages the lifecycle and resolution of infrastructure singletons.
    """

    _instance: Optional["DIContainer"] = None
    _lock: Lock = Lock()

    def __init__(self):
        # We wrap existing singletons to maintain a central point of access
        # while allowing future transition to full factory-based DI.
        self.settings: Settings = app_settings
        self.registry: ProviderRegistry = app_registry
        self.telemetry_dispatcher: TelemetryDispatcher = app_dispatcher
        self.telemetry_engine: TelemetryEngine = app_telemetry_engine
        self.circuit_breaker: CircuitBreaker = app_circuit_breaker
        self.provider_manager: ProviderManager = app_provider_manager

        logger.debug("DIContainer initialized with core infrastructure.")

    @classmethod
    def get_instance(cls) -> "DIContainer":
        """Thread-safe singleton access to the container."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance


# Global access point
container = DIContainer.get_instance()
