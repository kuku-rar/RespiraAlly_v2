"""
Unit tests for EmailAddress Value Object

Tests cover:
- Valid email formats
- Invalid email formats
- Normalization (lowercase, whitespace trimming)
- Immutability
- Equality and hashing
"""

import pytest
from pydantic import ValidationError

from respira_ally.domain.value_objects.email import EmailAddress


class TestEmailAddressValidation:
    """Test email address format validation."""

    def test_valid_email_simple(self):
        """Test valid simple email address."""
        email = EmailAddress(value="user@example.com")
        assert email.value == "user@example.com"

    def test_valid_email_with_subdomain(self):
        """Test valid email with subdomain."""
        email = EmailAddress(value="user@mail.example.com")
        assert email.value == "user@mail.example.com"

    def test_valid_email_with_plus(self):
        """Test valid email with plus sign."""
        email = EmailAddress(value="user+tag@example.com")
        assert email.value == "user+tag@example.com"

    def test_valid_email_with_dots(self):
        """Test valid email with dots in local part."""
        email = EmailAddress(value="user.name@example.com")
        assert email.value == "user.name@example.com"

    def test_invalid_email_no_at_sign(self):
        """Test invalid email without @ sign."""
        with pytest.raises(ValidationError) as exc_info:
            EmailAddress(value="userexample.com")
        assert "Invalid email format" in str(exc_info.value)

    def test_invalid_email_no_domain(self):
        """Test invalid email without domain."""
        with pytest.raises(ValidationError) as exc_info:
            EmailAddress(value="user@")
        assert "Invalid email format" in str(exc_info.value)

    def test_invalid_email_no_local_part(self):
        """Test invalid email without local part."""
        with pytest.raises(ValidationError) as exc_info:
            EmailAddress(value="@example.com")
        assert "Invalid email format" in str(exc_info.value)

    def test_invalid_email_empty_string(self):
        """Test invalid empty email."""
        with pytest.raises(ValidationError) as exc_info:
            EmailAddress(value="")
        assert "Email address cannot be empty" in str(exc_info.value)

    def test_invalid_email_whitespace_only(self):
        """Test invalid whitespace-only email."""
        with pytest.raises(ValidationError) as exc_info:
            EmailAddress(value="   ")
        assert "Email address cannot be empty" in str(exc_info.value)


class TestEmailAddressNormalization:
    """Test email address normalization."""

    def test_normalization_lowercase(self):
        """Test email is converted to lowercase."""
        email = EmailAddress(value="User@Example.COM")
        assert email.value == "user@example.com"

    def test_normalization_trim_whitespace(self):
        """Test leading/trailing whitespace is trimmed."""
        email = EmailAddress(value="  user@example.com  ")
        assert email.value == "user@example.com"

    def test_normalization_both(self):
        """Test both lowercase and whitespace normalization."""
        email = EmailAddress(value="  User@Example.COM  ")
        assert email.value == "user@example.com"


class TestEmailAddressImmutability:
    """Test email address immutability (Value Object principle)."""

    def test_immutability_frozen(self):
        """Test EmailAddress is frozen (cannot be modified)."""
        email = EmailAddress(value="user@example.com")
        with pytest.raises(ValidationError):
            email.value = "new@example.com"


class TestEmailAddressEquality:
    """Test email address equality and hashing."""

    def test_equality_same_value(self):
        """Test two emails with same value are equal."""
        email1 = EmailAddress(value="user@example.com")
        email2 = EmailAddress(value="user@example.com")
        assert email1 == email2

    def test_equality_case_insensitive(self):
        """Test equality is case-insensitive (normalized)."""
        email1 = EmailAddress(value="User@Example.COM")
        email2 = EmailAddress(value="user@example.com")
        assert email1 == email2

    def test_inequality_different_value(self):
        """Test two emails with different values are not equal."""
        email1 = EmailAddress(value="user1@example.com")
        email2 = EmailAddress(value="user2@example.com")
        assert email1 != email2

    def test_hash_same_value(self):
        """Test emails with same value have same hash."""
        email1 = EmailAddress(value="user@example.com")
        email2 = EmailAddress(value="user@example.com")
        assert hash(email1) == hash(email2)

    def test_hash_usable_in_set(self):
        """Test EmailAddress can be used in sets."""
        email1 = EmailAddress(value="user@example.com")
        email2 = EmailAddress(value="user@example.com")
        email3 = EmailAddress(value="other@example.com")

        email_set = {email1, email2, email3}
        assert len(email_set) == 2  # email1 and email2 are duplicates


class TestEmailAddressStringRepresentation:
    """Test email address string representations."""

    def test_str_representation(self):
        """Test __str__ returns email value."""
        email = EmailAddress(value="user@example.com")
        assert str(email) == "user@example.com"

    def test_repr_representation(self):
        """Test __repr__ returns developer-friendly format."""
        email = EmailAddress(value="user@example.com")
        assert repr(email) == "EmailAddress('user@example.com')"
