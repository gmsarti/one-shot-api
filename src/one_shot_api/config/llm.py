from functools import lru_cache
from typing import Literal, Optional

from langchain_openai import ChatOpenAI
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """LLM configuration settings."""

    # LLM Settings
    model: Literal["gpt-4.1-nano", "gpt-4.1-mini-2025-04-14"] = "gpt-4.1-nano"
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None

    # API Settings
    api_host: str = "127.0.0.1"
    api_port: str = "8000"
    debug: bool = True

    # Database Settings
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "one_shot_api"

    # Default Settings
    default_rpg_system: str = "custom"
    default_story_length: str = "short"
    default_theme: str = "fantasy"

    class Config:
        env_prefix = "ONE_SHOT_"
        env_file = ".env"
        extra = "allow"


class LLMConfig:
    """Configuration for LLMs used in the story generation system."""

    def __init__(self, settings: LLMSettings):
        self.settings = settings

    def get_llm(self) -> ChatOpenAI:
        """Get a configured instance of the LLM."""
        return ChatOpenAI(
            model=self.settings.model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            api_key=self.settings.api_key,
        )


@lru_cache()
def get_llm_config() -> LLMConfig:
    """Get a cached instance of the LLM configuration."""
    settings = LLMSettings()
    return LLMConfig(settings)


# Default configuration
default_llm_config = get_llm_config()
