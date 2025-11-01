"""
Address Value Object
Domain Layer - Value Objects

Represents a validated address following DDD principles.
Immutable and self-validating.

Note: Current implementation uses simple string format.
Future enhancement: Structured address (city, district, street, etc.)
"""

from typing import Any

from pydantic import BaseModel, field_validator


class Address(BaseModel):
    """
    Address value object with basic validation.

    **Invariants**:
    - Must be non-empty
    - Maximum 200 characters
    - Whitespace normalized
    - Immutable after creation

    **Examples**:
        >>> addr = Address(value="台北市大安區復興南路一段100號")
        >>> addr.value
        '台北市大安區復興南路一段100號'

    **Future Enhancement**:
        Structured format: {city, district, street, building}
        Taiwan postal code validation
        Google Maps API integration

    **Raises**:
        ValueError: If address is invalid
    """

    value: str

    class Config:
        frozen = True  # Immutable value object

    @field_validator("value")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """
        Validates address format.

        Linus principle: Simple validation, clear errors.

        Rules:
        1. Non-empty
        2. Max 200 characters (practical limit)
        3. Whitespace normalized

        Args:
            v: Address string

        Returns:
            Normalized address (trimmed whitespace)

        Raises:
            ValueError: If address is invalid
        """
        if not v or not v.strip():
            raise ValueError("Address cannot be empty")

        # Normalize: strip leading/trailing whitespace, collapse internal whitespace
        normalized = " ".join(v.strip().split())

        # Length validation
        if len(normalized) > 200:
            raise ValueError(
                f"Address too long: {len(normalized)} characters. Maximum: 200 characters."
            )

        # Minimum length (at least 5 characters for meaningful address)
        if len(normalized) < 5:
            raise ValueError(
                f"Address too short: {len(normalized)} characters. Minimum: 5 characters."
            )

        return normalized

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Address('{self.value}')"

    def __eq__(self, other: Any) -> bool:
        """
        Equality based on address value.

        Value objects are equal if their values are equal.
        """
        if isinstance(other, Address):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        """Hash based on address value for use in sets/dicts."""
        return hash(self.value)
