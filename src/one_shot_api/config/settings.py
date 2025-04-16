from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "One-Shot API"
    API_HOST: str = "127.0.0.1"  # Default to localhost for security
    API_PORT: int = 8000
    DEBUG: bool = True

    # Database Settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Security Settings
    SECRET_KEY: str = "your-secret-key-here"  # You should change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM Configuration
    LLM_PROVIDER: str
    LLM_MODEL: str
    OPENAI_API_KEY: str

    # Story Generation Defaults
    DEFAULT_RPG_SYSTEM: str
    DEFAULT_STORY_LENGTH: str
    DEFAULT_THEME: str

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
