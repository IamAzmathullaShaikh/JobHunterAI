import os
from abc import ABC, abstractmethod
try:
    from groq import AsyncGroq
except ImportError:
    AsyncGroq = None

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

class LLMClient(ABC):
    @abstractmethod
    async def chat_completion(self, model: str, messages: list) -> Any:
        pass

class GroqLLMClient(LLMClient):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured in .env file.")
        
        if not AsyncGroq:
            raise ImportError("groq package is not installed.")

        self.client = AsyncGroq(api_key=self.api_key)
        self.default_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    async def chat_completion(self, model: str, messages: list) -> Any:
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages
        )
        return response

class OpenRouterLLMClient(LLMClient):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured in .env file.")
        
        if not AsyncOpenAI:
            raise ImportError("openai package is not installed.")

        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.default_model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

    async def chat_completion(self, model: str, messages: list) -> Any:
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages
        )
        return response

class OllamaLLMClient(LLMClient):
    def __init__(self):
        if not AsyncOpenAI:
            raise ImportError("openai package is not installed.")

        self.client = AsyncOpenAI(
            base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434/v1"),
            api_key="ollama", # placeholder
        )
        self.default_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

    async def chat_completion(self, model: str, messages: list) -> Any:
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages
        )
        return response

class GeminiLLMClient(LLMClient):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in .env file.")
        
        if not AsyncOpenAI:
            raise ImportError("openai package is not installed.")

        # Using OpenAI compatible endpoint for Gemini
        self.client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key,
        )
        self.default_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    async def chat_completion(self, model: str, messages: list) -> Any:
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages
        )
        return response

from typing import Any

def get_llm_client() -> LLMClient:
    provider = os.getenv("AI_PROVIDER", "groq").lower()
    
    if provider == "groq":
        return GroqLLMClient()
    elif provider == "openrouter":
        return OpenRouterLLMClient()
    elif provider == "ollama":
        return OllamaLLMClient()
    elif provider == "gemini":
        return GeminiLLMClient()
    else:
        raise ValueError(f"Unsupported AI_PROVIDER: {provider}")
