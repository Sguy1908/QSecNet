"""Versioned readiness endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from backend.config import get_settings
from backend.database.session import engine

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    service_ready: bool


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Report readiness and validate database connectivity."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return HealthResponse(
            status="degraded", version="0.1.0", environment=get_settings().environment, service_ready=False
        )
    return HealthResponse(
        status="ok", version="0.1.0", environment=get_settings().environment, service_ready=True
    )
