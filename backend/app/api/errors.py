"""HTTP error handling utilities for mapping domain errors to HTTP responses."""

from typing import Any

from fastapi import HTTPException, status

from app.domain.errors import (
    ConflictError,
    DomainError,
    DomainValidationError,
    NotFoundError,
)


def domain_error_to_http_exception(error: DomainError) -> HTTPException:
    """Map a domain error to an appropriate HTTP exception.

    Args:
        error: The domain error to convert.

    Returns:
        HTTPException with appropriate status code and detail.

    Examples:
        >>> error = NotFoundError("Satellite not found", {"id": "123"})
        >>> http_exc = domain_error_to_http_exception(error)
        >>> http_exc.status_code
        404
    """
    status_code = _get_status_code_for_error(error)
    detail = _format_error_detail(error)

    return HTTPException(status_code=status_code, detail=detail)


def _get_status_code_for_error(error: DomainError) -> int:
    """Get the appropriate HTTP status code for a domain error.

    Args:
        error: The domain error.

    Returns:
        HTTP status code as integer.
    """
    error_status_map = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        DomainValidationError: 422,
    }
    for error_type, status_code in error_status_map.items():
        if isinstance(error, error_type):
            return status_code

    # Default to 500 for unknown domain errors
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _format_error_detail(error: DomainError) -> dict[str, Any]:
    """Format error detail for HTTP response.

    Args:
        error: The domain error.

    Returns:
        Dictionary with error message and optional details.
    """
    detail: dict[str, Any] = {
        "message": error.message,
        "details": error.details,
    }
    return detail
