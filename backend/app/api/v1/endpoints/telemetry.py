"""
Telemetry endpoints.

Provides query operations for telemetry data.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from fastapi import APIRouter, Query

from app.api import dep_injection
from app.domain.models import TelemetryData

router = APIRouter()


class OrderDirection(str, Enum):
    """Sort order direction."""

    ASC = "asc"
    DESC = "desc"


@router.get("/", response_model=list[TelemetryData])
async def query_telemetry(
    telemetry_service: dep_injection.TelemetryServiceDep,
    parameter_id: UUID | None = Query(None, description="Filter by parameter ID"),
    from_ts: datetime | None = Query(None, description="Start time (ISO 8601)"),
    to_ts: datetime | None = Query(None, description="End time (ISO 8601)"),
    order: OrderDirection = Query(OrderDirection.DESC, description="Sort order"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
):
    """
    Query telemetry data with filters.

    Args:
        parameter_id: Filter by parameter ID (required for now).
        from_ts: Filter records from this timestamp (inclusive).
        to_ts: Filter records to this timestamp (inclusive).
        order: Sort order (asc or desc, default desc).
        limit: Maximum number of records to return.
        offset: Number of records to skip for pagination.

    Returns:
        List of telemetry data points.

    Raises:
        HTTPException: 404 if parameter not found, 422 if invalid parameters.
    """
    # For now, require parameter_id
    if parameter_id is None:
        # Could extend to support satellite_id/unit_id filtering in future
        # For now, return empty list if no parameter_id specified
        return []

    # Query telemetry via service
    results = telemetry_service.query(
        parameter_id=parameter_id,
        start_time=from_ts,
        end_time=to_ts,
        limit=None,  # We'll handle limit/offset after getting all results
    )

    # Apply ordering
    if order == OrderDirection.ASC:
        results = sorted(results, key=lambda t: t.timestamp)
    else:
        results = sorted(results, key=lambda t: t.timestamp, reverse=True)

    # Apply pagination
    start_idx = offset
    end_idx = offset + limit
    return results[start_idx:end_idx]
