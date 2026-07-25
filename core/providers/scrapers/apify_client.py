import asyncio
import logging
from typing import Any, Dict, List, Optional

from apify_client import ApifyClientAsync

from core.providers.scrapers.apify_config import ApifyConfig

logger = logging.getLogger(__name__)


class ApifyClient:
    """
    Low-level wrapper for the Apify SDK.
    Handles authentication, actor execution, and dataset retrieval.
    """

    def __init__(self, config: ApifyConfig):
        self._config = config
        self._sdk: Optional[ApifyClientAsync] = None

    async def connect(self) -> None:
        """Initializes the Apify SDK client."""
        if not self._config.api_token:
            raise ValueError("Apify API token is missing.")

        self._sdk = ApifyClientAsync(token=self._config.api_token)
        logger.debug("ApifyClientAsync initialized.")

    async def disconnect(self) -> None:
        """Cleans up the SDK resources."""
        if self._sdk:
            # Apify SDK does not require explicit close for client,
            # but we null it out for safety.
            self._sdk = None
            logger.debug("Apify SDK client disconnected.")

    async def ping(self) -> bool:
        """Verifies authentication with Apify."""
        if not self._sdk:
            return False
        try:
            # Fetch current user info as a heartbeat
            await self._sdk.user().get()
            return True
        except Exception:
            return False

    async def run_actor(
        self, actor_id: str, run_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Starts an actor and waits for completion.
        Returns the raw Run object.
        """
        if not self._sdk:
            raise RuntimeError("ApifyClient not connected.")

        logger.info(f"Starting Apify Actor: {actor_id}")

        # Use .call() for synchronous wait in the async context
        run = await self._sdk.actor(actor_id).call(
            run_input=run_input,
            memory_mbytes=self._config.memory_mbytes,
            timeout_secs=self._config.timeout_secs,
        )
        return run

    async def get_dataset_items(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all items from a completed dataset.
        """
        if not self._sdk:
            raise RuntimeError("ApifyClient not connected.")

        dataset = await self._sdk.dataset(dataset_id).list_items()

        # SDK might return a ListPage or dict depending on version/call
        if hasattr(dataset, "items"):
            return dataset.items
        if isinstance(dataset, dict):
            return dataset.get("items", [])
        return list(dataset) if isinstance(dataset, (list, tuple)) else []

    async def abort_run(self, run_id: str) -> bool:
        """Attempts to stop a running actor task."""
        if not self._sdk:
            return False
        try:
            await self._sdk.run(run_id).abort()
            return True
        except Exception as e:
            logger.error(f"Failed to abort Apify run {run_id}: {e}")
            return False
