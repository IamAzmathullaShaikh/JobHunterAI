import os
import logging
from typing import Dict, Any, List
from core.ai.smart_router import route

logger = logging.getLogger("jobhunterai.scraper")

# --- Cloud Primary ---
async def apify_scrape(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Uses Apify Actors for high-quality scraping."""
    from apify_client import ApifyClient

    token = os.getenv("APIFY_API_TOKEN")
    client = ApifyClient(token)

    # Use a reliable public actor for LinkedIn job scraping
    actor_id = os.getenv("APIFY_ACTOR_ID", "epctex/linkedin-jobs-scraper")

    try:
        run_input = {
            "queries": payload.get("query", "Software Engineer"),
            "limit": payload.get("limit", 10),
        }

        logger.info(f"Calling Apify Actor: {actor_id}")
        # Removed timeout_secs as it is deprecated/unsupported in recent apify-client versions for .call()
        run = client.actor(actor_id).call(run_input=run_input)
        results = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not results:
            logger.warning(f"Apify Actor {actor_id} returned no results.")
            return None # Trigger fallback

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
            "description_raw": "This is a sample job returned because the scraping service is currently being rate-limited."
        },
        {
            "title": "Full Stack Developer (Sample)",
            "company_name": "Cloud Systems",
            "location": "New York, NY",
            "source": "sample_fallback",
            "url": "https://example.com/demo-job-2",
            "description_raw": "Experience the JobHunterAI interface with this mock data. Try again in a few minutes."
        }
    ]

# --- Local Fallback ---
async def local_scrape(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Uses python-jobspy for local scraping with anti-bot resilience."""
    try:
        from jobspy import scrape_jobs

        # In a real async app we'd use run_in_executor for sync libs like JobSpy
        # but for simplicity in this tiering, we call it directly.
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=payload.get("query", "Software Engineer"),
            location=payload.get("location", "Remote"),
            results_wanted=payload.get("limit", 10),
        )

        if jobs is None or jobs.empty:
            logger.warning("JobSpy returned empty results. Serving sample fallback.")
            return {"source": "sample_fallback", "data": get_sample_jobs()}

        return {"source": "jobspy", "data": jobs.to_dict('records')}
    except Exception as e:
        logger.warning(f"Local jobspy scrape blocked or failed: {e}. Falling back to sample data.")
        return {"source": "sample_fallback", "data": get_sample_jobs()}

local_scrape.safe_placeholder = {"source": "error", "data": []}

# --- Public API ---
async def scrape_jobs(payload: Dict[str, Any]) -> Dict[str, Any]:
    return await route(apify_scrape, local_scrape, payload)
