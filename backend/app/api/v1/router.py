"""
API v1 Router.

This module defines the main router for API version 1,
aggregating all v1 endpoint routers under the /v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import parameters, satellites, telemetry, units

# Create the main v1 router
router = APIRouter()

# Include endpoint routers
router.include_router(satellites.router, prefix="/satellites", tags=["satellites"])
router.include_router(units.router, prefix="/units", tags=["units"])
router.include_router(parameters.router, prefix="/parameters", tags=["parameters"])
router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])


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
            "satellites": "/v1/satellites",
            "telemetry": "/v1/telemetry (coming soon)",
        },
    }
