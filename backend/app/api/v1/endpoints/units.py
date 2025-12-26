"""
Unit endpoints.

Provides CRUD operations for satellite units.
"""

from uuid import UUID

from fastapi import APIRouter

from app.api import dep_injection
from app.domain.models import Unit

router = APIRouter()


@router.post("/", response_model=Unit, status_code=201)
async def create_unit(
    unit: Unit,
    unit_service: dep_injection.UnitServiceDep,
):
    """
    Create a new unit.

    Args:
        unit: Unit data to create.

    Returns:
        Created unit.

    Raises:
        HTTPException: 404 if parent satellite not found, 409 if unit already exists.
    """
    return unit_service.create(unit)


@router.get("/", response_model=list[Unit])
async def list_units(
    satellite_id: UUID,
    unit_service: dep_injection.UnitServiceDep,
):
    """
    List all units for a satellite.

    Args:
        satellite_id: Filter units by satellite ID.

    Returns:
        List of units.
    """
    return unit_service.list_by_satellite(satellite_id)


@router.get("/{unit_id}", response_model=Unit)
async def get_unit(
    unit_id: UUID,
    unit_service: dep_injection.UnitServiceDep,
):
    """
    Get a unit by ID.

    Args:
        unit_id: Unit ID.

    Returns:
        Unit details.

    Raises:
        HTTPException: 404 if unit not found.
    """
    return unit_service.get(unit_id)


@router.put("/{unit_id}", response_model=Unit)
async def update_unit(
    unit_id: UUID,
    unit_service: dep_injection.UnitServiceDep,
    name: str | None = None,
    description: str | None = None,
):
    """
    Update a unit.

    Args:
        unit_id: Unit ID.
        name: New name (optional).
        description: New description (optional).

    Returns:
        Updated unit.

    Raises:
        HTTPException: 404 if unit not found.
    """
    return unit_service.update(
        unit_id=unit_id,
        name=name,
        description=description,
    )


@router.delete("/{unit_id}", status_code=204)
async def delete_unit(
    unit_id: UUID,
    unit_service: dep_injection.UnitServiceDep,
):
    """
    Delete a unit.

    Args:
        unit_id: Unit ID.

    Raises:
        HTTPException: 404 if unit not found.
    """
    unit_service.delete(unit_id)
