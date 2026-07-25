import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the path to the .env file in the project root
project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_path), env_file_encoding="utf-8", extra="ignore"
    )

    # --- Core System Settings ---
    DEBUG: bool = True
    PORT: int = 8000
    NODE_ENV: str = "development"
    LOG_DIR: str = "logs"
    DATABASE_URL: str = "sqlite+aiosqlite:///jobhunter.db"

    # --- AI Provider Configuration ---
    AI_PROVIDER: str = "groq"  # groq, gemini, openai, openrouter, ollama

    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"

    OLLAMA_HOST: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"

    # --- Scraper Configuration ---
    APIFY_API_TOKEN: Optional[str] = None
    APIFY_ACTOR_ID: str = "apify/google-jobs-scraper"

    HUNTER_API_KEY: Optional[str] = None

    # --- Matching & ATS Intelligence ---
    MATCHING_CONFIG_VERSION: str = "1.0.0"
    MATCHING_WEIGHTS: Dict[str, float] = {
        "skills": 0.35,
        "experience": 0.25,
        "education": 0.10,
        "keywords": 0.15,
        "location": 0.10,
        "salary": 0.05,
    }
    MIN_KEYWORD_SCORE: float = 0.4
    MIN_SKILL_MATCH: float = 0.5
    ATS_THRESHOLDS: Dict[str, float] = {"completeness": 0.6, "quantification": 0.4}

    # Skill Aliases for deterministic resolution
    SKILL_ALIASES: Dict[str, str] = {
        "js": "javascript",
        "ts": "typescript",
        "node": "node.js",
        "py": "python",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "aws": "amazon web services",
        "gcp": "google cloud platform",
    }

    @field_validator("MATCHING_WEIGHTS")
    def validate_weights(cls, v):
        total = sum(v.values())
        if not (0.99 <= total <= 1.01 or 99 <= total <= 101):
            raise ValueError(
                f"MATCHING_WEIGHTS must sum to 1.0 or 100 (current: {total})"
            )
        return v

    # --- Security ---
    CORS_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    def validate_cors(cls, v):
        node_env = os.getenv("NODE_ENV", "development").lower()
        if node_env == "production":
            if isinstance(v, list) and "*" in v:
                raise ValueError("CORS_ORIGINS cannot contain '*' in production")
            if isinstance(v, str) and v == "*":
                raise ValueError("CORS_ORIGINS cannot be '*' in production")
        return v

    @field_validator("AI_PROVIDER")
    def validate_provider(cls, v):
        allowed = ["groq", "gemini", "openai", "openrouter", "ollama"]
        if v.lower() not in allowed:
            raise ValueError(f"AI_PROVIDER must be one of {allowed}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        return self.NODE_ENV.lower() == "production"


# Singleton instance
settings = Settings()
