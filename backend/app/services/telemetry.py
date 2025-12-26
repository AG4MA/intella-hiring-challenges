"""Telemetry service with business logic."""

from datetime import datetime
from uuid import UUID

from app.domain.errors import DomainValidationError, NotFoundError
from app.domain.models import ParameterType, SatelliteStatus, TelemetryData
from app.storage.base import (
    ParameterRepository,
    SatelliteRepository,
    TelemetryRepository,
    UnitRepository,
)


class TelemetryService:
    """Service for telemetry business logic."""

    def __init__(
        self,
        telemetry_repository: TelemetryRepository,
        parameter_repository: ParameterRepository,
        unit_repository: UnitRepository,
        satellite_repository: SatelliteRepository,
    ) -> None:
        """Initialize the service.

        Args:
            telemetry_repository: The telemetry repository.
            parameter_repository: The parameter repository.
            unit_repository: The unit repository.
            satellite_repository: The satellite repository.
        """
        self._repo = telemetry_repository
        self._param_repo = parameter_repository
        self._unit_repo = unit_repository
        self._sat_repo = satellite_repository

    def append_point(self, telemetry: TelemetryData) -> TelemetryData:
        """Append a new telemetry data point.

        Args:
            telemetry: The telemetry data to append.

        Returns:
            The added telemetry data.

        Raises:
            NotFoundError: If parameter, unit, or satellite not found.
            DomainValidationError: If parameter or satellite is not active,
                or if value is invalid for parameter type.
        """
        # Get parameter
        parameter = self._param_repo.get(telemetry.parameter_id)
        if parameter is None:
            raise NotFoundError(
                "Parameter not found",
                {"parameter_id": str(telemetry.parameter_id)},
            )

        # Check parameter is active
        if not parameter.is_active:
            raise DomainValidationError(
                "Cannot add telemetry for inactive parameter",
                {"parameter_id": str(parameter.id)},
            )

        # Get unit
        unit = self._unit_repo.get(parameter.unit_id)
        if unit is None:
            raise NotFoundError(
                "Unit not found",
                {"unit_id": str(parameter.unit_id)},
            )

        # Get satellite
        satellite = self._sat_repo.get(unit.satellite_id)
        if satellite is None:
            raise NotFoundError(
                "Satellite not found",
                {"satellite_id": str(unit.satellite_id)},
            )

        # Check satellite is active
        if satellite.status != SatelliteStatus.ACTIVE:
            raise DomainValidationError(
                "Cannot add telemetry for inactive satellite",
                {"satellite_id": str(satellite.id)},
            )

        # Validate value based on parameter type
        self._validate_value_for_type(telemetry.value, parameter.parameter_type)

        # Add telemetry
        return self._repo.add(telemetry)

    def _validate_value_for_type(
        self,
        value: float,
        parameter_type: ParameterType,
    ) -> None:
        """Validate a telemetry value based on parameter type.

        Args:
            value: The value to validate.
            parameter_type: The parameter type.

        Raises:
            DomainValidationError: If value is invalid for the parameter type.
        """
        # Type-specific validation rules
        if parameter_type == ParameterType.TEMPERATURE:
            if value < -273.15:  # Below absolute zero
                raise DomainValidationError(
                    "Temperature cannot be below absolute zero",
                    {"value": value, "min": -273.15},
                )
        elif parameter_type == ParameterType.VOLTAGE:
            # Reasonable voltage range for satellites
            if value < -1000 or value > 1000:
                raise DomainValidationError(
                    "Voltage out of reasonable range",
                    {"value": value, "min": -1000, "max": 1000},
                )
        elif parameter_type == ParameterType.CURRENT:
            # Current should be non-negative in most satellite systems
            if value < 0:
                raise DomainValidationError(
                    "Current must be non-negative",
                    {"value": value, "min": 0},
                )
        elif parameter_type == ParameterType.PRESSURE:
            if value < 0:
                raise DomainValidationError(
                    "Pressure must be non-negative",
                    {"value": value, "min": 0},
                )
        elif parameter_type == ParameterType.HUMIDITY:
            if value < 0 or value > 100:
                raise DomainValidationError(
                    "Humidity must be between 0 and 100",
                    {"value": value, "min": 0, "max": 100},
                )
        elif parameter_type == ParameterType.POWER:
            if value < 0:
                raise DomainValidationError(
                    "Power must be non-negative",
                    {"value": value, "min": 0},
                )

    def query(
        self,
        parameter_id: UUID,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int | None = None,
    ) -> list[TelemetryData]:
        """Query telemetry data for a parameter.

        Args:
            parameter_id: The parameter ID.
            start_time: Start time (inclusive, optional).
            end_time: End time (inclusive, optional).
            limit: Maximum number of results (optional).

        Returns:
            List of telemetry data, sorted by timestamp.

        Raises:
            NotFoundError: If parameter not found.
        """
        # Verify parameter exists
        parameter = self._param_repo.get(parameter_id)
        if parameter is None:
            raise NotFoundError(
                "Parameter not found",
                {"parameter_id": str(parameter_id)},
            )

        # Query based on time range or limit
        if start_time is not None and end_time is not None:
            # Time range query
            results = self._repo.get_by_parameter_time_range(
                parameter_id,
                start_time,
                end_time,
            )
            # Apply limit if specified
            if limit is not None and len(results) > limit:
                results = results[-limit:]
            return results
        else:
            # Simple query with optional limit
            return self._repo.get_by_parameter(parameter_id, limit=limit)
