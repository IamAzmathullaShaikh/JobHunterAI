import asyncio
from typing import List, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from scrapers.base import BaseScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.indeed import IndeedScraper
from scrapers.naukri import NaukriScraper
from scrapers.foundit import FounditScraper
from scrapers.glassdoor import GlassdoorScraper
from scrapers.google_jobs import GoogleJobsScraper
from schemas.job_listing import JobListingCreate
from scrapers.apify_scraper import ApifyJobScraper
from scrapers.internshala import InternshalaScraper
from scrapers.yc_jobs import YCJobsScraper

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
        job_type: str
    ) -> tuple[str, List[JobListingCreate]]:
        logger.info(f"Running scraper: {scraper.name}")
        try:
            listings = await scraper.scrape(search_query, location, limit, job_type)
            return scraper.name, listings
        except Exception as e:
            logger.error(f"{scraper.name} failed during execution: {str(e)}")
            return scraper.name, []

    async def run_all(
        self, 
        search_query: str, 
        location: str = "Remote", 
        limit_per_site: int = 10, 
        job_type: str = "Full-Time",
        scrapers: Optional[List[BaseScraper]] = None
    ) -> List[JobListingCreate]:
        active_scrapers = scrapers or self.default_scrapers
        logger.info(f"Launching {len(active_scrapers)} active scraper engines concurrently...")
        
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
            logger.success(f"{scraper_name} finished cleanly. Discovered {len(listings)} records.")
            all_listings.extend(listings)
            
        return all_listings