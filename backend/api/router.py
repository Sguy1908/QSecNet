"""Top-level API router."""

from fastapi import APIRouter

from backend.api.attacks import router as attacks_router
from backend.api.health import router as health_router
from backend.api.ibm import router as ibm_router
from backend.api.recommendations import router as recommendations_router
from backend.api.reports import router as reports_router
from backend.api.security import router as security_router
from backend.api.simulations import router as simulations_router
from backend.api.topologies import router as topologies_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(attacks_router)
api_router.include_router(ibm_router)
api_router.include_router(topologies_router)
api_router.include_router(simulations_router)
api_router.include_router(security_router)
api_router.include_router(reports_router)
api_router.include_router(recommendations_router)
