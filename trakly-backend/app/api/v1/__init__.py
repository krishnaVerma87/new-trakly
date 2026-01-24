"""API v1 router aggregation."""
from fastapi import APIRouter

from app.api.v1 import auth, users, organizations, projects, features, issues, dashboard

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(organizations.router)
api_router.include_router(projects.router)
api_router.include_router(features.router)
api_router.include_router(issues.router)
api_router.include_router(dashboard.router)

__all__ = ["api_router"]
