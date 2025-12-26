"""Tests for domain errors."""

import pytest

from app.domain.errors import (
    ConflictError,
    DomainError,
    DomainValidationError,
    NotFoundError,
)


class TestDomainError:
    """Tests for base DomainError class."""

    def test_create_domain_error_with_message_only(self):
        """Test creating a domain error with only a message."""
        error = DomainError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.details is None
        assert str(error) == "Something went wrong"

    def test_create_domain_error_with_details(self):
        """Test creating a domain error with details."""
        details = {"field": "name", "value": "invalid"}
        error = DomainError("Validation failed", details=details)
        assert error.message == "Validation failed"
        assert error.details == details
        assert error.details["field"] == "name"

    def test_domain_error_is_exception(self):
        """Test that DomainError is a proper exception."""
        error = DomainError("Test error")
        assert isinstance(error, Exception)


class TestNotFoundError:
    """Tests for NotFoundError."""

    def test_create_not_found_error(self):
        """Test creating a not found error."""
        error = NotFoundError("Resource not found", {"resource_id": "123"})
        assert error.message == "Resource not found"
        assert error.details["resource_id"] == "123"
        assert isinstance(error, DomainError)

    def test_not_found_error_inheritance(self):
        """Test that NotFoundError inherits from DomainError."""
        error = NotFoundError("Not found")
        assert isinstance(error, NotFoundError)
        assert isinstance(error, DomainError)


class TestConflictError:
    """Tests for ConflictError."""

    def test_create_conflict_error(self):
        """Test creating a conflict error."""
        error = ConflictError("Resource already exists", {"name": "duplicate"})
        assert error.message == "Resource already exists"
        assert error.details["name"] == "duplicate"
        assert isinstance(error, DomainError)

    def test_conflict_error_inheritance(self):
        """Test that ConflictError inherits from DomainError."""
        error = ConflictError("Conflict")
        assert isinstance(error, ConflictError)
        assert isinstance(error, DomainError)


class TestDomainValidationError:
    """Tests for DomainValidationError."""

    def test_create_validation_error(self):
        """Test creating a validation error."""
        error = DomainValidationError("Invalid data", {"reason": "out of range"})
        assert error.message == "Invalid data"
        assert error.details["reason"] == "out of range"
        assert isinstance(error, DomainError)

    def test_validation_error_inheritance(self):
        """Test that DomainValidationError inherits from DomainError."""
        error = DomainValidationError("Invalid")
        assert isinstance(error, DomainValidationError)
        assert isinstance(error, DomainError)


class TestErrorRaising:
    """Tests for raising domain errors."""

    def test_raise_and_catch_not_found_error(self):
        """Test raising and catching NotFoundError."""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("Satellite not found")
        assert exc_info.value.message == "Satellite not found"

    def test_raise_and_catch_conflict_error(self):
        """Test raising and catching ConflictError."""
        with pytest.raises(ConflictError) as exc_info:
            raise ConflictError("Name already exists")
        assert exc_info.value.message == "Name already exists"

    def test_raise_and_catch_validation_error(self):
        """Test raising and catching DomainValidationError."""
        with pytest.raises(DomainValidationError) as exc_info:
            raise DomainValidationError("Invalid state")
        assert exc_info.value.message == "Invalid state"

    def test_catch_specific_error_as_domain_error(self):
        """Test catching specific error as base DomainError."""
        with pytest.raises(DomainError):
            raise NotFoundError("Not found")
