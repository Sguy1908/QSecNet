"""FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.router import api_router
from backend.config import get_settings
from backend.database.session import initialize_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Prepare local persistence before accepting requests."""
    initialize_database()
    yield


app = FastAPI(
    title="QSecNet API",
    version="0.1.0",
    description="Quantum Network Security Analysis & Threat Assessment Platform.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return liveness information for load balancers and container probes."""
    return {"status": "ok", "service": settings.app_name}
