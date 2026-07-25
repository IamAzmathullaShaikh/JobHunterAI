from abc import ABC, abstractmethod
from typing import Any, Optional


class IUnitOfWork(ABC):
    """
    Interface for transaction management.
    Ensures atomic operations across multiple repositories.
    """

    @abstractmethod
    async def begin(self) -> None:
        """Explicitly starts a transaction."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commits the current transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rolls back the current transaction."""
        pass

    @abstractmethod
    async def flush(self) -> None:
        """Synchronizes in-memory state with the database without committing."""
        pass

    @abstractmethod
    async def dispose(self) -> None:
        """Releases all resources associated with the unit of work."""
        pass

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Async context manager entry."""
        pass

    @abstractmethod
    async def __aexit__(
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Any
    ):
        """Async context manager exit with automatic rollback on exception."""
        pass
