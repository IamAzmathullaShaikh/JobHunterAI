import inspect
import logging
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional, Set, Type

from core.exceptions import ProviderRegistrationError
from core.providers.base import ProviderLifecycle, ProviderMetadata

logger = logging.getLogger(__name__)


class RegistryEvent(str, Enum):
    PROVIDER_REGISTERED = "provider_registered"
    PROVIDER_REMOVED = "provider_removed"
    REGISTRY_FROZEN = "registry_frozen"
    VALIDATION_FAILED = "validation_failed"


class ProviderRegistry:
    """
    Central authority for provider discovery, registration, and validation.
    Designed for production stability with a 6-stage validation pipeline and
    runtime immutability in production mode.
    """

    def __init__(self):
        self._storage: Dict[str, tuple[ProviderMetadata, Type[ProviderLifecycle]]] = {}
        self._capability_index: Dict[str, Set[str]] = {}
        self._is_frozen: bool = False
        self._lock = Lock()

    def register(
        self, metadata: ProviderMetadata, provider_cls: Type[ProviderLifecycle]
    ) -> None:
        """
        Registers a provider class with its metadata through a strict validation pipeline.

        Args:
            metadata: Immutable provider configuration.
            provider_cls: The class implementing ProviderLifecycle.

        Raises:
            ProviderRegistrationError: If any validation stage fails.
            RuntimeError: If the registry is frozen.
        """
        with self._lock:
            if self._is_frozen:
                raise RuntimeError(
                    "Cannot register providers: Registry is frozen for production."
                )

            # Pipeline Stage 1: Validate Class
            self._validate_class(metadata.full_id, provider_cls)

            # Pipeline Stage 2: Validate Interface
            self._validate_interface(metadata.full_id, provider_cls)

            # Pipeline Stage 3: Duplicate Detection
            self._check_duplicates(metadata)

            # Pipeline Stage 4: Validate Metadata & Capabilities
            self._validate_metadata_content(metadata)

            # Stage 5: Commit to Storage
            self._storage[metadata.full_id] = (metadata, provider_cls)

            # Stage 6: Index Capabilities
            for cap in metadata.capabilities:
                if cap not in self._capability_index:
                    self._capability_index[cap] = set()
                self._capability_index[cap].add(metadata.full_id)

            logger.info(
                f"Successfully registered provider: {metadata.full_id} (Type: {metadata.provider_type})"
            )

    def unregister(self, full_id: str) -> None:
        """Removes a provider from the registry."""
        with self._lock:
            if self._is_frozen:
                raise RuntimeError("Cannot unregister providers: Registry is frozen.")

            if full_id in self._storage:
                metadata, _ = self._storage.pop(full_id)
                for cap in metadata.capabilities:
                    if cap in self._capability_index:
                        self._capability_index[cap].discard(full_id)
                logger.info(f"Unregistered provider: {full_id}")

    def freeze(self) -> None:
        """Locks the registry to prevent further modifications (Production mode)."""
        with self._lock:
            self._is_frozen = True
            logger.info("Provider Registry has been FROZEN.")

    def get(self, full_id: str) -> tuple[ProviderMetadata, Type[ProviderLifecycle]]:
        """Retrieves a provider tuple by its full namespace:id."""
        if full_id not in self._storage:
            raise KeyError(f"Provider '{full_id}' not found in registry.")
        return self._storage[full_id]

    def get_by_type(self, provider_type: str) -> List[ProviderMetadata]:
        """Returns metadata for all providers of a specific type."""
        return [
            meta
            for meta, _ in self._storage.values()
            if meta.provider_type == provider_type
        ]

    def get_by_capability(self, capability: str) -> List[ProviderMetadata]:
        """High-speed lookup for providers supporting a specific feature."""
        provider_ids = self._capability_index.get(capability, set())
        return [self._storage[pid][0] for pid in provider_ids]

    def list_all(self) -> List[ProviderMetadata]:
        """Returns all registered provider metadata."""
        return [meta for meta, _ in self._storage.values()]

    def exists(self, full_id: str) -> bool:
        """Checks if a provider is registered."""
        return full_id in self._storage

    # --- Validation Pipeline Stages ---

    def _validate_class(self, pid: str, cls: Type) -> None:
        if not inspect.isclass(cls):
            raise ProviderRegistrationError(
                "Provider must be a class, not an instance.", pid
            )
        if not issubclass(cls, ProviderLifecycle):
            raise ProviderRegistrationError(
                "Class must inherit from ProviderLifecycle.", pid
            )

    def _validate_interface(self, pid: str, cls: Type[ProviderLifecycle]) -> None:
        abstract_methods = getattr(cls, "__abstractmethods__", set())
        if abstract_methods:
            missing = ", ".join(abstract_methods)
            raise ProviderRegistrationError(
                f"Class is missing implementations for: {missing}", pid
            )

    def _check_duplicates(self, metadata: ProviderMetadata) -> None:
        if metadata.full_id in self._storage:
            raise ProviderRegistrationError(
                f"Duplicate full_id detected: {metadata.full_id}", metadata.full_id
            )

    def _validate_metadata_content(self, metadata: ProviderMetadata) -> None:
        if not metadata.provider_id or not metadata.namespace:
            raise ProviderRegistrationError(
                "Metadata missing core identifiers.", metadata.full_id
            )
        if not metadata.capabilities:
            logger.warning(
                f"Provider {metadata.full_id} registered with zero capabilities."
            )


# Shared instance
registry = ProviderRegistry()
