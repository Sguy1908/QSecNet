"""Versioned API router assembly."""

from fastapi import APIRouter

from backend.api.projects import router as projects_router
from backend.api.simulations import router as simulations_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects_router)
api_router.include_router(simulations_router)
