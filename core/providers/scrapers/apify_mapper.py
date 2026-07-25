from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    """Internal model for job scraping requests."""

    query: str
    location: str = "Remote"
    limit: int = 10
    max_pages: Optional[int] = None


class ApifyRequestMapper:
    """
    Handles translation between JobHunterAI internal models and Apify Actor inputs.
    """

    @staticmethod
    def to_actor_input(actor_id: str, request: ScrapeRequest) -> Dict[str, Any]:
        """
        Maps generic scrape request to actor-specific JSON schema.
        """
        if "google-jobs-scraper" in actor_id:
            return {
                "queries": f"{request.query} in {request.location}",
                "maxPagesPerQuery": request.max_pages or (request.limit // 10 + 1),
                "maxResultsPerQuery": request.limit,
            }

        if "linkedin-jobs-scraper" in actor_id:
            # curious_coder actor expectations
            return {
                "urls": [
                    f"https://www.linkedin.com/jobs/search/?keywords={request.query}&location={request.location}"
                ],
                "count": max(request.limit, 10),
            }

        # Generic fallback
        return {
            "query": request.query,
            "location": request.location,
            "limit": request.limit,
        }
