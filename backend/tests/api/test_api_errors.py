"""Tests for API error handling."""

from typing import Any, cast

from fastapi import HTTPException, status

from app.api.errors import domain_error_to_http_exception
from app.domain.errors import (
    ConflictError,
    DomainError,
    DomainValidationError,
    NotFoundError,
)


class TestDomainErrorToHttpException:
    """Tests for domain_error_to_http_exception function."""

    def test_not_found_error_maps_to_404(self):
        """Test that NotFoundError maps to HTTP 404."""
        error = NotFoundError("Satellite not found", {"satellite_id": "abc-123"})
        http_exc = domain_error_to_http_exception(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        detail = cast(dict[str, Any], http_exc.detail)
        assert detail["message"] == "Satellite not found"
        assert detail["details"]["satellite_id"] == "abc-123"

    def test_conflict_error_maps_to_409(self):
        """Test that ConflictError maps to HTTP 409."""
        error = ConflictError("Satellite name already exists", {"name": "TestSat"})
        http_exc = domain_error_to_http_exception(error)

        assert http_exc.status_code == status.HTTP_409_CONFLICT
        detail = cast(dict[str, Any], http_exc.detail)
        assert detail["message"] == "Satellite name already exists"
        assert detail["details"]["name"] == "TestSat"

    def test_validation_error_maps_to_422(self):
        """Test that DomainValidationError maps to HTTP 422."""
        error = DomainValidationError(
            "Invalid parameter range",
            {"field": "value", "constraint": "must be positive"},
        )
        http_exc = domain_error_to_http_exception(error)

        assert http_exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        detail = cast(dict[str, Any], http_exc.detail)
        assert detail["message"] == "Invalid parameter range"
        assert detail["details"]["field"] == "value"

    def test_generic_domain_error_maps_to_500(self):
        """Test that generic DomainError maps to HTTP 500."""
        error = DomainError("Unknown error occurred")
        http_exc = domain_error_to_http_exception(error)

        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = cast(dict[str, Any], http_exc.detail)
        assert detail["message"] == "Unknown error occurred"
        assert detail["details"] is None

    def test_error_without_details(self):
        """Test error conversion without additional details."""
        error = NotFoundError("Resource not found")
        http_exc = domain_error_to_http_exception(error)

        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        detail = cast(dict[str, Any], http_exc.detail)
        assert detail["message"] == "Resource not found"
        assert detail["details"] is None

    def test_error_with_empty_details(self):
        """Test error conversion with empty details dictionary."""
        error = ConflictError("Conflict occurred", details={})
        http_exc = domain_error_to_http_exception(error)

        assert http_exc.status_code == status.HTTP_409_CONFLICT
        detail = cast(dict[str, Any], http_exc.detail)
        assert detail["message"] == "Conflict occurred"
        assert detail["details"] == {}

    def test_error_with_complex_details(self):
        """Test error conversion with complex nested details."""
        details = {
            "field": "telemetry_data",
            "errors": [
                {"timestamp": "missing timezone"},
                {"value": "not a finite number"},
            ],
        }
        error = DomainValidationError("Multiple validation failures", details=details)
        http_exc = domain_error_to_http_exception(error)

        assert http_exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        detail = cast(dict[str, Any], http_exc.detail)
        assert detail["details"]["field"] == "telemetry_data"
        assert len(detail["details"]["errors"]) == 2
