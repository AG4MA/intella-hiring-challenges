"""Satellite domain model."""

from datetime import date
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.enums import SatelliteStatus
from app.domain.models.validators import NonEmptyStr


class Satellite(BaseModel):
    """Represents a satellite in the telemetry system.

    A satellite is the top-level entity that contains multiple units,
    each of which can have multiple telemetry parameters.

    Attributes:
        id: Unique identifier for the satellite.
        name: Human-readable name of the satellite.
        launch_date: Date when the satellite was launched.
        status: Current operational status of the satellite.
        metadata: Additional arbitrary metadata about the satellite.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique satellite identifier")
    name: NonEmptyStr = Field(..., description="Human-readable satellite name")
    launch_date: date = Field(..., description="Date of satellite launch")
    status: SatelliteStatus = Field(
        default=SatelliteStatus.ACTIVE,
        description="Current operational status",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional satellite metadata",
    )
