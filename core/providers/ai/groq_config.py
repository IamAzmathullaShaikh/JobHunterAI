from typing import Optional

from pydantic import BaseModel, Field

from core.config.settings import settings


class GroqConfig(BaseModel):
    """Configuration for the Groq LLM provider."""

    api_key: Optional[str] = Field(default=None)
    base_url: Optional[str] = Field(default=None)
    default_model: str = Field(default="llama-3.3-70b-versatile")

    # Generation parameters
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)

    # SDK parameters
    timeout: float = Field(default=30.0)
    max_retries: int = Field(default=2)

    @classmethod
    def from_settings(cls):
        """Loads configuration from global application settings."""
        return cls(api_key=settings.GROQ_API_KEY, default_model=settings.GROQ_MODEL)
