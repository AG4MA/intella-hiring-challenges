"""
Parameter endpoints.

Provides CRUD operations and activation management for telemetry parameters.
"""

from uuid import UUID

from fastapi import APIRouter, Query

from app.api import dep_injection
from app.domain.models import Parameter

router = APIRouter()


@router.post("/", response_model=Parameter, status_code=201)
async def create_parameter(
    parameter: Parameter,
    parameter_service: dep_injection.ParameterServiceDep,
):
    """
    Create a new parameter.

    Args:
        parameter: Parameter data to create.

    Returns:
        Created parameter.

    Raises:
        HTTPException: 404 if parent unit not found, 409 if parameter already exists.
    """
    return parameter_service.create(parameter)


@router.get("/", response_model=list[Parameter])
async def list_parameters(
    parameter_service: dep_injection.ParameterServiceDep,
    unit_id: UUID | None = Query(None, description="Filter by unit ID"),
):
    """
    List all parameters, optionally filtered by unit.

    Args:
        unit_id: Optional unit ID to filter parameters.

    Returns:
        List of parameters.
    """
    if unit_id is not None:
        return parameter_service.list_by_unit(unit_id)
    return parameter_service.list_all()


@router.get("/{parameter_id}", response_model=Parameter)
async def get_parameter(
    parameter_id: UUID,
    parameter_service: dep_injection.ParameterServiceDep,
):
    """
    Get a parameter by ID.

    Args:
        parameter_id: Parameter ID.

    Returns:
        Parameter details.

    Raises:
        HTTPException: 404 if parameter not found.
    """
    return parameter_service.get(parameter_id)


@router.put("/{parameter_id}", response_model=Parameter)
async def update_parameter(
    parameter_id: UUID,
    parameter_service: dep_injection.ParameterServiceDep,
    name: str | None = None,
    unit_of_measurement: str | None = None,
):
    """
    Update a parameter.

    Args:
        parameter_id: Parameter ID.
        name: New name (optional).
        unit_of_measurement: New unit of measurement (optional).

    Returns:
        Updated parameter.

    Raises:
        HTTPException: 404 if parameter not found.
    """
    return parameter_service.update(
        parameter_id=parameter_id,
        name=name,
        unit_of_measurement=unit_of_measurement,
    )


@router.post("/{parameter_id}/activate", response_model=Parameter)
async def activate_parameter(
    parameter_id: UUID,
    parameter_service: dep_injection.ParameterServiceDep,
):
    """
    Activate a parameter for data collection.

    Args:
        parameter_id: Parameter ID.

    Returns:
        Activated parameter.

    Raises:
        HTTPException: 404 if parameter not found.
    """
    return parameter_service.activate(parameter_id)


@router.post("/{parameter_id}/deactivate", response_model=Parameter)
async def deactivate_parameter(
    parameter_id: UUID,
    parameter_service: dep_injection.ParameterServiceDep,
):
    """
    Deactivate a parameter to stop data collection.

    Args:
        parameter_id: Parameter ID.

    Returns:
        Deactivated parameter.

    Raises:
        HTTPException: 404 if parameter not found.
    """
    return parameter_service.deactivate(parameter_id)


@router.delete("/{parameter_id}", status_code=204)
async def delete_parameter(
    parameter_id: UUID,
    parameter_service: dep_injection.ParameterServiceDep,
):
    """
    Delete a parameter.

    Args:
        parameter_id: Parameter ID.

    Raises:
        HTTPException: 404 if parameter not found.
    """
    parameter_service.delete(parameter_id)
