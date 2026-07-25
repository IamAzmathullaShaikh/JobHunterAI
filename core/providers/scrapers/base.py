from abc import abstractmethod
from typing import Any, Dict, List, Optional

from core.providers.base import (ProviderCostEstimate, ProviderLifecycle,
                                 RateLimitStatus)
from core.schemas.job_listing import JobListingCreate


class IScraperProvider(ProviderLifecycle):
    """
    Abstract contract for Job Scraper service providers.
    Every implementation (Apify, JobSpy) must satisfy this interface.
    """

    @abstractmethod
    async def search(
        self, query: str, location: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Executes a job search across supported boards.
        Returns raw provider-specific data.
        """
        pass

    @abstractmethod
    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[JobListingCreate]:
        """
        Maps raw provider results into the standardized JobHunterAI schema.
        Ensures consistency across all scraper engines.
        """
        pass

    @abstractmethod
    async def cancel(self, task_id: str) -> bool:
        """
        Attempts to terminate a running scrape task (relevant for Cloud Actors).
        """
        pass

    @abstractmethod
    def rate_limit_status(self) -> RateLimitStatus:
        """
        Returns the current throttle/quota state for this scraper.
        """
        pass

    @abstractmethod
    def estimate_cost(self, query: str, limit: int) -> ProviderCostEstimate:
        """
        Predicts the USD cost for the scraping operation.
        """
        pass
