"""Satellite service with business logic."""

from uuid import UUID

from app.domain.errors import ConflictError, NotFoundError
from app.domain.models import Satellite, SatelliteStatus
from app.storage.base import SatelliteRepository


class SatelliteService:
    """Service for satellite business logic."""

    def __init__(self, repository: SatelliteRepository) -> None:
        """Initialize the service.

        Args:
            repository: The satellite repository.
        """
        self._repo = repository

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
