"""Domain-level exceptions."""

from typing import Any


class DomainError(Exception):
    """Base exception for all domain-level errors.

    All domain errors should inherit from this class to enable
    consistent error handling across the application.

    Attributes:
        message: Human-readable error message.
        details: Optional additional error context.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize domain error.

        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error context.
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class NotFoundError(DomainError):
    """Exception raised when a requested resource is not found.

    Use this when a query for a specific entity returns no results.
    Maps to HTTP 404 Not Found.
    """

    pass


class ConflictError(DomainError):
    """Exception raised when an operation conflicts with existing state.

    Use this for violations of uniqueness constraints or when an operation
    cannot be completed due to conflicting state.
    Maps to HTTP 409 Conflict.
    """

    pass


class DomainValidationError(DomainError):
    """Exception raised when domain validation rules are violated.

    Use this for business rule violations that go beyond simple
    data type validation.
    Maps to HTTP 422 Unprocessable Entity.
    """

    pass
