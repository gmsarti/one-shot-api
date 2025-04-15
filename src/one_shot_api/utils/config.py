import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4.1-nano")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Database Configuration
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "one_shot_api")

    # Story Generation Defaults
    DEFAULT_RPG_SYSTEM: str = os.getenv("DEFAULT_RPG_SYSTEM", "custom")
    DEFAULT_STORY_LENGTH: str = os.getenv("DEFAULT_STORY_LENGTH", "short")
    DEFAULT_THEME: str = os.getenv("DEFAULT_THEME", "fantasy")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
