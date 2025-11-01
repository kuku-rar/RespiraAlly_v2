"""
PhoneNumber Value Object
Domain Layer - Value Objects

Represents a validated phone number (Taiwan format) following DDD principles.
Immutable and self-validating.
"""

import re
from typing import Any

from pydantic import BaseModel, field_validator


class PhoneNumber(BaseModel):
    """
    Phone number value object with Taiwan format validation.

    **Supported Formats**:
    - Taiwan mobile: 09XX-XXX-XXX or 09XXXXXXXX
    - International: +886-9XX-XXX-XXX or +886-9XXXXXXXX

    **Invariants**:
    - Must be valid Taiwan phone number format
    - Normalized to 09XXXXXXXX format (10 digits)
    - Immutable after creation

    **Examples**:
        >>> phone = PhoneNumber(value="0912-345-678")
        >>> phone.value
        '0912345678'
        >>> phone.formatted
        '0912-345-678'

    **Raises**:
        ValueError: If phone number format is invalid
    """

    value: str  # Normalized format: 09XXXXXXXX

    class Config:
        frozen = True  # Immutable value object

    @field_validator("value")
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        """
        Validates and normalizes Taiwan phone number.

        Linus principle: Handle common cases, reject invalid input clearly.

        Supported inputs:
        - 09XX-XXX-XXX
        - 09XXXXXXXX
        - +886-9XX-XXX-XXX
        - +886-9XXXXXXXX

        Args:
            v: Phone number string

        Returns:
            Normalized phone number (09XXXXXXXX format)

        Raises:
            ValueError: If phone number format is invalid
        """
        if not v or not v.strip():
            raise ValueError("Phone number cannot be empty")

        # Remove common separators: spaces, hyphens, parentheses
        cleaned = re.sub(r"[\s\-()]", "", v.strip())

        # Handle international format (+886)
        if cleaned.startswith("+886"):
            cleaned = "0" + cleaned[4:]  # +886-9XX -> 09XX
        elif cleaned.startswith("886"):
            cleaned = "0" + cleaned[3:]  # 886-9XX -> 09XX

        # Validate Taiwan mobile format: 09XXXXXXXX (10 digits starting with 09)
        if not re.match(r"^09\d{8}$", cleaned):
            raise ValueError(
                f"Invalid Taiwan phone number: {v}. "
                f"Expected format: 09XX-XXX-XXX or +886-9XX-XXX-XXX"
            )

        return cleaned

    @property
    def formatted(self) -> str:
        """
        Returns formatted phone number: 09XX-XXX-XXX

        Returns:
            Formatted phone number string
        """
        return f"{self.value[:4]}-{self.value[4:7]}-{self.value[7:]}"

    @property
    def international(self) -> str:
        """
        Returns international format: +886-9XX-XXX-XXX

        Returns:
            International format phone number
        """
        return f"+886-{self.value[1:4]}-{self.value[4:7]}-{self.value[7:]}"

    def __str__(self) -> str:
        """String representation (formatted)."""
        return self.formatted

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"PhoneNumber('{self.value}')"

    def __eq__(self, other: Any) -> bool:
        """
        Equality based on normalized phone number.

        Value objects are equal if their values are equal.
        """
        if isinstance(other, PhoneNumber):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        """Hash based on phone number value for use in sets/dicts."""
        return hash(self.value)
