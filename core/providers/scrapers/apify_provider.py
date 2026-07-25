import asyncio
import logging
from typing import Any, Dict, List, Optional

from core.providers.base import (HealthStatus, ProviderCostEstimate,
                                 ProviderMetrics, RateLimitStatus)
from core.providers.scrapers.actor_catalog import get_actor_metadata
from core.providers.scrapers.apify_client import ApifyClient
from core.providers.scrapers.apify_config import ApifyConfig
from core.providers.scrapers.apify_exceptions import translate_apify_exception
from core.providers.scrapers.apify_mapper import (ApifyRequestMapper,
                                                  ScrapeRequest)
from core.providers.scrapers.base import IScraperProvider
from core.providers.scrapers.dataset_mapper import DatasetMapper
from core.providers.scrapers.scrape_cost_calculator import ScrapeCostCalculator
from core.schemas.job_listing import JobListingCreate

logger = logging.getLogger(__name__)


class ApifyProvider(IScraperProvider):
    """
    Canonical reference implementation for the Apify Scraper Provider.
    """

    def __init__(self, config: Optional[ApifyConfig] = None):
        self._config = config or ApifyConfig.from_settings()
        self._client = ApifyClient(self._config)
        self._provider_id = "official:apify"
        self._initialized = False

    # --- ProviderLifecycle ---

    async def initialize(self) -> None:
        try:
            await self._client.connect()
            self._initialized = True
        except Exception as e:
            raise translate_apify_exception(e, self._provider_id)

    async def shutdown(self) -> None:
        await self._client.disconnect()
        self._initialized = False

    async def ready(self) -> bool:
        return self._initialized and self._config.api_token is not None

    async def health(self) -> HealthStatus:
        if not await self.ready():
            return HealthStatus.UNHEALTHY
        if await self._client.ping():
            return HealthStatus.HEALTHY
        return HealthStatus.DEGRADED

    def metrics(self) -> ProviderMetrics:
        return ProviderMetrics()

    # --- IScraperProvider ---

    async def search(
        self, query: str, location: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Executes a search via Apify Actor."""
        actor_id = self._config.default_actor_id
        request = ScrapeRequest(query=query, location=location, limit=limit)

        try:
            actor_input = ApifyRequestMapper.to_actor_input(actor_id, request)
            run = await self._client.run_actor(actor_id, actor_input)

            # Extract Dataset ID
            dataset_id = run.get("defaultDatasetId") or run.get("default_dataset_id")
            if not dataset_id:
                return []

            # Retrieve Items
            raw_items = await self._client.get_dataset_items(dataset_id)
            return raw_items

        except Exception as e:
            raise translate_apify_exception(e, self._provider_id)

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[JobListingCreate]:
        return DatasetMapper.normalize(raw_data, provider_name=self._provider_id)

    async def cancel(self, task_id: str) -> bool:
        return await self._client.abort_run(task_id)

    def rate_limit_status(self) -> RateLimitStatus:
        return RateLimitStatus()

    def estimate_cost(self, query: str, limit: int) -> ProviderCostEstimate:
        return ScrapeCostCalculator.calculate(self._config.default_actor_id, limit)
