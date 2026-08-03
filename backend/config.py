"""Application configuration loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime settings for the QSecNet API."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="QSECNET_")
    environment: str = "development"
    database_url: str = "sqlite:///./qsecnet.db"
    log_level: str = "INFO"
    ibm_token: str | None = None
    ibm_instance: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()
