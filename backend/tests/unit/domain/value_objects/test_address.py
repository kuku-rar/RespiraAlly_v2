"""
Unit tests for Address Value Object

Tests cover:
- Valid address formats
- Invalid address formats (empty, too short, too long)
- Normalization (whitespace trimming and collapsing)
- Immutability
- Equality and hashing
"""

import pytest
from pydantic import ValidationError

from respira_ally.domain.value_objects.address import Address


class TestAddressValidation:
    """Test address format validation."""

    def test_valid_address_simple(self):
        """Test valid simple address."""
        addr = Address(value="台北市大安區復興南路一段100號")
        assert addr.value == "台北市大安區復興南路一段100號"

    def test_valid_address_with_english(self):
        """Test valid address with English characters."""
        addr = Address(value="No. 100, Section 1, Fuxing S Rd, Da'an District, Taipei City")
        assert addr.value == "No. 100, Section 1, Fuxing S Rd, Da'an District, Taipei City"

    def test_valid_address_minimum_length(self):
        """Test valid address with minimum length (5 chars)."""
        addr = Address(value="台北市中山區")
        assert addr.value == "台北市中山區"

    def test_valid_address_maximum_length(self):
        """Test valid address with maximum length (200 chars)."""
        long_addr = "A" * 200
        addr = Address(value=long_addr)
        assert addr.value == long_addr

    def test_invalid_address_empty_string(self):
        """Test invalid empty address."""
        with pytest.raises(ValidationError) as exc_info:
            Address(value="")
        assert "Address cannot be empty" in str(exc_info.value)

    def test_invalid_address_whitespace_only(self):
        """Test invalid whitespace-only address."""
        with pytest.raises(ValidationError) as exc_info:
            Address(value="   ")
        assert "Address cannot be empty" in str(exc_info.value)

    def test_invalid_address_too_short(self):
        """Test invalid address too short (< 5 chars)."""
        with pytest.raises(ValidationError) as exc_info:
            Address(value="台北市")  # 3 chars
        assert "Address too short" in str(exc_info.value)
        assert "Minimum: 5 characters" in str(exc_info.value)

    def test_invalid_address_too_long(self):
        """Test invalid address too long (> 200 chars)."""
        long_addr = "A" * 201
        with pytest.raises(ValidationError) as exc_info:
            Address(value=long_addr)
        assert "Address too long" in str(exc_info.value)
        assert "Maximum: 200 characters" in str(exc_info.value)


class TestAddressNormalization:
    """Test address normalization."""

    def test_normalization_trim_whitespace(self):
        """Test leading/trailing whitespace is trimmed."""
        addr = Address(value="  台北市大安區復興南路一段100號  ")
        assert addr.value == "台北市大安區復興南路一段100號"

    def test_normalization_collapse_internal_whitespace(self):
        """Test internal whitespace is collapsed to single space."""
        addr = Address(value="台北市   大安區   復興南路   一段100號")
        assert addr.value == "台北市 大安區 復興南路 一段100號"

    def test_normalization_both(self):
        """Test both trimming and collapsing whitespace."""
        addr = Address(value="  台北市   大安區   復興南路   一段100號  ")
        assert addr.value == "台北市 大安區 復興南路 一段100號"

    def test_normalization_newlines_and_tabs(self):
        """Test newlines and tabs are normalized to spaces."""
        addr = Address(value="台北市\n大安區\t復興南路一段100號")
        assert addr.value == "台北市 大安區 復興南路一段100號"


class TestAddressImmutability:
    """Test address immutability (Value Object principle)."""

    def test_immutability_frozen(self):
        """Test Address is frozen (cannot be modified)."""
        addr = Address(value="台北市大安區復興南路一段100號")
        with pytest.raises(ValidationError):
            addr.value = "新北市板橋區中山路一段50號"


class TestAddressEquality:
    """Test address equality and hashing."""

    def test_equality_same_value(self):
        """Test two addresses with same value are equal."""
        addr1 = Address(value="台北市大安區復興南路一段100號")
        addr2 = Address(value="台北市大安區復興南路一段100號")
        assert addr1 == addr2

    def test_equality_after_normalization(self):
        """Test equality after whitespace normalization."""
        addr1 = Address(value="  台北市   大安區  ")
        addr2 = Address(value="台北市 大安區")
        assert addr1 == addr2

    def test_inequality_different_value(self):
        """Test two addresses with different values are not equal."""
        addr1 = Address(value="台北市大安區復興南路一段100號")
        addr2 = Address(value="新北市板橋區中山路一段50號")
        assert addr1 != addr2

    def test_hash_same_value(self):
        """Test addresses with same value have same hash."""
        addr1 = Address(value="台北市大安區復興南路一段100號")
        addr2 = Address(value="台北市大安區復興南路一段100號")
        assert hash(addr1) == hash(addr2)

    def test_hash_usable_in_set(self):
        """Test Address can be used in sets."""
        addr1 = Address(value="台北市大安區復興南路一段100號")
        addr2 = Address(value="台北市大安區復興南路一段100號")  # Same as addr1
        addr3 = Address(value="新北市板橋區中山路一段50號")

        addr_set = {addr1, addr2, addr3}
        assert len(addr_set) == 2  # addr1 and addr2 are duplicates


class TestAddressStringRepresentation:
    """Test address string representations."""

    def test_str_representation(self):
        """Test __str__ returns address value."""
        addr = Address(value="台北市大安區復興南路一段100號")
        assert str(addr) == "台北市大安區復興南路一段100號"

    def test_repr_representation(self):
        """Test __repr__ returns developer-friendly format."""
        addr = Address(value="台北市大安區復興南路一段100號")
        assert repr(addr) == "Address('台北市大安區復興南路一段100號')"
