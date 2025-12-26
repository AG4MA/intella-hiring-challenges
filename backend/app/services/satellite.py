"""Satellite service with business logic."""

from datetime import datetime
from uuid import UUID

from app.domain.errors import ConflictError, NotFoundError
from app.domain.models import Satellite, SatelliteStatus
from app.storage.base import (
    ParameterRepository,
    SatelliteRepository,
    TelemetryRepository,
    UnitRepository,
)


class SatelliteService:
    """Service for satellite business logic."""

    def __init__(
        self,
        repository: SatelliteRepository,
        unit_repository: UnitRepository | None = None,
        parameter_repository: ParameterRepository | None = None,
        telemetry_repository: TelemetryRepository | None = None,
    ) -> None:
        """Initialize the service.

        Args:
            repository: The satellite repository.
            unit_repository: Optional unit repository for aggregations.
            parameter_repository: Optional parameter repository for aggregations.
            telemetry_repository: Optional telemetry repository for aggregations.
        """
        self._repo = repository
        self._unit_repo = unit_repository
        self._parameter_repo = parameter_repository
        self._telemetry_repo = telemetry_repository

    def list_all(self) -> list[Satellite]:
        """List all satellites.

        Returns:
            List of all satellites.
        """
        return self._repo.list_all()

    def get(self, satellite_id: UUID) -> Satellite:
        """Get a satellite by ID.

        Args:
            satellite_id: The satellite ID.

        Returns:
            The satellite.

        Raises:
            NotFoundError: If satellite not found.
        """
        satellite = self._repo.get(satellite_id)
        if satellite is None:
            raise NotFoundError(
                "Satellite not found",
                {"satellite_id": str(satellite_id)},
            )
        return satellite

    def create(self, satellite: Satellite) -> Satellite:
        """Create a new satellite.

        Args:
            satellite: The satellite to create.

        Returns:
            The created satellite.

        Raises:
            ConflictError: If satellite with same ID already exists.
        """
        return self._repo.add(satellite)

    def update(
        self,
        satellite_id: UUID,
        name: str | None = None,
        status: SatelliteStatus | None = None,
        metadata: dict | None = None,
    ) -> Satellite:
        """Update a satellite.

        Args:
            satellite_id: The satellite ID.
            name: New name (optional).
            status: New status (optional).
            metadata: New metadata (optional).

        Returns:
            The updated satellite.

        Raises:
            NotFoundError: If satellite not found.
        """
        satellite = self.get(satellite_id)

        # Update fields if provided
        if name is not None:
            satellite.name = name
        if status is not None:
            satellite.status = status
        if metadata is not None:
            satellite.metadata = metadata

        return satellite

    def activate(self, satellite_id: UUID) -> Satellite:
        """Activate a satellite.

        Args:
            satellite_id: The satellite ID.

        Returns:
            The activated satellite.

        Raises:
            NotFoundError: If satellite not found.
            ConflictError: If satellite is already active.
        """
        satellite = self.get(satellite_id)

        if satellite.status == SatelliteStatus.ACTIVE:
            raise ConflictError(
                "Satellite is already active",
                {"satellite_id": str(satellite_id)},
            )

        satellite.status = SatelliteStatus.ACTIVE
        return satellite

    def disable(self, satellite_id: UUID) -> Satellite:
        """Disable a satellite.

        Args:
            satellite_id: The satellite ID.

        Returns:
            The disabled satellite.

        Raises:
            NotFoundError: If satellite not found.
            ConflictError: If satellite is already disabled.
        """
        satellite = self.get(satellite_id)

        if satellite.status == SatelliteStatus.DISABLED:
            raise ConflictError(
                "Satellite is already disabled",
                {"satellite_id": str(satellite_id)},
            )

        satellite.status = SatelliteStatus.DISABLED
        return satellite

    def get_operational_status_summary(self) -> list[dict]:
        """Get operational status summary for all satellites.

        Aggregates data from satellite, unit, parameter, and telemetry repositories
        to provide a comprehensive operational overview for each satellite.

        Returns:
            List of dictionaries containing operational status information:
            - satellite_id: UUID of the satellite
            - is_active: Whether satellite is active
            - last_telemetry_ts: Most recent telemetry timestamp or None
            - telemetry_points_count: Total telemetry data points
            - units_count: Number of units
            - parameters_count: Total parameters across all units
            - operational_status: "DISABLED", "NO_DATA", or "OK"

        Note:
            If repositories are not provided during initialization,
            counts will be 0 and status will reflect only satellite active state.
        """
        satellites = self.list_all()
        summaries = []

        # Pre-compute telemetry aggregates if available
        telemetry_stats: dict[UUID, tuple[datetime | None, int]] = {}
        if self._telemetry_repo is not None and self._parameter_repo is not None:
            all_telemetry = self._telemetry_repo.list_all()
            # Group by parameter to find last timestamp and count
            telemetry_by_param: dict[UUID, list] = {}
            for telem in all_telemetry:
                if telem.parameter_id not in telemetry_by_param:
                    telemetry_by_param[telem.parameter_id] = []
                telemetry_by_param[telem.parameter_id].append(telem)

            # Get parameter to unit mapping
            all_parameters = self._parameter_repo.list_all()
            param_to_unit = {p.id: p.unit_id for p in all_parameters}

            # Get unit to satellite mapping
            if self._unit_repo is not None:
                all_units = self._unit_repo.list_all()
                unit_to_satellite = {u.id: u.satellite_id for u in all_units}

                # Aggregate telemetry by satellite
                for param_id, telems in telemetry_by_param.items():
                    unit_id = param_to_unit.get(param_id)
                    if unit_id:
                        sat_id = unit_to_satellite.get(unit_id)
                        if sat_id:
                            if sat_id not in telemetry_stats:
                                telemetry_stats[sat_id] = (None, 0)

                            last_ts, count = telemetry_stats[sat_id]
                            count += len(telems)

                            # Find max timestamp
                            max_ts = max(t.timestamp for t in telems)
                            if last_ts is None or max_ts > last_ts:
                                last_ts = max_ts

                            telemetry_stats[sat_id] = (last_ts, count)

        for satellite in satellites:
            # Count units
            units_count = 0
            if self._unit_repo is not None:
                units = self._unit_repo.get_by_satellite(satellite.id)
                units_count = len(units)

            # Count parameters
            parameters_count = 0
            if self._parameter_repo is not None and self._unit_repo is not None:
                units = self._unit_repo.get_by_satellite(satellite.id)
                for unit in units:
                    params = self._parameter_repo.get_by_unit(unit.id)
                    parameters_count += len(params)

            # Get telemetry stats
            last_telemetry_ts, telemetry_points_count = telemetry_stats.get(
                satellite.id, (None, 0)
            )

            # Determine operational status
            is_active = satellite.status == SatelliteStatus.ACTIVE
            if not is_active:
                operational_status = "DISABLED"
            elif last_telemetry_ts is None:
                operational_status = "NO_DATA"
            else:
                operational_status = "OK"

            summaries.append(
                {
                    "satellite_id": satellite.id,
                    "is_active": is_active,
                    "last_telemetry_ts": last_telemetry_ts,
                    "telemetry_points_count": telemetry_points_count,
                    "units_count": units_count,
                    "parameters_count": parameters_count,
                    "operational_status": operational_status,
                }
            )

        return summaries
