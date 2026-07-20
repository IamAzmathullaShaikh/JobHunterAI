import os
from abc import ABC, abstractmethod
import litellm  # Assuming we use litellm for free LLMs

class LLMClient(ABC):
    @abstractmethod
    async def chat_completion(self, model: str, messages: list) -> dict:
        pass

class GroqLLMClient(LLMClient):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured in .env file.")
        
        litellm.api_key = self.api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.default_model = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")

    async def chat_completion(self, model: str, messages: list) -> dict:
        response = litellm.create_chat_completion(
            model=model or self.default_model,
            messages=messages
        )
        return response

class OpenRouterLLMClient(LLMClient):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured in .env file.")
        
        litellm.api_key = self.api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = os.getenv("OPENROUTER_MODEL", "openrouter/meta-llama/llama-3.3-70b-instruct:free")

    async def chat_completion(self, model: str, messages: list) -> dict:
        response = litellm.create_chat_completion(
            model=model or self.default_model,
            messages=messages
        )
        return response

class OllamaLLMClient(LLMClient):
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434/v1")
        self.default_model = os.getenv("OLLAMA_MODEL", "ollama/qwen2.5-coder:7b")

    async def chat_completion(self, model: str, messages: list) -> dict:
        response = litellm.create_chat_completion(
            model=model or self.default_model,
            messages=messages
        )
        return response

class GeminiLLMClient(LLMClient):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in .env file.")
        
        litellm.api_key = self.api_key
        self.base_url = "https://api.gemini.com/openai/v1"
        self.default_model = os.getenv("GEMINI_MODEL", "gemini/llama-3.3-70b-versatile")

    async def chat_completion(self, model: str, messages: list) -> dict:
        response = litellm.create_chat_completion(
            model=model or self.default_model,
            messages=messages
        )
        return response

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
