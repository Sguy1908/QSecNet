"""Application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = "QSecNet"
    environment: str = "development"
    database_url: str = "sqlite:///./qsecnet.db"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    ibm_quantum_token: str | None = None
    ibm_quantum_instance: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="QSECNET_")


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
