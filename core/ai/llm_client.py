import os
import logging
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

try:
    from groq import AsyncGroq
except ImportError:
    AsyncGroq = None

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from core.config.settings import settings
from core.ai.smart_router import route

logger = logging.getLogger("jobhunterai.llm_client")


class Capability:
    REASONING = "reasoning"
    FAST = "fast"
    VISION = "vision"


class LLMClient(ABC):
    @abstractmethod
    async def chat_completion(self, model: str = None, messages: list = []) -> Any:
        pass

    def get_model_for_capability(self, capability: str) -> str:
        """Maps system capabilities to provider-specific models."""
        provider = settings.AI_PROVIDER.lower()

        # If auto, use the default provider's mapping
        if provider == "auto":
            provider = settings.DEFAULT_AI_PROVIDER.lower()

        mapping = {
            "groq": {
                Capability.REASONING: settings.GROQ_MODEL,
                Capability.FAST: "llama-3.1-8b-instant",
            },
            "gemini": {
                Capability.REASONING: settings.GEMINI_MODEL,
                Capability.FAST: "gemini-1.5-flash-8b",
            },
            "openrouter": {
                Capability.REASONING: settings.OPENROUTER_MODEL,
                Capability.FAST: settings.OPENROUTER_MODEL,
            },
            "ollama": {
                Capability.REASONING: settings.OLLAMA_MODEL,
                Capability.FAST: settings.OLLAMA_MODEL,
            }
        }

        provider_map = mapping.get(provider, mapping["groq"])
        return provider_map.get(capability, list(provider_map.values())[0])


class GroqLLMClient(LLMClient):
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key or not AsyncGroq:
            self.client = None
            return

        self.client = AsyncGroq(api_key=self.api_key)
        self.default_model = settings.GROQ_MODEL

    async def chat_completion(self, model: str = None, messages: list = []) -> Any:
        if not self.client:
            raise ValueError("Groq client not available (check API key or installation)")
        target_model = model or self.default_model
        response = await self.client.chat.completions.create(
            model=target_model, messages=messages
        )
        return response


class OpenRouterLLMClient(LLMClient):
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        if not self.api_key or not AsyncOpenAI:
            self.client = None
            return

        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.default_model = settings.OPENROUTER_MODEL

    async def chat_completion(self, model: str = None, messages: list = []) -> Any:
        if not self.client:
            raise ValueError("OpenRouter client not available")
        target_model = model or self.default_model
        response = await self.client.chat.completions.create(
            model=target_model, messages=messages
        )
        return response


class OllamaLLMClient(LLMClient):
    def __init__(self):
        if not AsyncOpenAI:
            self.client = None
            return

        self.client = AsyncOpenAI(
            base_url=settings.OLLAMA_HOST,
            api_key="ollama",  # placeholder
        )
        self.default_model = settings.OLLAMA_MODEL

    async def chat_completion(self, model: str = None, messages: list = []) -> Any:
        if not self.client:
            raise ValueError("Ollama client not available")
        target_model = model or self.default_model
        response = await self.client.chat.completions.create(
            model=target_model, messages=messages
        )
        return response


class GeminiLLMClient(LLMClient):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key or not AsyncOpenAI:
            self.client = None
            return

        self.client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key,
        )
        self.default_model = settings.GEMINI_MODEL

    async def chat_completion(self, model: str = None, messages: list = []) -> Any:
        if not self.client:
            raise ValueError("Gemini client not available")
        target_model = model or self.default_model
        response = await self.client.chat.completions.create(
            model=target_model, messages=messages
        )
        return response


class SmartLLMClient(LLMClient):
    """
    Orchestrates multiple LLM providers with automatic fallback.
    Utilizes 3-tier routing: Groq (Primary) -> Gemini (Secondary) -> Ollama (Local).
    """

    async def chat_completion(self, model: str = None, messages: list = []) -> Any:

        async def groq_tier(**kwargs):
            client = GroqLLMClient()
            if not client.client:
                raise ValueError("Groq client not available")
            target_model = model or settings.GROQ_MODEL
            return await client.chat_completion(target_model, messages)

        groq_tier.required_envs = ["GROQ_API_KEY"]
        groq_tier.model_id = model or settings.GROQ_MODEL
        groq_tier.safe_placeholder = {"error": "Groq tier failed"}

        async def gemini_tier(**kwargs):
            client = GeminiLLMClient()
            if not client.client:
                raise ValueError("Gemini client not available")
            target_model = model or settings.GEMINI_MODEL
            return await client.chat_completion(target_model, messages)

        gemini_tier.required_envs = ["GEMINI_API_KEY"]
        gemini_tier.model_id = model or settings.GEMINI_MODEL
        gemini_tier.safe_placeholder = {"error": "Gemini tier failed"}

        async def ollama_tier(**kwargs):
            client = OllamaLLMClient()
            if not client.client:
                raise ValueError("Ollama client not available")
            target_model = model or settings.OLLAMA_MODEL
            return await client.chat_completion(target_model, messages)

        ollama_tier.required_envs = []
        ollama_tier.safe_placeholder = {"error": "All LLM tiers exhausted"}

        return await route(groq_tier, gemini_tier, ollama_tier)


def get_llm_client(provider_override: str = None) -> LLMClient:
    """Factory function for retrieving the configured LLM client."""
    provider = (provider_override or settings.AI_PROVIDER).lower()

    if provider == "auto":
        return SmartLLMClient()
    elif provider == "groq":
        return GroqLLMClient()
    elif provider == "openrouter":
        return OpenRouterLLMClient()
    elif provider == "ollama":
        return OllamaLLMClient()
    elif provider == "gemini":
        return GeminiLLMClient()
    else:
        logger.warning(f"Unknown AI provider '{provider}'. Defaulting to Groq.")
        return GroqLLMClient()
