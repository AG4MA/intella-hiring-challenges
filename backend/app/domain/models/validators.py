"""Shared validators for domain models."""

import math
from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator, Field


def validate_non_empty_string(value: str) -> str:
    """Validate that a string is not empty or whitespace-only.

    Args:
        value: The string to validate.

    Returns:
        The stripped string value.

    Raises:
        ValueError: If the string is empty or contains only whitespace.
    """
    stripped = value.strip()
    if not stripped:
        raise ValueError("String must not be empty or whitespace-only")
    return stripped


def validate_utc_timestamp(value: datetime) -> datetime:
    """Validate that a datetime has UTC timezone info.

    Args:
        value: The datetime to validate.

    Returns:
        The validated datetime.

    Raises:
        ValueError: If the datetime is naive or not in UTC.
    """
    if value.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")
    if value.utcoffset() != timezone.utc.utcoffset(None):
        raise ValueError("Timestamp must be in UTC timezone")
    return value


def validate_finite_float(value: float) -> float:
    """Validate that a float is finite (not NaN or Inf).

    Args:
        value: The float to validate.

    Returns:
        The validated float value.

    Raises:
        ValueError: If the value is NaN or infinite.
    """
    if math.isnan(value) or math.isinf(value):
        raise ValueError("Value must be a finite number (not NaN or Inf)")
    return value


# Type aliases for annotated validated types
NonEmptyStr = Annotated[str, AfterValidator(validate_non_empty_string)]
UtcDatetime = Annotated[datetime, AfterValidator(validate_utc_timestamp)]
FiniteFloat = Annotated[float, AfterValidator(validate_finite_float)]

# UUID4 field with default factory
Uuid4Field = Field(default_factory=lambda: __import__("uuid").uuid4())
