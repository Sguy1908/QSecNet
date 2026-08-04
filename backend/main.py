"""ASGI entry point for QSecNet."""

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.api.errors import install_exception_handlers
from backend.api.router import api_router
from backend.config import get_settings
from backend.utils.observability import configure_logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Attach request IDs and emit structured request completion records."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        started_at = perf_counter()
        response = await call_next(request)  # type: ignore[operator]
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "%s %s completed with %s in %.3fs",
            request.method,
            request.url.path,
            response.status_code,
            perf_counter() - started_at,
            extra={"request_id": request_id},
        )
        return response


def create_app() -> FastAPI:
    """Create the QSecNet API application."""
    settings = get_settings()
    configure_logging(getattr(settings, "log_level", "INFO"))
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(
        title="QSecNet API",
        version="0.1.0",
        description="Quantum Network Security Analysis & Threat Assessment Platform",
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    install_exception_handlers(app)

    @app.get("/health", tags=["Operations"])
    async def health_check() -> dict[str, str]:
        """Report whether the service process is ready to receive requests."""
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
