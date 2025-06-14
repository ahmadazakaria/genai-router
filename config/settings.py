from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables with prefix 'GENAI_'."""

    ollama_base_url: str = "http://localhost:11434"
    api_keys: str | None = None  # Comma-separated list of accepted keys
    # e.g. "60/min" or "100/hour". Empty → no rate limiting.
    rate_limit: str | None = None

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

    @property
    def parsed_rate_limit(self) -> tuple[int, int] | None:
        """Return `(max_requests, window_seconds)` if rate limiting is configured."""

        if not self.rate_limit:
            return None

        try:
            amount, per = self.rate_limit.split("/")
            max_req = int(amount)
            if per == "sec":
                window = 1
            elif per == "min" or per == "minute":
                window = 60
            elif per == "hour":
                window = 3600
            else:
                window = int(per)
            return max_req, window
        except Exception:  # pragma: no cover
            return None

    class Config:
        env_prefix = "GENAI_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings() 