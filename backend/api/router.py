"""Versioned API router assembly."""

from fastapi import APIRouter

from backend.api.attacks import router as attacks_router
from backend.api.exports import router as exports_router
from backend.api.ibm import router as ibm_router
from backend.api.network import router as network_router
from backend.api.projects import router as projects_router
from backend.api.recommendations import router as recommendations_router
from backend.api.security import router as security_router
from backend.api.simulations import router as simulations_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects_router)
api_router.include_router(simulations_router)
api_router.include_router(network_router)
api_router.include_router(attacks_router)
api_router.include_router(security_router)
api_router.include_router(recommendations_router)
api_router.include_router(exports_router)
api_router.include_router(ibm_router)
