"""
API v1 Router.

This module defines the main router for API version 1,
aggregating all v1 endpoint routers under the /v1 prefix.
"""

from fastapi import APIRouter

# Create the main v1 router
router = APIRouter()


@router.get("/")
async def root_v1():
    """
    V1 API root endpoint.

    Returns:
        Welcome message and API information.
    """
    return {
        "message": "Satellite Telemetry API v1",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "satellites": "/v1/satellites (coming soon)",
            "telemetry": "/v1/telemetry (coming soon)",
        },
    }
