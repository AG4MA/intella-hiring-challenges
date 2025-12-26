"""Unit service with business logic."""

from uuid import UUID

from app.domain.errors import NotFoundError
from app.domain.models import Unit
from app.storage.base import SatelliteRepository, UnitRepository


class UnitService:
    """Service for unit business logic."""

    def __init__(
        self,
        unit_repository: UnitRepository,
        satellite_repository: SatelliteRepository,
    ) -> None:
        """Initialize the service.

        Args:
            unit_repository: The unit repository.
            satellite_repository: The satellite repository.
        """
        self._repo = unit_repository
        self._satellite_repo = satellite_repository

    def create(self, unit: Unit) -> Unit:
        """Create a new unit.

        Args:
            unit: The unit to create.

        Returns:
            The created unit.

        Raises:
            NotFoundError: If parent satellite does not exist.
            ConflictError: If unit with same ID already exists.
        """
        # Check satellite exists
        satellite = self._satellite_repo.get(unit.satellite_id)
        if satellite is None:
            raise NotFoundError(
                "Parent satellite not found",
                {"satellite_id": str(unit.satellite_id)},
            )

        return self._repo.add(unit)

    def get(self, unit_id: UUID) -> Unit:
        """Get a unit by ID.

        Args:
            unit_id: The unit ID.

        Returns:
            The unit.

        Raises:
            NotFoundError: If unit not found.
        """
        unit = self._repo.get(unit_id)
        if unit is None:
            raise NotFoundError(
                "Unit not found",
                {"unit_id": str(unit_id)},
            )
        return unit

    def list_by_satellite(self, satellite_id: UUID) -> list[Unit]:
        """List all units for a satellite.

        Args:
            satellite_id: The satellite ID.

        Returns:
            List of units for the satellite.
        """
        return self._repo.get_by_satellite(satellite_id)

    def update(
        self,
        unit_id: UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> Unit:
        """Update a unit.

        Args:
            unit_id: The unit ID.
            name: New name (optional).
            description: New description (optional).

        Returns:
            The updated unit.

        Raises:
            NotFoundError: If unit not found.
        """
        unit = self.get(unit_id)

        if name is not None:
            unit.name = name
        if description is not None:
            unit.description = description

        return unit

    def delete(self, unit_id: UUID) -> None:
        """Delete a unit.

        Args:
            unit_id: The unit ID.

        Raises:
            NotFoundError: If unit not found.
        """
        if not self._repo.delete(unit_id):
            raise NotFoundError(
                "Unit not found",
                {"unit_id": str(unit_id)},
            )
