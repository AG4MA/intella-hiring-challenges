"""In-memory repository implementations with indexing."""

import bisect
from collections import defaultdict
from datetime import datetime
from uuid import UUID

from app.domain.errors import ConflictError
from app.domain.models import Parameter, Satellite, TelemetryData, Unit


class InMemorySatelliteRepository:
    """In-memory implementation of satellite repository."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self._satellites: dict[UUID, Satellite] = {}

    def add(self, satellite: Satellite) -> Satellite:
        """Add a new satellite.

        Args:
            satellite: The satellite to add.

        Returns:
            The added satellite.

        Raises:
            ConflictError: If satellite with same ID already exists.
        """
        if satellite.id in self._satellites:
            raise ConflictError(
                "Satellite already exists",
                {"satellite_id": str(satellite.id)},
            )
        self._satellites[satellite.id] = satellite
        return satellite

    def get(self, satellite_id: UUID) -> Satellite | None:
        """Get a satellite by ID.

        Args:
            satellite_id: The satellite ID.

        Returns:
            The satellite if found, None otherwise.
        """
        return self._satellites.get(satellite_id)

    def list_all(self) -> list[Satellite]:
        """List all satellites.

        Returns:
            List of all satellites.
        """
        return list(self._satellites.values())

    def delete(self, satellite_id: UUID) -> bool:
        """Delete a satellite by ID.

        Args:
            satellite_id: The satellite ID.

        Returns:
            True if deleted, False if not found.
        """
        if satellite_id in self._satellites:
            del self._satellites[satellite_id]
            return True
        return False


class InMemoryUnitRepository:
    """In-memory implementation of unit repository with satellite index."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self._units: dict[UUID, Unit] = {}
        self._units_by_satellite: dict[UUID, list[UUID]] = defaultdict(list)

    def add(self, unit: Unit) -> Unit:
        """Add a new unit.

        Args:
            unit: The unit to add.

        Returns:
            The added unit.

        Raises:
            ConflictError: If unit with same ID already exists.
        """
        if unit.id in self._units:
            raise ConflictError(
                "Unit already exists",
                {"unit_id": str(unit.id)},
            )
        self._units[unit.id] = unit
        self._units_by_satellite[unit.satellite_id].append(unit.id)
        return unit

    def get(self, unit_id: UUID) -> Unit | None:
        """Get a unit by ID.

        Args:
            unit_id: The unit ID.

        Returns:
            The unit if found, None otherwise.
        """
        return self._units.get(unit_id)

    def get_by_satellite(self, satellite_id: UUID) -> list[Unit]:
        """Get all units for a satellite.

        Args:
            satellite_id: The satellite ID.

        Returns:
            List of units belonging to the satellite.
        """
        unit_ids = self._units_by_satellite.get(satellite_id, [])
        return [self._units[uid] for uid in unit_ids if uid in self._units]

    def list_all(self) -> list[Unit]:
        """List all units.

        Returns:
            List of all units.
        """
        return list(self._units.values())

    def delete(self, unit_id: UUID) -> bool:
        """Delete a unit by ID.

        Args:
            unit_id: The unit ID.

        Returns:
            True if deleted, False if not found.
        """
        unit = self._units.get(unit_id)
        if unit is None:
            return False

        # Remove from main storage
        del self._units[unit_id]

        # Remove from satellite index
        satellite_units = self._units_by_satellite.get(unit.satellite_id)
        if satellite_units and unit_id in satellite_units:
            satellite_units.remove(unit_id)

        return True


class InMemoryParameterRepository:
    """In-memory implementation of parameter repository with unit index."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self._parameters: dict[UUID, Parameter] = {}
        self._parameters_by_unit: dict[UUID, list[UUID]] = defaultdict(list)

    def add(self, parameter: Parameter) -> Parameter:
        """Add a new parameter.

        Args:
            parameter: The parameter to add.

        Returns:
            The added parameter.

        Raises:
            ConflictError: If parameter with same ID already exists.
        """
        if parameter.id in self._parameters:
            raise ConflictError(
                "Parameter already exists",
                {"parameter_id": str(parameter.id)},
            )
        self._parameters[parameter.id] = parameter
        self._parameters_by_unit[parameter.unit_id].append(parameter.id)
        return parameter

    def get(self, parameter_id: UUID) -> Parameter | None:
        """Get a parameter by ID.

        Args:
            parameter_id: The parameter ID.

        Returns:
            The parameter if found, None otherwise.
        """
        return self._parameters.get(parameter_id)

    def get_by_unit(self, unit_id: UUID) -> list[Parameter]:
        """Get all parameters for a unit.

        Args:
            unit_id: The unit ID.

        Returns:
            List of parameters belonging to the unit.
        """
        param_ids = self._parameters_by_unit.get(unit_id, [])
        return [self._parameters[pid] for pid in param_ids if pid in self._parameters]

    def list_all(self) -> list[Parameter]:
        """List all parameters.

        Returns:
            List of all parameters.
        """
        return list(self._parameters.values())

    def update(self, parameter: Parameter) -> Parameter:
        """Update a parameter.

        Args:
            parameter: The parameter to update.

        Returns:
            The updated parameter.

        Raises:
            ConflictError: If parameter with same ID does not exist.
        """
        if parameter.id not in self._parameters:
            raise ConflictError(
                "Parameter not found",
                {"parameter_id": str(parameter.id)},
            )
        self._parameters[parameter.id] = parameter
        return parameter

    def delete(self, parameter_id: UUID) -> bool:
        """Delete a parameter by ID.

        Args:
            parameter_id: The parameter ID.

        Returns:
            True if deleted, False if not found.
        """
        parameter = self._parameters.get(parameter_id)
        if parameter is None:
            return False

        # Remove from main storage
        del self._parameters[parameter_id]

        # Remove from unit index
        unit_params = self._parameters_by_unit.get(parameter.unit_id)
        if unit_params and parameter_id in unit_params:
            unit_params.remove(parameter_id)

        return True


class InMemoryTelemetryRepository:
    """In-memory telemetry repository with append-only storage and timestamp indexing.

    Telemetry data is stored in append-only fashion, sorted by timestamp within
    each parameter for efficient range queries using binary search.
    """

    def __init__(self) -> None:
        """Initialize the repository."""
        self._telemetry: dict[UUID, TelemetryData] = {}
        # Parameter ID -> list of (timestamp, telemetry_id) tuples, sorted by timestamp
        self._telemetry_by_parameter: dict[UUID, list[tuple[datetime, UUID]]] = (
            defaultdict(list)
        )

    def add(self, telemetry: TelemetryData) -> TelemetryData:
        """Add a new telemetry data point (append-only).

        Args:
            telemetry: The telemetry data to add.

        Returns:
            The added telemetry data.

        Note:
            Telemetry is append-only; duplicate IDs will overwrite.
        """
        self._telemetry[telemetry.id] = telemetry

        # Insert into sorted index using bisect
        param_data = self._telemetry_by_parameter[telemetry.parameter_id]
        entry = (telemetry.timestamp, telemetry.id)
        bisect.insort(param_data, entry)

        return telemetry

    def get(self, telemetry_id: UUID) -> TelemetryData | None:
        """Get telemetry data by ID.

        Args:
            telemetry_id: The telemetry data ID.

        Returns:
            The telemetry data if found, None otherwise.
        """
        return self._telemetry.get(telemetry_id)

    def get_by_parameter(
        self,
        parameter_id: UUID,
        limit: int | None = None,
    ) -> list[TelemetryData]:
        """Get telemetry data for a parameter, sorted by timestamp.

        Args:
            parameter_id: The parameter ID.
            limit: Optional maximum number of records to return (most recent).

        Returns:
            List of telemetry data for the parameter, sorted by timestamp ascending.
        """
        entries = self._telemetry_by_parameter.get(parameter_id, [])

        # Apply limit from the end (most recent)
        if limit is not None and len(entries) > limit:
            entries = entries[-limit:]

        # Return telemetry data sorted by timestamp
        return [self._telemetry[tid] for _, tid in entries if tid in self._telemetry]

    def list_all(self) -> list[TelemetryData]:
        """List all telemetry data.

        Returns:
            List of all telemetry data.
        """
        return list(self._telemetry.values())

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
        entries = self._telemetry_by_parameter.get(parameter_id, [])

        # Use bisect to find range
        start_idx = bisect.bisect_left(entries, (start_time, UUID(int=0)))
        # Use a "max" UUID for upper bound to include all entries at end_time
        end_idx = bisect.bisect_right(entries, (end_time, UUID(int=2**128 - 1)))

        # Extract telemetry data
        return [
            self._telemetry[tid]
            for _, tid in entries[start_idx:end_idx]
            if tid in self._telemetry
        ]
