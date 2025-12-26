"""Base repository protocols and interfaces."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.models import Parameter, Satellite, TelemetryData, Unit


class SatelliteRepository(Protocol):
    """Protocol for satellite repository operations."""

    def add(self, satellite: Satellite) -> Satellite:
        """Add a new satellite.

        Args:
            satellite: The satellite to add.

        Returns:
            The added satellite.

        Raises:
            ConflictError: If satellite with same ID already exists.
        """
        ...

    def get(self, satellite_id: UUID) -> Satellite | None:
        """Get a satellite by ID.

        Args:
            satellite_id: The satellite ID.

        Returns:
            The satellite if found, None otherwise.
        """
        ...

    def list_all(self) -> list[Satellite]:
        """List all satellites.

        Returns:
            List of all satellites.
        """
        ...

    def delete(self, satellite_id: UUID) -> bool:
        """Delete a satellite by ID.

        Args:
            satellite_id: The satellite ID.

        Returns:
            True if deleted, False if not found.
        """
        ...


class UnitRepository(Protocol):
    """Protocol for unit repository operations."""

    def add(self, unit: Unit) -> Unit:
        """Add a new unit.

        Args:
            unit: The unit to add.

        Returns:
            The added unit.

        Raises:
            ConflictError: If unit with same ID already exists.
        """
        ...

    def get(self, unit_id: UUID) -> Unit | None:
        """Get a unit by ID.

        Args:
            unit_id: The unit ID.

        Returns:
            The unit if found, None otherwise.
        """
        ...

    def get_by_satellite(self, satellite_id: UUID) -> list[Unit]:
        """Get all units for a satellite.

        Args:
            satellite_id: The satellite ID.

        Returns:
            List of units belonging to the satellite.
        """
        ...

    def delete(self, unit_id: UUID) -> bool:
        """Delete a unit by ID.

        Args:
            unit_id: The unit ID.

        Returns:
            True if deleted, False if not found.
        """
        ...


class ParameterRepository(Protocol):
    """Protocol for parameter repository operations."""

    def add(self, parameter: Parameter) -> Parameter:
        """Add a new parameter.

        Args:
            parameter: The parameter to add.

        Returns:
            The added parameter.

        Raises:
            ConflictError: If parameter with same ID already exists.
        """
        ...

    def get(self, parameter_id: UUID) -> Parameter | None:
        """Get a parameter by ID.

        Args:
            parameter_id: The parameter ID.

        Returns:
            The parameter if found, None otherwise.
        """
        ...

    def get_by_unit(self, unit_id: UUID) -> list[Parameter]:
        """Get all parameters for a unit.

        Args:
            unit_id: The unit ID.

        Returns:
            List of parameters belonging to the unit.
        """
        ...

    def list_all(self) -> list[Parameter]:
        """List all parameters.

        Returns:
            List of all parameters.
        """
        ...

    def update(self, parameter: Parameter) -> Parameter:
        """Update a parameter.

        Args:
            parameter: The parameter to update.

        Returns:
            The updated parameter.

        Raises:
            NotFoundError: If parameter not found.
        """
        ...

    def delete(self, parameter_id: UUID) -> bool:
        """Delete a parameter by ID.

        Args:
            parameter_id: The parameter ID.

        Returns:
            True if deleted, False if not found.
        """
        ...


class TelemetryRepository(Protocol):
    """Protocol for telemetry repository operations."""

    def add(self, telemetry: TelemetryData) -> TelemetryData:
        """Add a new telemetry data point.

        Args:
            telemetry: The telemetry data to add.

        Returns:
            The added telemetry data.
        """
        ...

    def get(self, telemetry_id: UUID) -> TelemetryData | None:
        """Get telemetry data by ID.

        Args:
            telemetry_id: The telemetry data ID.

        Returns:
            The telemetry data if found, None otherwise.
        """
        ...

    def get_by_parameter(
        self,
        parameter_id: UUID,
        limit: int | None = None,
    ) -> list[TelemetryData]:
        """Get telemetry data for a parameter.

        Args:
            parameter_id: The parameter ID.
            limit: Optional maximum number of records to return.

        Returns:
            List of telemetry data for the parameter, sorted by timestamp.
        """
        ...

    def get_by_parameter_time_range(
        self,
        parameter_id: UUID,
        start_time: datetime,
        end_time: datetime,
    ) -> list[TelemetryData]:
        """Get telemetry data for a parameter within a time range.

        Args:
            parameter_id: The parameter ID.
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).

        Returns:
            List of telemetry data within the time range, sorted by timestamp.
        """
        ...
