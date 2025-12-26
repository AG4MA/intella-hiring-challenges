"""Unit domain model."""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.validators import NonEmptyStr


class Unit(BaseModel):
    """Represents a functional unit within a satellite.

    A unit is a logical grouping of related telemetry parameters,
    such as a power subsystem or thermal control module.

    Attributes:
        id: Unique identifier for the unit.
        satellite_id: Reference to the parent satellite.
        name: Human-readable name of the unit.
        description: Detailed description of the unit's function.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique unit identifier")
    satellite_id: UUID = Field(..., description="Parent satellite identifier")
    name: NonEmptyStr = Field(..., description="Human-readable unit name")
    description: NonEmptyStr = Field(..., description="Unit function description")
