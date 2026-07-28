import asyncio
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas.job_listing import JobListingCreate
from core.scrapers.apify_scraper import ApifyJobScraper
from core.scrapers.base import BaseScraper
from core.scrapers.foundit import FounditScraper
from core.scrapers.glassdoor import GlassdoorScraper
from core.scrapers.google_jobs import GoogleJobsScraper
from core.scrapers.indeed import IndeedScraper
from core.scrapers.internshala import InternshalaScraper
from core.scrapers.linkedin import LinkedInScraper
from core.scrapers.naukri import NaukriScraper
from core.scrapers.yc_jobs import YCJobsScraper


class ScraperManager:
    def __init__(self, session: AsyncSession = None):
        self.session = session
        # Standard local/stealth scrapers
        self.stealth_scrapers: List[BaseScraper] = [
            LinkedInScraper(),
            GlassdoorScraper(),
        ]

    async def _run_scraper(
        self,
        scraper: BaseScraper,
        search_query: str,
        location: str,
        limit: int,
        job_type: str,
    ) -> tuple[str, List[JobListingCreate]]:
        logger.info(f"Running scraper: {scraper.name}")
        max_retries = 1 # Fleet mode has lower retries to keep it fast
        for attempt in range(max_retries + 1):
            try:
                listings = await asyncio.wait_for(
                    scraper.scrape(search_query, location, limit, job_type),
                    timeout=120.0
                )
                return scraper.name, listings
            except Exception as e:
                logger.error(f"{scraper.name} attempt {attempt+1} failed: {e}")
                continue

        return scraper.name, []

    async def run_all(
        self,
        search_query: str,
        location: str = "Remote",
        limit_per_site: int = 10,
        job_type: str = "Full-Time",
        scrapers: Optional[List[BaseScraper]] = None,
    ) -> List[JobListingCreate]:

        # 1. Resolve Fleet via Apify Registry
        from core.providers.apify.selector import selector as apify_selector

        # Select best 3 Apify actors for this query
        apify_actors = apify_selector.select_actors_parallel(search_query, count=3)
        apify_fleet = [ApifyJobScraper(actor) for actor in apify_actors]

        # 2. Combine with Stealth Local Scrapers
        full_fleet = apify_fleet + self.stealth_scrapers
        if scrapers: full_fleet = scrapers # Override if provided

        logger.info(f"Launching Scraper Fleet v2.0 ({len(full_fleet)} engines)...")

        tasks = [
            self._run_scraper(scraper, search_query, location, limit_per_site, job_type)
            for scraper in full_fleet
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_listings: List[JobListingCreate] = []

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Fleet engine critical failure: {result}")
                continue
            scraper_name, listings = result
            if listings:
                logger.info(f"[{scraper_name}] Discovered {len(listings)} records.")
                all_listings.extend(listings)

        return all_listings
