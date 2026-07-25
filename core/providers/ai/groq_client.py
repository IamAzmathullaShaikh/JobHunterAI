import asyncio
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

from groq import AsyncGroq

from core.providers.ai.groq_config import GroqConfig

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Low-level wrapper for the official Groq SDK.
    Handles raw API communication, streaming, and authentication.
    """

    def __init__(self, config: GroqConfig):
        self._config = config
        self._sdk: Optional[AsyncGroq] = None

    async def connect(self) -> None:
        """Initializes the AsyncGroq client."""
        if not self._config.api_key:
            raise ValueError("Groq API key is missing.")

        self._sdk = AsyncGroq(
            api_key=self._config.api_key,
            base_url=self._config.base_url,
            timeout=self._config.timeout,
        )
        logger.debug("AsyncGroq client initialized.")

    async def close(self) -> None:
        """Closes the underlying HTTP client."""
        if self._sdk:
            await self._sdk.close()
            self._sdk = None
            logger.debug("AsyncGroq client closed.")

    async def ping(self) -> bool:
        """Lightweight check to verify authentication."""
        if not self._sdk:
            return False
        try:
            # List models as a cheap health check
            await self._sdk.models.list()
            return True
        except Exception:
            return False

    async def execute_completion(self, params: Dict[str, Any]) -> Any:
        """Executes a single non-streaming chat completion."""
        if not self._sdk:
            raise RuntimeError("GroqClient not connected.")

        return await self._sdk.chat.completions.create(**params)

    async def execute_stream(self, params: Dict[str, Any]) -> AsyncIterator[Any]:
        """Executes a streaming chat completion."""
        if not self._sdk:
            raise RuntimeError("GroqClient not connected.")

        params["stream"] = True
        stream = await self._sdk.chat.completions.create(**params)
        async for chunk in stream:
            yield chunk
