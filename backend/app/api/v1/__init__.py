"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import analytics

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)
