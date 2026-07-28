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
    def __init__(self, actor_config: Optional[dict] = None):
        """
        Generic Apify Actor wrapper.
        :param actor_config: Configuration from the YAML registry.
        """
        self.config = actor_config or {
            "id": "google_jobs",
            "name": "Apify Cloud",
            "actor_id": "toolsnmoreapi/google-jobs",
        }

    @property
    def name(self) -> str:
        return self.config.get("name", "Apify Cloud")

    async def scrape(
        self,
        search_query: str,
        location: Optional[str] = None,
        limit: int = 10,
        job_type: str = "Full-Time",
    ) -> List[JobListingCreate]:
        log = logger.bind(scraper=self.name)
        from core.providers.apify.registry import registry as apify_registry

        token = settings.APIFY_API_TOKEN.strip() if settings.APIFY_API_TOKEN else ""
        if not token:
            log.warning("APIFY_API_TOKEN unconfigured. Skipping.")
            return []

        actor_id = self.config.get("actor_id")
        target_location = location or "Remote"

        client = ApifyClientAsync(token=token)

        # 1. Determine specialized input based on actor ID
        if "google-jobs" in actor_id:
            run_input = {
                "queries": f"{search_query} in {target_location}",
                "maxPagesPerQuery": 1,
                "maxResultsPerQuery": limit
            }
        elif "linkedin-jobs" in actor_id:
            run_input = {
                "queries": f"{search_query} {target_location}",
                "limit": limit
            }
        elif "indeed" in actor_id:
            run_input = {
                "position": search_query,
                "location": target_location,
                "maxItems": limit
            }
        else:
            # Fallback for generic scrapers
            run_input = {"queries": search_query, "limit": limit}

        try:
            log.info(f"Invoking {self.name} ({actor_id})")
            run = await client.actor(actor_id).call(
                run_input=run_input,
                timeout_secs=self.config.get("timeout_seconds", 120)
            )

            # 2. Extract Dataset ID
            dataset_id = run.get("defaultDatasetId") or run.get("default_dataset_id")
            if not dataset_id:
                log.error(f"No dataset ID for {actor_id}")
                return []

            # 3. Retrieve and Map Items
            dataset_items = await client.dataset(dataset_id).list_items()
            raw_items = []
            if hasattr(dataset_items, "items"): raw_items = dataset_items.items
            elif isinstance(dataset_items, list): raw_items = dataset_items

            jobs = []
            for item in raw_items[:limit]:
                try:
                    # Multi-schema mapping
                    title = item.get("title") or item.get("positionName") or "Role"
                    company = item.get("companyName") or item.get("company") or "Company"
                    loc = item.get("location") or item.get("city", target_location)
                    job_url = item.get("url") or item.get("link") or item.get("jobUrl", "#")
                    raw_id = str(item.get("id") or item.get("jobId") or f"{self.config['id']}-{random.randint(1000, 9999)}")
                    desc = item.get("description") or item.get("descriptionText", "View listing for details.")

                    jobs.append(
                        JobListingCreate(
                            job_id_raw=raw_id,
                            title=title.strip(),
                            company_name=company.strip(),
                            location=str(loc),
                            work_place_type="Onsite",
                            job_type=job_type,
                            source=f"apify:{self.config['id']}",
                            url=job_url,
                            description_raw=str(desc),
                            description_clean=str(desc)[:300],
                        )
                    )
                except:
                    continue

            apify_registry.mark_actor_healthy(self.config["id"])
            log.info(f"{self.name} finished. Found {len(jobs)}")
            return jobs

        except Exception as e:
            log.error(f"{self.name} failed: {e}")
            apify_registry.mark_actor_unhealthy(self.config["id"], str(e))
            return []
