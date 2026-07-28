"""Top-level API router."""

from fastapi import APIRouter

from backend.api.health import router as health_router
from backend.api.security import router as security_router
from backend.api.simulations import router as simulations_router
from backend.api.topologies import router as topologies_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(topologies_router)
api_router.include_router(simulations_router)
api_router.include_router(security_router)
