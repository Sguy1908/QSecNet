"""Service health and configuration visibility endpoint."""

from fastapi import APIRouter
from sqlalchemy import text

from backend.config import get_settings
from backend.database.session import SessionLocal
from backend.services.ibm_service import ibm_enabled

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    """Return readiness information for API, DB, and optional IBM adapter."""
    settings = get_settings()
    database_ready = False
    with SessionLocal() as session:
        try:
            session.execute(text("SELECT 1"))
            database_ready = True
        except Exception:
            database_ready = False

    return {
        "status": "ok" if database_ready else "degraded",
        "version": "0.1.0",
        "environment": settings.environment,
        "service": settings.app_name,
        "readiness": {
            "database": database_ready,
            "ibm_integration_enabled": ibm_enabled(),
        },
    }
