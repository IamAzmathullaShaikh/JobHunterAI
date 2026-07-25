import logging
from datetime import timedelta
from typing import Any, Awaitable, Callable, Optional, TypeVar

from application.ports.providers.cache_port import ICacheProvider

T = TypeVar("T")
logger = logging.getLogger(__name__)


class CacheCoordinator:
    """
    Orchestrates caching across use cases to minimize redundant
    computations and cloud provider calls.
    """

    def __init__(self, cache: ICacheProvider):
        self._cache = cache

    async def get_or_compute(
        self,
        key: str,
        computer: Callable[[], Awaitable[T]],
        ttl: Optional[timedelta] = None,
    ) -> T:
        """Standard cache-aside pattern."""
        cached = await self._cache.get(key)
        if cached is not None:
            logger.debug(f"Cache HIT for key: {key}")
            return cached

        logger.debug(f"Cache MISS for key: {key}. Computing...")
        result = await computer()
        await self._cache.set(key, result, ttl)
        return result

    async def invalidate_context(self, candidate_id: str):
        """Clears all cached items for a specific candidate."""
        await self._cache.clear(pattern=f"candidate:{candidate_id}:*")
