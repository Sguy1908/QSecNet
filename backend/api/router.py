"""Versioned API router assembly."""

from fastapi import APIRouter

from backend.api.projects import router as projects_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects_router)
