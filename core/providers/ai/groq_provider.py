import logging
from typing import Any, AsyncIterator, Dict, List, Optional

from core.providers.ai.base import IAIProvider
from core.providers.ai.groq_client import GroqClient
from core.providers.ai.groq_config import GroqConfig
from core.providers.ai.groq_exceptions import translate_groq_exception
from core.providers.ai.groq_mapper import (GroqMapper, ProviderRequest,
                                           ProviderResponse)
from core.providers.ai.groq_models import get_model_metadata
from core.providers.base import (HealthStatus, ProviderCostEstimate,
                                 ProviderMetrics)

logger = logging.getLogger(__name__)


class GroqAIProvider(IAIProvider):
    """
    Canonical reference implementation for an AI Provider using Groq.
    Orchestrates low-level client logic, mapping, and telemetry.
    """

    def __init__(self, config: Optional[GroqConfig] = None):
        self._config = config or GroqConfig.from_settings()
        self._client = GroqClient(self._config)
        self._provider_id = f"official:groq"
        self._initialized = False

    # --- ProviderLifecycle Implementation ---

    async def initialize(self) -> None:
        """Sets up the underlying Groq SDK client."""
        try:
            await self._client.connect()
            self._initialized = True
            logger.debug(f"GroqAIProvider '{self._provider_id}' initialized.")
        except Exception as e:
            raise translate_groq_exception(e, self._provider_id)

    async def shutdown(self) -> None:
        """Gracefully closes the SDK client."""
        await self._client.close()
        self._initialized = False

    async def ready(self) -> bool:
        """Checks if the provider is initialized."""
        return self._initialized and self._config.api_key is not None

    async def health(self) -> HealthStatus:
        """Detailed health check via API ping."""
        if not await self.ready():
            return HealthStatus.UNHEALTHY

        if await self._client.ping():
            return HealthStatus.HEALTHY

        return HealthStatus.DEGRADED

    def metrics(self) -> ProviderMetrics:
        """Placeholder for runtime metrics collection (M5.5)."""
        return ProviderMetrics()

    # --- IAIProvider Implementation ---

    async def generate(
        self, messages: List[Dict[str, str]], config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executes a structured JSON completion."""
        # 1. Validation & Defaulting
        model_id = (config or {}).get("model") or self._config.default_model

        request = ProviderRequest(
            messages=messages,
            model=model_id,
            temperature=(config or {}).get("temperature") or self._config.temperature,
            max_tokens=(config or {}).get("max_tokens") or self._config.max_tokens,
            json_mode=(config or {}).get("json_mode") or False,
        )

        # 2. Execution
        try:
            params = GroqMapper.to_sdk_request(request)
            raw_response = await self._client.execute_completion(params)

            # 3. Mapping & Extraction
            response = GroqMapper.from_sdk_response(raw_response)

            return {
                "data": response.data,
                "meta": {
                    **response.meta,
                    "provider": self._provider_id,
                    "model": model_id,
                },
            }
        except Exception as e:
            raise translate_groq_exception(e, self._provider_id)

    async def stream(
        self, messages: List[Dict[str, str]], config: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """Provides real-time token streaming."""
        model_id = (config or {}).get("model") or self._config.default_model
        params = {
            "messages": messages,
            "model": model_id,
            "temperature": (config or {}).get("temperature")
            or self._config.temperature,
            "max_tokens": (config or {}).get("max_tokens") or self._config.max_tokens,
        }

        try:
            async for chunk in self._client.execute_stream(params):
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        yield delta.content
        except Exception as e:
            raise translate_groq_exception(e, self._provider_id)

    async def embed(self, text_input: str) -> List[float]:
        """Embeddings are currently not supported by native Groq SDK."""
        raise NotImplementedError(
            "Groq does not natively support embeddings. Use a cloud embedding provider."
        )

    def estimate_cost(self, messages: List[Dict[str, str]]) -> ProviderCostEstimate:
        """Estimated cost calculation for Groq requests."""
        return ProviderCostEstimate(estimated_usd=0.0)

    def supports(self, feature: str) -> bool:
        """Capability discovery based on model catalog."""
        # For this ref implementation, we'll check the default model
        meta = get_model_metadata(self._config.default_model)
        return feature in meta.capabilities
