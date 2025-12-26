"""Telemetry data domain model."""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.validators import FiniteFloat, UtcDatetime


class TelemetryData(BaseModel):
    """Represents a single telemetry data point.

    A telemetry data point captures the measured value of a parameter
    at a specific point in time.

    Attributes:
        id: Unique identifier for the telemetry record.
        parameter_id: Reference to the measured parameter.
        timestamp: UTC timestamp when the measurement was taken.
        value: The measured value (must be a finite float).
    """

    id: UUID = Field(default_factory=uuid4, description="Unique telemetry identifier")
    parameter_id: UUID = Field(..., description="Reference to measured parameter")
    timestamp: UtcDatetime = Field(..., description="UTC timestamp of measurement")
    value: FiniteFloat = Field(..., description="Measured value (finite float)")
