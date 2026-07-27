import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict
from core.providers.apify.registry import registry as default_registry
from core.config.settings import settings

try:
    from apify_client import ApifyClient
except ImportError:
    ApifyClient = None

logger = logging.getLogger("jobhunterai.apify_health")

class ApifyHealthChecker:
    """Monitors Apify actor health by checking recent run status."""

    def __init__(self, registry_instance=None):
        self.registry = registry_instance or default_registry
        self._last_check: Dict[str, datetime] = {}
        self.check_interval = timedelta(minutes=5)

    async def check_actor_health(self, actor_id: str) -> bool:
        """Verify if the actor is healthy. Caches results for 5 mins."""
        if actor_id in self._last_check:
            if datetime.now() - self._last_check[actor_id] < self.check_interval:
                return self.registry.is_actor_healthy(actor_id)

        if not ApifyClient or not settings.APIFY_API_TOKEN:
            # Can't check, assume healthy to avoid false positives
            return True

        try:
            client = ApifyClient(settings.APIFY_API_TOKEN)
            # Find the internal apify actor ID from our registry metadata if possible
            actor_meta = self.registry.get_actor(actor_id)
            apify_id = actor_meta.get("actor_id") if actor_meta else actor_id

            # Check last 3 runs
            runs = client.actor(apify_id).runs().list(limit=3, desc=True).items
            if not runs:
                return True # Never run, assume OK

            # If all last 3 failed, mark unhealthy
            failures = [r for r in runs if r.get("status") in ["FAILED", "ABORTED", "TIMED-OUT"]]
            if len(failures) == len(runs):
                self.registry.mark_unhealthy(actor_id, f"Last {len(runs)} runs failed")
                return False

            self.registry.mark_actor_healthy(actor_id)
            self._last_check[actor_id] = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Health check failed for {actor_id}: {e}")
            return True # Conservative fallback

# Singleton instance
health_checker = ApifyHealthChecker()
