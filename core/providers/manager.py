import asyncio
import logging
import time
from threading import RLock
from typing import Any, Dict, List, Optional, Type, TypeVar

from core.exceptions import (DuplicateInstanceError,
                             ProviderInitializationError,
                             ProviderNotFoundError, ProviderNotReadyError)
from core.providers.base import ProviderLifecycle, ProviderMetadata
from core.providers.breaker_exceptions import CallRejectedError
from core.providers.circuit_breaker import breaker as default_breaker
from core.providers.registry import ProviderRegistry
from core.providers.registry import registry as default_registry
from core.providers.telemetry_dispatcher import dispatcher as telemetry
from core.providers.telemetry_events import (ProviderInitialized,
                                             ProviderInvocationCompleted,
                                             ProviderInvocationFailed,
                                             ProviderInvocationStarted,
                                             ProviderReloaded,
                                             ProviderShutdown)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=ProviderLifecycle)


class CircuitBreakerProxy(ProviderLifecycle):
    """
    Intercepts calls to a provider instance to enforce circuit breaker state.
    """

    def __init__(self, instance: T, provider_id: str, breaker: Any):
        self._instance = instance
        self._provider_id = provider_id
        self._breaker = breaker

    async def initialize(self):
        return await self._instance.initialize()

    async def shutdown(self):
        return await self._instance.shutdown()

    async def ready(self):
        return await self._instance.ready()

    async def health(self):
        return await self._instance.health()

    def metrics(self):
        return self._instance.metrics()

    def __getattr__(self, name):
        attr = getattr(self._instance, name)
        if callable(attr) and not name.startswith("_"):
            # Wrap public methods with circuit breaker logic
            if asyncio.iscoroutinefunction(attr):
                return self._wrap_async(attr)
            return self._wrap_sync(attr)
        return attr

    def _wrap_async(self, func):
        async def wrapper(*args, **kwargs):
            if not self._breaker.allow_request(self._provider_id):
                raise CallRejectedError(
                    self._provider_id, self._breaker.get_state(self._provider_id)
                )

            start_time = time.perf_counter()
            telemetry.publish(
                ProviderInvocationStarted(
                    provider_id=self._provider_id, method=func.__name__
                )
            )

            try:
                result = await func(*args, **kwargs)
                latency = (time.perf_counter() - start_time) * 1000
                self._breaker.record_success(self._provider_id)

                # Try to extract token usage if available in result
                tokens = None
                if isinstance(result, dict) and "meta" in result:
                    tokens = result["meta"].get("tokens") or result["meta"].get(
                        "token_usage"
                    )

                telemetry.publish(
                    ProviderInvocationCompleted(
                        provider_id=self._provider_id,
                        method=func.__name__,
                        latency_ms=latency,
                        token_usage=tokens,
                    )
                )
                return result
            except Exception as e:
                latency = (time.perf_counter() - start_time) * 1000
                self._breaker.record_failure(self._provider_id, e)

                telemetry.publish(
                    ProviderInvocationFailed(
                        provider_id=self._provider_id,
                        method=func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        latency_ms=latency,
                    )
                )
                raise e

        return wrapper

    def _wrap_sync(self, func):
        def wrapper(*args, **kwargs):
            if not self._breaker.allow_request(self._provider_id):
                raise CallRejectedError(
                    self._provider_id, self._breaker.get_state(self._provider_id)
                )

            start_time = time.perf_counter()
            telemetry.publish(
                ProviderInvocationStarted(
                    provider_id=self._provider_id, method=func.__name__
                )
            )

            try:
                result = func(*args, **kwargs)
                latency = (time.perf_counter() - start_time) * 1000
                self._breaker.record_success(self._provider_id)

                telemetry.publish(
                    ProviderInvocationCompleted(
                        provider_id=self._provider_id,
                        method=func.__name__,
                        latency_ms=latency,
                    )
                )
                return result
            except Exception as e:
                latency = (time.perf_counter() - start_time) * 1000
                self._breaker.record_failure(self._provider_id, e)

                telemetry.publish(
                    ProviderInvocationFailed(
                        provider_id=self._provider_id,
                        method=func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        latency_ms=latency,
                    )
                )
                raise e

        return wrapper


class ProviderManager:
    """
    Runtime orchestrator responsible for instantiating, caching, and managing
    the lifecycle of cloud service providers.

    This is the ONLY component allowed to create provider instances.
    """

    def __init__(
        self,
        registry: ProviderRegistry = default_registry,
        breaker: Any = default_breaker,
    ):
        self._registry = registry
        self._breaker = breaker
        self._instances: Dict[str, ProviderLifecycle] = {}
        self._lock = RLock()  # Reentrant lock for safe multi-step initialization

    async def get_provider(
        self, full_id: str, expected_type: Type[T] = ProviderLifecycle
    ) -> T:
        """
        Retrieves a provider instance, lazily initializing it if necessary.

        Args:
            full_id: The 'namespace:provider_id' string from the registry.
            expected_type: Type hint for the returned instance.

        Returns:
            The instantiated and initialized provider.

        Raises:
            ProviderNotFoundError: If the ID is not in the registry.
            ProviderInitializationError: If initialize() fails.
            ProviderNotReadyError: If ready() returns False after initialization.
        """
        if not self._registry.exists(full_id):
            raise ProviderNotFoundError(full_id)

        # 1. Check cache first
        with self._lock:
            if full_id in self._instances:
                instance = self._instances[full_id]
                if not isinstance(instance, expected_type):
                    raise TypeError(
                        f"Provider {full_id} is not of expected type {expected_type}"
                    )
                return instance

        # 2. Double-checked locking pattern for initialization
        with self._lock:
            if full_id in self._instances:
                return self._instances[full_id]

            metadata, provider_cls = self._registry.get(full_id)
            logger.info(f"Lazily instantiating provider: {full_id}")

            try:
                # Factory: Create the instance
                instance = provider_cls()

                # Apply extension points (Circuit Breaker, Telemetry, etc. - M5.4+)
                instance = self._apply_middleware(instance, metadata)

                # Cache immediately to prevent duplicate triggers during async init
                self._instances[full_id] = instance
            except Exception as e:
                logger.error(f"Critical failure during instantiation of {full_id}: {e}")
                raise ProviderInitializationError(str(e), full_id)

        # 3. Asynchronous Initialization (outside the sync lock)
        try:
            start_init = time.perf_counter()
            logger.debug(f"Calling initialize() for {full_id}...")
            await instance.initialize()

            init_time = (time.perf_counter() - start_init) * 1000

            if not await instance.ready():
                raise ProviderNotReadyError(full_id)

            telemetry.publish(
                ProviderInitialized(
                    provider_id=full_id, initialization_time_ms=init_time
                )
            )
            logger.info(f"Provider {full_id} is now ACTIVE.")
            return instance

        except Exception as e:
            # Cleanup on failure
            with self._lock:
                self._instances.pop(full_id, None)
            logger.error(f"Async initialization failed for {full_id}: {e}")
            if isinstance(e, ProviderNotReadyError):
                raise e
            raise ProviderInitializationError(str(e), full_id)

    async def get_default_provider(
        self, provider_type: str, capability: Optional[str] = None
    ) -> ProviderLifecycle:
        """
        Selects and returns the optimal provider based on metadata criteria.

        Selection Priority:
        1. Type match
        2. Capability match (if requested)
        3. Enabled status
        4. Highest priority value (lowest number)
        """
        candidates = self._registry.get_by_type(provider_type)

        if capability:
            cap_candidates = self._registry.get_by_capability(capability)
            candidates = [c for c in candidates if c in cap_candidates]

        # Filter enabled only
        active_candidates = [c for c in candidates if c.enabled]

        if not active_candidates:
            raise ProviderNotFoundError(
                f"No enabled providers found for type '{provider_type}'"
            )

        # Sort by priority (lower number = higher priority)
        active_candidates.sort(key=lambda x: x.priority)

        target = active_candidates[0]
        return await self.get_provider(target.full_id)

    async def reload_provider(self, full_id: str) -> ProviderLifecycle:
        """Invalidates cache and re-initializes a provider."""
        logger.warning(f"Forcing reload of provider: {full_id}")
        with self._lock:
            old_instance = self._instances.pop(full_id, None)
            if old_instance:
                try:
                    await old_instance.shutdown()
                except Exception as e:
                    logger.debug(f"Error during reload-shutdown for {full_id}: {e}")

        telemetry.publish(ProviderReloaded(provider_id=full_id))
        return await self.get_provider(full_id)

    async def shutdown(self) -> None:
        """Gracefully shuts down all instantiated providers."""
        logger.info(
            f"Shutting down Provider Manager. Closing {len(self._instances)} instances..."
        )

        # Snapshot instances to avoid mutation during iteration
        with self._lock:
            targets = list(self._instances.items())
            self._instances.clear()

        for pid, instance in targets:
            try:
                logger.debug(f"Shutting down {pid}...")
                await instance.shutdown()
                telemetry.publish(ProviderShutdown(provider_id=pid))
            except Exception as e:
                logger.error(f"Error during shutdown of {pid}: {e}")

    def _apply_middleware(
        self, instance: ProviderLifecycle, metadata: ProviderMetadata
    ) -> ProviderLifecycle:
        """
        Wraps the instance in proxy layers for Circuit Breaking and Telemetry.
        """
        # 1. Apply Circuit Breaker (M5.4)
        protected_instance = CircuitBreakerProxy(
            instance, metadata.full_id, self._breaker
        )

        # Extension point for M5.5 (Telemetry)
        # protected_instance = TelemetryProxy(protected_instance, ...)

        return protected_instance

    def list_active_ids(self) -> List[str]:
        """Returns IDs of currently instantiated providers."""
        with self._lock:
            return list(self._instances.keys())


# Shared instance
manager = ProviderManager()
