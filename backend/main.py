"""ASGI entry point for QSecNet."""

import logging

from fastapi import FastAPI

from backend.api.router import api_router
from backend.config import get_settings


def create_app() -> FastAPI:
    """Create the QSecNet API application."""
    settings = get_settings()
    logging.basicConfig(level=getattr(settings, "log_level", "INFO"))
    app = FastAPI(
        title="QSecNet API",
        version="0.1.0",
        description="Quantum Network Security Analysis & Threat Assessment Platform",
    )
    app.include_router(api_router)

    @app.get("/health", tags=["Operations"])
    async def health_check() -> dict[str, str]:
        """Report whether the service process is ready to receive requests."""
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
