from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    environment: str = "dev"
    debug: bool = False
    log_level: str = "INFO"
    telemetry_step_seconds: int = 10
    telemetry_backfill_hours: int = 24


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
