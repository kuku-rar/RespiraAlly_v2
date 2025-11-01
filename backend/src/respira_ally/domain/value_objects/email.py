"""
EmailAddress Value Object
Domain Layer - Value Objects

Represents a validated email address following DDD principles.
Immutable and self-validating.
"""

import re
from typing import Any

from pydantic import BaseModel, field_validator


class EmailAddress(BaseModel):
    """
    Email address value object with format validation.

    **Invariants**:
    - Must be valid email format (xxx@xxx.xxx)
    - Case-insensitive comparison
    - Immutable after creation

    **Examples**:
        >>> email = EmailAddress(value="user@example.com")
        >>> email.value
        'user@example.com'

    **Raises**:
        ValueError: If email format is invalid
    """

    value: str

    class Config:
        frozen = True  # Immutable value object

    @field_validator("value")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """
        Validates email address format.

        Simple regex validation following RFC 5322 simplified pattern.
        Linus principle: Practicality over theoretical perfection.

        Args:
            v: Email address string

        Returns:
            Normalized email address (lowercase)

        Raises:
            ValueError: If email format is invalid
        """
        if not v or not v.strip():
            raise ValueError("Email address cannot be empty")

        # Normalize: strip whitespace and convert to lowercase
        normalized = v.strip().lower()

        # Simple but practical email regex
        # Matches: user@domain.tld
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, normalized):
            raise ValueError(
                f"Invalid email format: {v}. Expected format: user@domain.com"
            )

        return normalized

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"EmailAddress('{self.value}')"

    def __eq__(self, other: Any) -> bool:
        """
        Equality based on email value (case-insensitive).

        Value objects are equal if their values are equal.
        """
        if isinstance(other, EmailAddress):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        """Hash based on email value for use in sets/dicts."""
        return hash(self.value)
