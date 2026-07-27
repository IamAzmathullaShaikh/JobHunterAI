import logging
import random
from typing import List, Optional
from urllib.parse import quote

from apify_client import ApifyClientAsync

logger = logging.getLogger(__name__)

from core.config.settings import settings
from core.schemas.job_listing import JobListingCreate
from core.scrapers.base import BaseScraper


class ApifyJobScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Apify Cloud"

    async def scrape(
        self,
        search_query: str,
        location: Optional[str] = None,
        limit: int = 10,
        job_type: str = "Full-Time",
    ) -> List[JobListingCreate]:
        log = logger.bind(scraper=self.name)

        token = settings.APIFY_API_TOKEN.strip() if settings.APIFY_API_TOKEN else ""
        if not token:
            log.warning(
                "APIFY_API_TOKEN is unconfigured in .env file. Skipping cloud actor execution."
            )
            return []

        target_location = location or "India"
        log.info(
            f"Dispatching Apify Cloud Actor for Query: '{search_query}' in '{target_location}'"
        )

        client = ApifyClientAsync(token=token)

        # Use the actor configured in settings for maximum flexibility
        actor_id = settings.APIFY_ACTOR_ID or "apify/google-jobs-scraper"

        # Determine input based on actor type
        if "google-jobs" in actor_id:
            run_input = {
                "queries": search_query,
                "maxPagesPerQuery": 1,
                "maxResultsPerQuery": limit
            }
        else:
            # Fallback for generic scrapers
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={quote(search_query)}&location={quote(target_location)}"
            run_input = {"urls": [search_url], "count": max(limit, 10)}

        try:
            log.info(f"Invoking Apify Actor: {actor_id}")
            run = await client.actor(actor_id).call(run_input=run_input)

            # Safely extract default_dataset_id from SDK ActorRun object or dict
            dataset_id = None
            if run:
                if isinstance(run, dict):
                    dataset_id = run.get("default_dataset_id") or run.get(
                        "defaultDatasetId"
                    )
                else:
                    dataset_id = getattr(run, "default_dataset_id", None) or getattr(
                        run, "defaultDatasetId", None
                    )

            if not dataset_id:
                log.error("Apify run finished without returning a valid dataset ID.")
                return []

            dataset_items = await client.dataset(dataset_id).list_items()

            # Unpack items list from ListPage object or raw dictionary
            if hasattr(dataset_items, "items"):
                raw_items = dataset_items.items
            elif isinstance(dataset_items, dict):
                raw_items = dataset_items.get("items", [])
            elif isinstance(dataset_items, list):
                raw_items = dataset_items
            else:
                raw_items = []

            log.info(
                f"Apify cloud actor returned {len(raw_items)} records from dataset."
            )

            for item in raw_items[:limit]:
                try:
                    title = item.get("title") or item.get(
                        "position", "Role Opportunity"
                    )
                    company = item.get("companyName") or item.get(
                        "company", "Listed Partner"
                    )
                    loc = item.get("location") or target_location
                    job_url = (
                        item.get("link")
                        or item.get("url")
                        or item.get("jobUrl")
                        or search_url
                    )
                    raw_id = str(
                        item.get("id")
                        or item.get("jobId")
                        or f"apify-{random.randint(100000, 999999)}"
                    )
                    desc = (
                        item.get("descriptionText")
                        or item.get("description")
                        or f"{title} role at {company} in {loc}."
                    )

                    jobs.append(
                        JobListingCreate(
                            job_id_raw=raw_id,
                            title=title,
                            company_name=company,
                            location=loc,
                            work_place_type="Onsite",
                            job_type=job_type,
                            source=self.name,
                            url=job_url,
                            description_raw=str(desc),
                            description_clean=str(desc)[:300],
                        )
                    )
                except Exception as item_err:
                    log.warning(
                        f"Skipping malformed item from Apify dataset: {item_err}"
                    )

        except Exception as e:
            log.error(f"Apify cloud execution failed: {str(e)}")

        return jobs
