import logging
import time
from typing import Any, Dict, List

from application.ports.providers.health_port import (ComponentStatus,
                                                     IHealthProvider)
from application.ports.repositories.interfaces import IJobRepository
from core.config.settings import settings
from core.providers.manager import ProviderManager

logger = logging.getLogger(__name__)


class PlatformValidationService:
    """
    Orchestrates system-wide health and readiness checks.
    Ensures repositories and cloud providers are operational.
    """

    def __init__(self, provider_manager: ProviderManager, job_repo: IJobRepository):
        self._provider_manager = provider_manager
        self._job_repo = job_repo

    async def run_full_validation(self) -> Dict[str, Any]:
        results = {"status": "healthy", "timestamp": time.time(), "components": {}}

        # 1. Check AI Provider
        try:
            ai_provider = await self._provider_manager.get_default_provider("ai")
            ai_health = await ai_provider.health()
            results["components"]["ai_provider"] = str(ai_health.value)
            if ai_health.value != "healthy":
                results["status"] = "degraded"
        except Exception as e:
            results["components"]["ai_provider"] = f"error: {str(e)}"
            results["status"] = "degraded"

        # 2. Check Scraper Provider
        try:
            scraper = await self._provider_manager.get_default_provider("scraper")
            scraper_health = await scraper.health()
            results["components"]["scraper_provider"] = str(scraper_health.value)
        except Exception as e:
            results["components"]["scraper_provider"] = f"error: {str(e)}"
            results["status"] = "degraded"

        # 3. Check Repository
        try:
            count = await self._job_repo.count()
            results["components"]["database"] = "connected"
        except Exception as e:
            results["components"]["database"] = f"error: {str(e)}"
            results["status"] = "unhealthy"

        return results

    def validate_configuration(self) -> List[str]:
        """Checks for missing critical environment variables."""
        errors = []
        if not settings.GROQ_API_KEY and not settings.GEMINI_API_KEY:
            errors.append("At least one AI provider API key is required.")
        if not settings.APIFY_API_TOKEN:
            errors.append("Apify API token is missing.")
        return errors
