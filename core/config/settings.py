import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the path to the .env file in the project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, ".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_path,
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