import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.scrapers.manager import ScraperManager
from core.schemas.job_listing import JobListingCreate

@pytest.mark.asyncio
async def test_scraper_manager_parallel_dispatch():
    """Verify that ScraperManager dispatches multiple actors in parallel."""
    manager = ScraperManager()

    # Mock Registry and Selector
    mock_actors = [
        {"id": "a", "name": "Actor A", "actor_id": "id-a", "priority": 1},
        {"id": "b", "name": "Actor B", "actor_id": "id-b", "priority": 2}
    ]

    with patch("core.providers.apify.selector.selector.select_actors_parallel", return_value=mock_actors):
        with patch("core.scrapers.apify_scraper.ApifyJobScraper.scrape", new_callable=AsyncMock) as mock_scrape:
            mock_scrape.return_value = [JobListingCreate(
                job_id_raw="123", title="T", company_name="C", location="L",
                source="S", url="U", description_raw="D"
            )]

            # Disable stealth scrapers for pure fleet test
            manager.stealth_scrapers = []

            results = await manager.run_all("Python", "Remote")

            # Should have called scrape twice (once per actor)
            assert mock_scrape.call_count == 2
            assert len(results) == 2

def test_deduplication_variations():
    """Verify that DeduplicationEngine handles company name variations."""
    from core.deduplication_engine import deduplication_engine

    job1 = {"title": "Software Engineer", "company_name": "Google", "location": "Remote"}
    job2 = {"title": "Software Engineer", "company_name": "Google LLC", "location": "Remote"}

    assert deduplication_engine.are_duplicates(job1, job2) is True
