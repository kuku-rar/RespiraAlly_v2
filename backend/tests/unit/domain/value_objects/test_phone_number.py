"""
Unit tests for PhoneNumber Value Object

Tests cover:
- Valid Taiwan phone number formats
- Invalid phone number formats
- Normalization (remove separators, handle international format)
- Immutability
- Equality and hashing
- Formatted output
"""

import pytest
from pydantic import ValidationError

from respira_ally.domain.value_objects.phone_number import PhoneNumber


class TestPhoneNumberValidation:
    """Test phone number format validation."""

    def test_valid_phone_simple(self):
        """Test valid simple format: 09XXXXXXXX"""
        phone = PhoneNumber(value="0912345678")
        assert phone.value == "0912345678"

    def test_valid_phone_with_hyphens(self):
        """Test valid format with hyphens: 09XX-XXX-XXX"""
        phone = PhoneNumber(value="0912-345-678")
        assert phone.value == "0912345678"  # Normalized

    def test_valid_phone_with_spaces(self):
        """Test valid format with spaces: 09XX XXX XXX"""
        phone = PhoneNumber(value="0912 345 678")
        assert phone.value == "0912345678"  # Normalized

    def test_valid_phone_international_plus(self):
        """Test valid international format: +886-9XX-XXX-XXX"""
        phone = PhoneNumber(value="+886-912-345-678")
        assert phone.value == "0912345678"  # Normalized to Taiwan format

    def test_valid_phone_international_no_plus(self):
        """Test valid international format without plus: 886-9XX-XXX-XXX"""
        phone = PhoneNumber(value="886-912-345-678")
        assert phone.value == "0912345678"  # Normalized

    def test_invalid_phone_too_short(self):
        """Test invalid phone number too short."""
        with pytest.raises(ValidationError) as exc_info:
            PhoneNumber(value="091234567")  # 9 digits instead of 10
        assert "Invalid Taiwan phone number" in str(exc_info.value)

    def test_invalid_phone_too_long(self):
        """Test invalid phone number too long."""
        with pytest.raises(ValidationError) as exc_info:
            PhoneNumber(value="09123456789")  # 11 digits
        assert "Invalid Taiwan phone number" in str(exc_info.value)

    def test_invalid_phone_wrong_prefix(self):
        """Test invalid phone number with wrong prefix (not starting with 09)."""
        with pytest.raises(ValidationError) as exc_info:
            PhoneNumber(value="0812345678")  # Starts with 08 instead of 09
        assert "Invalid Taiwan phone number" in str(exc_info.value)

    def test_invalid_phone_empty_string(self):
        """Test invalid empty phone number."""
        with pytest.raises(ValidationError) as exc_info:
            PhoneNumber(value="")
        assert "Phone number cannot be empty" in str(exc_info.value)

    def test_invalid_phone_whitespace_only(self):
        """Test invalid whitespace-only phone number."""
        with pytest.raises(ValidationError) as exc_info:
            PhoneNumber(value="   ")
        assert "Phone number cannot be empty" in str(exc_info.value)

    def test_invalid_phone_contains_letters(self):
        """Test invalid phone number with letters."""
        with pytest.raises(ValidationError) as exc_info:
            PhoneNumber(value="091234abcd")
        assert "Invalid Taiwan phone number" in str(exc_info.value)


class TestPhoneNumberNormalization:
    """Test phone number normalization."""

    def test_normalization_remove_hyphens(self):
        """Test hyphens are removed during normalization."""
        phone = PhoneNumber(value="0912-345-678")
        assert phone.value == "0912345678"

    def test_normalization_remove_spaces(self):
        """Test spaces are removed during normalization."""
        phone = PhoneNumber(value="0912 345 678")
        assert phone.value == "0912345678"

    def test_normalization_remove_parentheses(self):
        """Test parentheses are removed during normalization."""
        phone = PhoneNumber(value="(0912) 345-678")
        assert phone.value == "0912345678"

    def test_normalization_international_to_local(self):
        """Test international format is normalized to Taiwan format."""
        phone = PhoneNumber(value="+886-912-345-678")
        assert phone.value == "0912345678"


class TestPhoneNumberFormatting:
    """Test phone number formatted output."""

    def test_formatted_property(self):
        """Test formatted property returns 09XX-XXX-XXX format."""
        phone = PhoneNumber(value="0912345678")
        assert phone.formatted == "0912-345-678"

    def test_international_property(self):
        """Test international property returns +886-9XX-XXX-XXX format."""
        phone = PhoneNumber(value="0912345678")
        assert phone.international == "+886-912-345-678"

    def test_str_returns_formatted(self):
        """Test __str__ returns formatted version."""
        phone = PhoneNumber(value="0912345678")
        assert str(phone) == "0912-345-678"


class TestPhoneNumberImmutability:
    """Test phone number immutability (Value Object principle)."""

    def test_immutability_frozen(self):
        """Test PhoneNumber is frozen (cannot be modified)."""
        phone = PhoneNumber(value="0912345678")
        with pytest.raises(ValidationError):
            phone.value = "0987654321"


class TestPhoneNumberEquality:
    """Test phone number equality and hashing."""

    def test_equality_same_value(self):
        """Test two phone numbers with same value are equal."""
        phone1 = PhoneNumber(value="0912345678")
        phone2 = PhoneNumber(value="0912345678")
        assert phone1 == phone2

    def test_equality_normalized(self):
        """Test equality after normalization."""
        phone1 = PhoneNumber(value="0912-345-678")
        phone2 = PhoneNumber(value="0912345678")
        assert phone1 == phone2

    def test_equality_international_vs_local(self):
        """Test equality between international and local formats."""
        phone1 = PhoneNumber(value="+886-912-345-678")
        phone2 = PhoneNumber(value="0912345678")
        assert phone1 == phone2

    def test_inequality_different_value(self):
        """Test two phone numbers with different values are not equal."""
        phone1 = PhoneNumber(value="0912345678")
        phone2 = PhoneNumber(value="0987654321")
        assert phone1 != phone2

    def test_hash_same_value(self):
        """Test phone numbers with same value have same hash."""
        phone1 = PhoneNumber(value="0912345678")
        phone2 = PhoneNumber(value="0912-345-678")
        assert hash(phone1) == hash(phone2)

    def test_hash_usable_in_set(self):
        """Test PhoneNumber can be used in sets."""
        phone1 = PhoneNumber(value="0912345678")
        phone2 = PhoneNumber(value="0912-345-678")  # Same as phone1 after normalization
        phone3 = PhoneNumber(value="0987654321")

        phone_set = {phone1, phone2, phone3}
        assert len(phone_set) == 2  # phone1 and phone2 are duplicates


class TestPhoneNumberStringRepresentation:
    """Test phone number string representations."""

    def test_str_representation(self):
        """Test __str__ returns formatted phone number."""
        phone = PhoneNumber(value="0912345678")
        assert str(phone) == "0912-345-678"

    def test_repr_representation(self):
        """Test __repr__ returns developer-friendly format."""
        phone = PhoneNumber(value="0912345678")
        assert repr(phone) == "PhoneNumber('0912345678')"
