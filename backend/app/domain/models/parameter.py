"""Parameter domain model."""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.enums import ParameterType
from app.domain.models.validators import NonEmptyStr


class Parameter(BaseModel):
    """Represents a telemetry parameter measured by a satellite unit.

    A parameter defines what is being measured, its unit of measurement,
    and whether it is currently active for data collection.

    Attributes:
        id: Unique identifier for the parameter.
        unit_id: Reference to the parent unit.
        name: Human-readable name of the parameter.
        unit_of_measurement: Physical unit of the measured value (e.g., "V", "°C").
        parameter_type: Classification of the parameter type.
        is_active: Whether the parameter is actively collecting data.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique parameter identifier")
    unit_id: UUID = Field(..., description="Parent unit identifier")
    name: NonEmptyStr = Field(..., description="Human-readable parameter name")
    unit_of_measurement: NonEmptyStr = Field(
        ...,
        description="Physical unit of measurement",
    )
    parameter_type: ParameterType = Field(
        ...,
        description="Classification of parameter type",
    )
    is_active: bool = Field(
        default=True,
        description="Whether parameter is actively collecting data",
    )
