"""ASGI entry point for QSecNet."""

import logging

from fastapi import FastAPI

from backend.config import get_settings


def create_app() -> FastAPI:
    """Create the QSecNet API application."""
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    app = FastAPI(
        title="QSecNet API",
        version="0.1.0",
        description="Quantum Network Security Analysis & Threat Assessment Platform",
    )

    @app.get("/health", tags=["Operations"])
    async def health_check() -> dict[str, str]:
        """Report whether the service process is ready to receive requests."""
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
