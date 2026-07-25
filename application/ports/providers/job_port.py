from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Optional


@dataclass(frozen=True)
class BackgroundJob:
    id: str
    name: str
    payload: Dict[str, Any]
    scheduled_at: datetime
    status: str  # pending, running, completed, failed


class IBackgroundJobProvider(ABC):
    """
    Interface for background task processing.
    Supports Analytics refresh, report generation, and cache cleanup.
    """

    @abstractmethod
    async def enqueue(self, job_name: str, payload: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def schedule(
        self, job_name: str, payload: Dict[str, Any], run_at: datetime
    ) -> str:
        pass

    @abstractmethod
    async def get_job_status(self, job_id: str) -> str:
        pass

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        pass
