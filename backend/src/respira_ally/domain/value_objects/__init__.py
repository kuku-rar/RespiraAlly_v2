"""
Domain Value Objects

Value Objects are immutable objects that represent descriptive aspects of the domain
with no conceptual identity. They are defined only by their attributes.

**DDD Principles**:
- Immutable (frozen=True)
- Self-validating
- Value-based equality
- No identity

**Available Value Objects**:
- EmailAddress: Validated email address
- PhoneNumber: Validated Taiwan phone number
- Address: Validated address string
"""

from respira_ally.domain.value_objects.address import Address
from respira_ally.domain.value_objects.email import EmailAddress
from respira_ally.domain.value_objects.phone_number import PhoneNumber

__all__ = [
    "EmailAddress",
    "PhoneNumber",
    "Address",
]
