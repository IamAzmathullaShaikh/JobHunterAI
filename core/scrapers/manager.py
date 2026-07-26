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
        # Active engines: only those that reliably return real postings.
        # Indeed / Naukri / Foundit / Google Jobs / Internshala / YC Jobs are
        # kept importable but disabled here because they get blocked or return
        # empty in practice. Add them back to this list to re-enable.
        self.default_scrapers: List[BaseScraper] = [
            LinkedInScraper(),
            GlassdoorScraper(),
            ApifyJobScraper(),  # requires APIFY_API_TOKEN in .env, else returns empty
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
        try:
            # Wrap scraper in a wait_for to ensure it doesn't block forever
            listings = await asyncio.wait_for(
                scraper.scrape(search_query, location, limit, job_type),
                timeout=60.0 # 60s max per scraper
            )
            return scraper.name, listings
        except asyncio.TimeoutError:
            logger.error(f"{scraper.name} timed out after 60s.")
            return scraper.name, []
        except Exception as e:
            logger.error(f"{scraper.name} failed during execution: {str(e)}")
            return scraper.name, []

    async def run_all(
        self,
        search_query: str,
        location: str = "Remote",
        limit_per_site: int = 10,
        job_type: str = "Full-Time",
        scrapers: Optional[List[BaseScraper]] = None,
    ) -> List[JobListingCreate]:
        active_scrapers = scrapers or self.default_scrapers
        logger.info(
            f"Launching {len(active_scrapers)} active scraper engines concurrently..."
        )

        tasks = [
            self._run_scraper(scraper, search_query, location, limit_per_site, job_type)
            for scraper in active_scrapers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_listings: List[JobListingCreate] = []

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Background scraper thread error: {result}")
                continue
            scraper_name, listings = result
            logger.info(
                f"{scraper_name} finished cleanly. Discovered {len(listings)} records."
            )
            all_listings.extend(listings)

        return all_listings
