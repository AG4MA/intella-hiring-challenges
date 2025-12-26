"""
Satellite endpoints.

Provides CRUD operations and status management for satellites.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query

from app.api import dep_injection
from app.domain.models import Satellite

router = APIRouter()


@router.get("/", response_model=list[Satellite])
async def list_satellites(
    satellite_service: dep_injection.SatelliteServiceDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
):
    """
    List all satellites with pagination.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        List of satellites.
    """
    satellites = satellite_service.list_all()
    return satellites[skip : skip + limit]


@router.get("/{satellite_id}", response_model=Satellite)
async def get_satellite(
    satellite_id: UUID,
    satellite_service: dep_injection.SatelliteServiceDep,
):
    """
    Get a satellite by ID.

    Args:
        satellite_id: Satellite ID.

    Returns:
        Satellite details.

    Raises:
        HTTPException: 404 if satellite not found.
    """
    return satellite_service.get(satellite_id)


@router.patch("/{satellite_id}", response_model=Satellite)
async def update_satellite(
    satellite_id: UUID,
    satellite_service: dep_injection.SatelliteServiceDep,
    name: Optional[str] = None,
    metadata: Optional[dict] = None,
):
    """
    Update a satellite.

    Args:
        satellite_id: Satellite ID.
        name: New name (optional).
        metadata: New metadata (optional).

    Returns:
        Updated satellite.

    Raises:
        HTTPException: 404 if satellite not found.
    """
    return satellite_service.update(
        satellite_id=satellite_id,
        name=name,
        metadata=metadata,
    )


@router.post("/{satellite_id}/activate", response_model=Satellite)
async def activate_satellite(
    satellite_id: UUID,
    satellite_service: dep_injection.SatelliteServiceDep,
):
    """
    Activate a satellite.

    Args:
        satellite_id: Satellite ID.

    Returns:
        Activated satellite.

    Raises:
        HTTPException: 404 if satellite not found, 409 if already active.
    """
    return satellite_service.activate(satellite_id)


@router.post("/{satellite_id}/disable", response_model=Satellite)
async def disable_satellite(
    satellite_id: UUID,
    satellite_service: dep_injection.SatelliteServiceDep,
):
    """
    Disable a satellite.

    Args:
        satellite_id: Satellite ID.

    Returns:
        Disabled satellite.

    Raises:
        HTTPException: 404 if satellite not found, 409 if already disabled.
    """
    return satellite_service.disable(satellite_id)
