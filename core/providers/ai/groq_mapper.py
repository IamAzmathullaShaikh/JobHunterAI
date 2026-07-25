import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProviderRequest(BaseModel):
    """Internal model for AI generation requests."""

    messages: List[Dict[str, str]]
    model: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4096
    json_mode: bool = False


class ProviderResponse(BaseModel):
    """Internal model for AI generation results."""

    data: Any
    meta: Dict[str, Any]


class ProviderStreamChunk(BaseModel):
    """Standardized object for real-time token streaming."""

    content: str
    is_final: bool = False


class GroqMapper:
    """
    Handles translation between JobHunterAI internal models and Groq SDK objects.
    Ensures internal systems never see 'groq.ChatCompletion' directly.
    """

    @staticmethod
    def to_sdk_request(request: ProviderRequest) -> Dict[str, Any]:
        """Maps internal request to Groq SDK dictionary."""
        params = {
            "messages": request.messages,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        if request.json_mode:
            params["response_format"] = {"type": "json_object"}

        return params

    @staticmethod
    def from_sdk_response(response: Any) -> ProviderResponse:
        """Maps Groq SDK response to internal ProviderResponse."""
        content = response.choices[0].message.content

        # Try to auto-parse JSON if requested
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = content

        from core.providers.ai.usage_extractor import GroqUsageExtractor

        usage = GroqUsageExtractor.extract(response)

        return ProviderResponse(data=data, meta=usage)
