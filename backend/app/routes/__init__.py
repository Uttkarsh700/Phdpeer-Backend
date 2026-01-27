"""
API routes package.

This package contains all API route definitions.
Routes should be organized by domain/feature.

Example structure:
    - users.py: User-related endpoints
    - timelines.py: Timeline-related endpoints
    - auth.py: Authentication endpoints
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include route modules here
# Example:
# from app.routes import users, timelines, auth
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(timelines.router, prefix="/timelines", tags=["timelines"])
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

__all__ = ["api_router"]
