
import datetime
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from respira_ally.domain.exceptions import BusinessRuleViolationError
from respira_ally.domain.value_objects import Address, PhoneNumber


@dataclass
class Patient:
    """
    Patient Aggregate Root

    This entity encapsulates the core data and business rules for a patient.
    It is the consistency boundary for all patient-related operations.
    """

    user_id: UUID
    therapist_id: UUID
    name: str
    birth_date: datetime.date
    gender: Literal["MALE", "FEMALE", "OTHER"]
    height_cm: Decimal
    weight_kg: Decimal
    phone_number: PhoneNumber  # Value Object with validation
    address: Optional[Address] = None  # Optional Value Object
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        self._validate()

    @property
    def age(self) -> int:
        """Calculates age based on birth date."""
        today = datetime.date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    @property
    def bmi(self) -> Decimal:
        """
        Calculates Body Mass Index (BMI).

        Formula: weight (kg) / [height (m)]^2
        Returns BMI as a Decimal, rounded to one decimal place.
        This ensures the value is always a number, not a string.
        """
        if self.height_cm <= 0:
            return Decimal("0.0")
        height_m = self.height_cm / Decimal("100")
        bmi_value = self.weight_kg / (height_m * height_m)
        return round(bmi_value, 1)

    def update_profile(self, **kwargs):
        """
        Updates patient profile attributes and enforces validation rules.
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        
        self.updated_at = datetime.datetime.now()
        self._validate()

    def _validate(self):
        """
        Enforces business rules and invariants for the Patient aggregate.

        Invariants (Linus "Good Taste" - eliminate edge cases):
        1. Patient name must be non-empty and <= 100 chars
        2. Gender must be valid enum value (MALE/FEMALE/OTHER)
        3. Height and weight must be positive
        4. Birth date cannot be in the future
        5. Phone number must be valid (validated by PhoneNumber Value Object)
        6. Address is optional but must be valid if provided (validated by Address Value Object)
        7. IDs (user_id, therapist_id) must exist

        Raises:
            BusinessRuleViolationError: If any invariant is violated
        """
        # Invariant 1: Name validation
        if not self.name or not self.name.strip():
            raise BusinessRuleViolationError("Patient name cannot be empty.")
        if len(self.name) > 100:
            raise BusinessRuleViolationError("Patient name cannot exceed 100 characters.")

        # Invariant 2: Gender validation
        valid_genders = {"MALE", "FEMALE", "OTHER"}
        if self.gender not in valid_genders:
            raise BusinessRuleViolationError(
                f"Gender must be one of {valid_genders}, got: {self.gender}"
            )

        # Invariant 3: Height and weight must be positive
        if self.height_cm <= 0 or self.weight_kg <= 0:
            raise BusinessRuleViolationError("Height and weight must be positive values.")

        # Invariant 4: Birth date validation
        if self.birth_date > datetime.date.today():
            raise BusinessRuleViolationError("Birth date cannot be in the future.")

        # Invariant 5: Phone number validation (enforced by PhoneNumber Value Object)
        if not self.phone_number:
            raise BusinessRuleViolationError("Phone number is required.")
        # Note: Format validation is handled by PhoneNumber Value Object automatically

        # Invariant 6: Address validation (optional, validated by Address Value Object if provided)
        # No validation needed here - Address Value Object handles it

        # Invariant 7: ID validation (basic existence check)
        if not self.user_id:
            raise BusinessRuleViolationError("User ID is required.")
        if not self.therapist_id:
            raise BusinessRuleViolationError("Therapist ID is required.")

