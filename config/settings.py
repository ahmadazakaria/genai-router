from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables with prefix 'GENAI_'."""

    ollama_base_url: str = "http://localhost:11434"

    class Config:
        env_prefix = "GENAI_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings() 