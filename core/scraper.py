import logging
import os
from typing import Any, Dict, List

from core.ai.smart_router import route
from core.config.settings import settings

logger = logging.getLogger("jobhunterai.scraper")


# --- Cloud Primary ---
async def apify_scrape(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Uses Apify Actors for high-quality scraping."""
    from apify_client import ApifyClient

    token = settings.APIFY_API_TOKEN
    client = ApifyClient(token)

    # Use a reliable public actor for job scraping
    actor_id = settings.APIFY_ACTOR_ID

    try:
        run_input = {
            "queries": payload.get("query", "Software Engineer"),
            "maxPagesPerQuery": 1,
        }

        logger.info(f"Calling Apify Actor: {actor_id}")
        run = client.actor(actor_id).call(run_input=run_input)
        results = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not results:
            logger.warning(f"Apify Actor {actor_id} returned no results.")
            return None  # Trigger fallback

        return {"source": "apify", "data": results}
    except Exception as e:
        logger.error(f"Apify Actor {actor_id} call failed: {str(e)}")
        # Re-raise to trigger the smart_router fallback to local JobSpy
        raise e


apify_scrape.required_envs = ["APIFY_API_TOKEN"]


def get_sample_jobs() -> List[Dict[str, Any]]:
    """Returns realistic mock jobs when scraping is blocked."""
    return [
        {
            "title": "Backend Engineer (Sample)",
            "company_name": "JobHunterAI Demo",
            "location": "Remote",
            "source": "sample_fallback",
            "url": "https://example.com/demo-job-1",
            "description_raw": "This is a sample job returned because the scraping service is currently being rate-limited.",
        },
        {
            "title": "Full Stack Developer (Sample)",
            "company_name": "Cloud Systems",
            "location": "New York, NY",
            "source": "sample_fallback",
            "url": "https://example.com/demo-job-2",
            "description_raw": "Experience the JobHunterAI interface with this mock data. Try again in a few minutes.",
        },
    ]


# --- Local Fallback ---
async def local_scrape(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Uses python-jobspy for local scraping with anti-bot resilience and backoff."""
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            import asyncio
            import random

            from jobspy import scrape_jobs

            # Jittered delay for retries
            if attempt > 0:
                delay = 5 * attempt + random.uniform(1, 3)
                logger.info(
                    f"Retrying local scrape in {delay:.2f}s (Attempt {attempt+1}/{max_retries+1})"
                )
                await asyncio.sleep(delay)

            # Reduced sites to minimize 403 blocks
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed"],
                search_term=payload.get("query", "Software Engineer"),
                location=payload.get("location", "Remote"),
                results_wanted=payload.get("limit", 10),
            )

            if jobs is None or jobs.empty:
                if attempt == max_retries:
                    logger.warning(
                        "JobSpy returned empty results after retries. Serving sample fallback."
                    )
                    return {"source": "sample_fallback", "data": get_sample_jobs()}
                continue

            return {"source": "jobspy", "data": jobs.to_dict("records")}
        except Exception as e:
            err_str = str(e)
            if "403" in err_str or "blocked" in err_str.lower():
                logger.warning(f"Local jobspy blocked (403) on attempt {attempt+1}")
                if attempt < max_retries:
                    continue

            logger.warning(
                f"Local jobspy scrape failed: {e}. Falling back to sample data."
            )
            return {"source": "sample_fallback", "data": get_sample_jobs()}

    return {"source": "sample_fallback", "data": get_sample_jobs()}


local_scrape.safe_placeholder = {"source": "error", "data": []}


# --- Public API ---
async def scrape_jobs(payload: Dict[str, Any]) -> Dict[str, Any]:
    res = await route(apify_scrape, local_scrape, payload)

    # Simple Normalization
    normalized = []
    raw_data = res.get("data", [])
    for job in raw_data:
        normalized.append(
            {
                "title": job.get("title") or job.get("job_title") or "Unknown Title",
                "company_name": job.get("company_name")
                or job.get("company")
                or "Unknown Company",
                "location": job.get("location") or "Remote",
                "url": job.get("url") or job.get("job_url") or "#",
                "source": res.get("source", "unknown"),
                "description_raw": job.get("description")
                or job.get("description_raw")
                or "",
            }
        )

    return {"source": res.get("source"), "data": normalized}
