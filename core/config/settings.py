import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # Core System Settings
    DEBUG: bool = True
    LOG_DIR: str = "logs"
    DATABASE_URL: str = "sqlite+aiosqlite:///jobhunter.db"

    # AI & Cloud Integrations
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENAI_API_KEY: str = ""
    APIFY_API_TOKEN: str = ""  # Reads from .env automatically

settings = Settings()