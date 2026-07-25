from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Optional, Union


class ICacheProvider(ABC):
    """
    Interface for multi-layered caching.
    Supports Analytics snapshots, prompt renderings, and context reuse.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> None:
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass
