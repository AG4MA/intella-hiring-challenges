"""Parameter service with business logic."""

from uuid import UUID

from app.domain.errors import NotFoundError
from app.domain.models import Parameter
from app.storage.base import ParameterRepository, UnitRepository


class ParameterService:
    """Service for parameter business logic."""

    def __init__(
        self,
        parameter_repository: ParameterRepository,
        unit_repository: UnitRepository,
    ) -> None:
        """Initialize the service.

        Args:
            parameter_repository: The parameter repository.
            unit_repository: The unit repository.
        """
        self._repo = parameter_repository
        self._unit_repo = unit_repository

    def create(self, parameter: Parameter) -> Parameter:
        """Create a new parameter.

        Args:
            parameter: The parameter to create.

        Returns:
            The created parameter.

        Raises:
            NotFoundError: If parent unit does not exist.
            ConflictError: If parameter with same ID already exists.
        """
        # Check unit exists
        unit = self._unit_repo.get(parameter.unit_id)
        if unit is None:
            raise NotFoundError(
                "Parent unit not found",
                {"unit_id": str(parameter.unit_id)},
            )

        return self._repo.add(parameter)

    def get(self, parameter_id: UUID) -> Parameter:
        """Get a parameter by ID.

        Args:
            parameter_id: The parameter ID.

        Returns:
            The parameter.

        Raises:
            NotFoundError: If parameter not found.
        """
        parameter = self._repo.get(parameter_id)
        if parameter is None:
            raise NotFoundError(
                "Parameter not found",
                {"parameter_id": str(parameter_id)},
            )
        return parameter

    def list_by_unit(self, unit_id: UUID) -> list[Parameter]:
        """List all parameters for a unit.

        Args:
            unit_id: The unit ID.

        Returns:
            List of parameters for the unit.
        """
        return self._repo.get_by_unit(unit_id)

    def update(
        self,
        parameter_id: UUID,
        name: str | None = None,
        unit_of_measurement: str | None = None,
    ) -> Parameter:
        """Update a parameter.

        Args:
            parameter_id: The parameter ID.
            name: New name (optional).
            unit_of_measurement: New unit of measurement (optional).

        Returns:
            The updated parameter.

        Raises:
            NotFoundError: If parameter not found.
        """
        parameter = self.get(parameter_id)

        if name is not None:
            parameter.name = name
        if unit_of_measurement is not None:
            parameter.unit_of_measurement = unit_of_measurement

        return parameter

    def activate(self, parameter_id: UUID) -> Parameter:
        """Activate a parameter.

        Args:
            parameter_id: The parameter ID.

        Returns:
            The activated parameter.

        Raises:
            NotFoundError: If parameter not found.
        """
        parameter = self.get(parameter_id)
        parameter.is_active = True
        return parameter

    def deactivate(self, parameter_id: UUID) -> Parameter:
        """Deactivate a parameter.

        Args:
            parameter_id: The parameter ID.

        Returns:
            The deactivated parameter.

        Raises:
            NotFoundError: If parameter not found.
        """
        parameter = self.get(parameter_id)
        parameter.is_active = False
        return parameter

    def delete(self, parameter_id: UUID) -> None:
        """Delete a parameter.

        Args:
            parameter_id: The parameter ID.

        Raises:
            NotFoundError: If parameter not found.
        """
        if not self._repo.delete(parameter_id):
            raise NotFoundError(
                "Parameter not found",
                {"parameter_id": str(parameter_id)},
            )
