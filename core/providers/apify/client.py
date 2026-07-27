import logging
from typing import Any, Dict, Optional
from core.config.settings import settings

try:
    from apify_client import ApifyClientAsync
except ImportError:
    ApifyClientAsync = None

logger = logging.getLogger("jobhunterai.apify_client")

class ApifyRegistryClient:
    """Hardened wrapper around ApifyClientAsync."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.APIFY_API_TOKEN
        self._client = None
        if self.token and ApifyClientAsync:
            self._client = ApifyClientAsync(self.token)

    async def call_actor(self, actor_id: str, run_input: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self._client:
            logger.error("Apify client not initialized. Check APIFY_API_TOKEN.")
            return None

        try:
            logger.info(f"Calling Apify Actor: {actor_id}")
            run = await self._client.actor(actor_id).call(run_input=run_input)

            if not run:
                return None

            # Safely extract dataset ID
            dataset_id = run.get("defaultDatasetId") or run.get("default_dataset_id")
            if not dataset_id:
                logger.error(f"Actor {actor_id} run finished but no dataset ID was returned.")
                return None

            # Fetch results
            dataset_items = await self._client.dataset(dataset_id).list_items()

            # Normalize items extraction
            if hasattr(dataset_items, "items"):
                items = dataset_items.items
            elif isinstance(dataset_items, dict):
                items = dataset_items.get("items", [])
            else:
                items = dataset_items # assume list

            return {
                "actor_id": actor_id,
                "run_id": run.get("id"),
                "items": items
            }

        except Exception as e:
            logger.error(f"Apify actor call failed: {e}")
            raise e
