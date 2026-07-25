from typing import Optional

from core.providers.base import ProviderCostEstimate
from core.providers.scrapers.actor_catalog import get_actor_metadata


class ScrapeCostCalculator:
    """
    Utility for projecting USD costs for scraping operations based on actor metadata.
    """

    @staticmethod
    def calculate(actor_id: str, item_count: int) -> ProviderCostEstimate:
        """
        Estimates the cost of a scrape based on the number of successfully harvested items.
        """
        meta = get_actor_metadata(actor_id)

        # Estimate: cost per 1k items
        rate = meta.estimated_usd_per_1k / 1000.0
        projected_cost = item_count * rate

        return ProviderCostEstimate(
            estimated_usd=round(projected_cost, 4), is_cached=False
        )
