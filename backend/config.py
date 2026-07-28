"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = "QSecNet"
    environment: str = "development"
    database_url: str = "sqlite:///./qsecnet.db"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="QSECNET_")


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
