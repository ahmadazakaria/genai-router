from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables with prefix 'GENAI_'."""

    ollama_base_url: str = "http://localhost:11434"
    api_keys: str | None = None  # Comma-separated list of accepted keys

    @property
    def allowed_api_keys(self) -> set[str]:
        """Return a set of allowed API keys.

        If the *GENAI_API_KEYS* env-var is unset or empty, authentication is
        disabled and the returned set is empty.
        """

        if not self.api_keys:
            return set()

        # Split on comma and strip whitespace.
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}

    class Config:
        env_prefix = "GENAI_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings() 