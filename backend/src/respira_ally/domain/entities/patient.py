"""
Patient Domain Entity
Domain Layer - Clean Architecture

Pure domain entity with zero infrastructure dependencies.
This represents the core Patient business concept.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class Patient:
    """
    Patient Domain Entity

    Pure business entity representing a patient in the COPD management system.
    This entity contains no database-specific logic or infrastructure dependencies.

    Attributes:
        user_id: Unique identifier (also serves as FK to User)
        therapist_id: Assigned therapist's user ID
        name: Patient's full name
        birth_date: Date of birth
        gender: Gender (MALE, FEMALE, OTHER)
        hospital_medical_record_number: Hospital MRN for integration
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        smoking_status: Smoking status (NEVER, FORMER, CURRENT)
        smoking_years: Years of smoking history
        exacerbation_count_last_12m: Number of exacerbations in last 12 months
        hospitalization_count_last_12m: Number of hospitalizations in last 12 months
        last_exacerbation_date: Date of last exacerbation
        medical_history: Medical history data (dict)
        contact_info: Contact information (dict)
    """

    user_id: UUID
    name: str
    birth_date: date
    therapist_id: UUID | None = None
    gender: str | None = None
    hospital_medical_record_number: str | None = None
    height_cm: int | None = None
    weight_kg: Decimal | None = None
    smoking_status: str | None = None
    smoking_years: int | None = None
    exacerbation_count_last_12m: int = 0
    hospitalization_count_last_12m: int = 0
    last_exacerbation_date: date | None = None
    medical_history: dict = field(default_factory=dict)
    contact_info: dict = field(default_factory=dict)

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def calculate_age(self) -> int:
        """
        Calculate current age from birth date

        Returns:
            Age in years
        """
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def calculate_bmi(self) -> Decimal | None:
        """
        Calculate Body Mass Index (BMI)

        Formula: BMI = weight(kg) / height(m)^2

        Returns:
            BMI value (rounded to 1 decimal) or None if data insufficient
        """
        if not self.weight_kg or not self.height_cm:
            return None

        height_m = Decimal(self.height_cm) / Decimal(100)
        bmi = self.weight_kg / (height_m * height_m)
        return round(bmi, 1)

    def is_current_smoker(self) -> bool:
        """
        Check if patient is currently smoking

        Returns:
            True if smoking_status is CURRENT
        """
        return self.smoking_status == "CURRENT"

    def is_former_smoker(self) -> bool:
        """
        Check if patient is a former smoker

        Returns:
            True if smoking_status is FORMER
        """
        return self.smoking_status == "FORMER"

    def has_smoking_history(self) -> bool:
        """
        Check if patient has any smoking history

        Returns:
            True if patient has ever smoked (CURRENT or FORMER)
        """
        return self.smoking_status in ("CURRENT", "FORMER")

    def has_recent_exacerbation(self) -> bool:
        """
        Check if patient had exacerbation in last 12 months

        Returns:
            True if exacerbation_count_last_12m > 0
        """
        return self.exacerbation_count_last_12m > 0

    def has_frequent_exacerbations(self) -> bool:
        """
        Check if patient has frequent exacerbations (>=2 in last 12 months)

        This is a GOLD guideline criteria for COPD severity assessment.

        Returns:
            True if exacerbation_count_last_12m >= 2
        """
        return self.exacerbation_count_last_12m >= 2

    def requires_hospitalization_followup(self) -> bool:
        """
        Check if patient requires hospitalization follow-up

        Patients with recent hospitalizations need closer monitoring.

        Returns:
            True if hospitalization_count_last_12m > 0
        """
        return self.hospitalization_count_last_12m > 0

    def is_high_risk_patient(self) -> bool:
        """
        Identify high-risk patients based on exacerbation/hospitalization history

        High-risk patients require more intensive monitoring and intervention.

        Returns:
            True if patient has >=2 exacerbations OR >=1 hospitalization in last 12 months
        """
        return self.has_frequent_exacerbations() or self.requires_hospitalization_followup()

    def get_pack_years(self) -> Decimal | None:
        """
        Calculate pack-years for smoking history

        Pack-years = (packs per day) x (years smoked)
        Assumes 1 pack = 20 cigarettes, average 1 pack/day

        Returns:
            Estimated pack-years or None if smoking_years not available
        """
        if not self.smoking_years or not self.has_smoking_history():
            return None

        # Simplified calculation: assume 1 pack/day average
        return Decimal(self.smoking_years)

    def __repr__(self) -> str:
        return f"<Patient(user_id={self.user_id}, name={self.name})>"
