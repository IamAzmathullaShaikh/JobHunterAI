import os
from typing import List, Dict, Any
from datetime import datetime
try:
    from jobspy import scrape_jobs
except ImportError:
    scrape_jobs = None

from core.utils.logger import logger
from core.schemas.job_listing import JobListingCreate

class ScraperEngine:
    """
    9-Platform Multi-Scraper Engine.
    Platforms: LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google Jobs,
    Dice, Monster, SimplyHired, Working Nomads.
    """

    def __init__(self):
        self.supported_platforms = [
            "linkedin", "indeed", "glassdoor", "zip_recruiter",
            "google", "dice", "monster", "simply_hired", "working_nomads"
        ]

    async def search_all(
        self,
        query: str,
        location: str = "Remote",
        limit: int = 20,
        platforms: List[str] = None
    ) -> List[Dict[str, Any]]:
        if not scrape_jobs:
            logger.error("python-jobspy not installed. Cannot perform live search.")
            return []

        search_platforms = platforms if platforms else self.supported_platforms
        logger.info(f"Searching for '{query}' in '{location}' across {len(search_platforms)} platforms...")

        try:
            # JobSpy is a synchronous library, so we run it in a thread if needed,
            # but for now we'll call it directly as it's the primary engine.
            jobs = scrape_jobs(
                site_name=search_platforms,
                search_term=query,
                location=location,
                results_wanted=limit,
                hours_old=72,
                country_allowed='usa', # Defaulting to usa, can be parameterized
            )

            # Convert to list of dicts and standardize
            if jobs.empty:
                return []

            return jobs.to_dict('records')
        except Exception as e:
            logger.error(f"Live job search failed: {e}")
            return []

scraper_engine = ScraperEngine()
