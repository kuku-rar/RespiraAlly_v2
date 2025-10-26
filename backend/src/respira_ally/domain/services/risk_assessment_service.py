"""
Risk Assessment Domain Service
Domain Layer - Clean Architecture

Pure business logic for COPD risk assessment using GOLD ABE classification.
No infrastructure dependencies (database, external APIs, etc.)

Following Linus Torvalds' "Good Taste" principles:
1. Simple data structures that eliminate special cases
2. Pure functions with no side effects
3. Clear separation between "what" (business rules) and "how" (implementation)

ADR References:
- ADR-013 v2.0: GOLD ABE Classification
- ADR-014: Hybrid Strategy (backward compatibility with legacy risk_score/risk_level)
"""

from dataclasses import dataclass
from typing import Literal

# Type aliases for domain concepts
GoldGroup = Literal["A", "B", "E"]
RiskLevel = Literal["low", "medium", "high", "critical"]


@dataclass(frozen=True)
class RiskAssessmentInput:
    """
    Input data for risk assessment calculation

    Immutable data structure - following functional programming principles.
    "Good programmers worry about data structures" - Linus Torvalds

    Attributes:
        cat_score: CAT (COPD Assessment Test) score (0-40)
        mmrc_grade: mMRC (Modified Medical Research Council) grade (0-4)
        exacerbation_count_12m: Number of exacerbations in last 12 months
        hospitalization_count_12m: Number of hospitalizations in last 12 months
    """
    cat_score: int
    mmrc_grade: int
    exacerbation_count_12m: int
    hospitalization_count_12m: int

    def __post_init__(self) -> None:
        """Validate input data ranges"""
        if not (0 <= self.cat_score <= 40):
            raise ValueError(f"CAT score must be 0-40, got {self.cat_score}")
        if not (0 <= self.mmrc_grade <= 4):
            raise ValueError(f"mMRC grade must be 0-4, got {self.mmrc_grade}")
        if self.exacerbation_count_12m < 0:
            raise ValueError(f"Exacerbation count cannot be negative, got {self.exacerbation_count_12m}")
        if self.hospitalization_count_12m < 0:
            raise ValueError(f"Hospitalization count cannot be negative, got {self.hospitalization_count_12m}")


@dataclass(frozen=True)
class RiskAssessmentResult:
    """
    Result of risk assessment calculation

    Immutable data structure containing both GOLD ABE classification
    and legacy risk scoring (for backward compatibility).

    Attributes:
        gold_group: GOLD ABE group classification ('A', 'B', or 'E')
        risk_score: Legacy numeric risk score (0-100)
        risk_level: Legacy risk level category
        reasoning: Human-readable explanation of classification
    """
    gold_group: GoldGroup
    risk_score: int
    risk_level: RiskLevel
    reasoning: str


class RiskAssessmentService:
    """
    Domain Service for COPD risk assessment using GOLD ABE classification

    Pure business logic - no database, no external APIs, no side effects.
    This is what Domain-Driven Design is about: encapsulating domain knowledge.

    GOLD ABE Classification Logic (GOLD 2011):
    - Group A (Low Risk): CAT<10 AND mMRC<2
    - Group B (Medium Risk): CAT>=10 OR mMRC>=2 (but not both)
    - Group E (High Risk): CAT>=10 AND mMRC>=2

    Design Philosophy (Linus-approved):
    "Bad programmers worry about the code. Good programmers worry about
    data structures and their relationships."

    This service has:
    1. Clear input/output data structures (RiskAssessmentInput/Result)
    2. No special cases - pure business rules
    3. No hidden dependencies - stateless pure functions
    4. Testable without mocks - just pass data, get data back
    """

    def calculate_risk(self, input_data: RiskAssessmentInput) -> RiskAssessmentResult:
        """
        Calculate COPD risk assessment based on GOLD ABE classification

        Pure function: Same input always produces same output.
        No side effects: No database writes, no API calls, no logging.

        Args:
            input_data: Risk assessment input parameters

        Returns:
            Risk assessment result with GOLD group and legacy mappings

        Example:
            >>> input_data = RiskAssessmentInput(
            ...     cat_score=15, mmrc_grade=3,
            ...     exacerbation_count_12m=2, hospitalization_count_12m=1
            ... )
            >>> result = service.calculate_risk(input_data)
            >>> result.gold_group
            'E'
            >>> result.risk_level
            'high'
        """
        # Step 1: Classify into GOLD ABE group
        gold_group = self._classify_gold_group(input_data.cat_score, input_data.mmrc_grade)

        # Step 2: Map to legacy risk score/level (Hybrid Strategy for backward compatibility)
        risk_score, risk_level = self._map_to_legacy_risk(gold_group)

        # Step 3: Generate human-readable reasoning
        reasoning = self._generate_reasoning(
            gold_group=gold_group,
            cat_score=input_data.cat_score,
            mmrc_grade=input_data.mmrc_grade,
            exacerbation_count_12m=input_data.exacerbation_count_12m,
        )

        return RiskAssessmentResult(
            gold_group=gold_group,
            risk_score=risk_score,
            risk_level=risk_level,
            reasoning=reasoning,
        )

    def _classify_gold_group(self, cat_score: int, mmrc_grade: int) -> GoldGroup:
        """
        Classify patient into GOLD ABE group

        GOLD ABE Classification Algorithm (GOLD 2011):

        This is the core domain knowledge - the medical guideline.
        It's simple, clear, and has no special cases.

        "Good taste" code structure:
        - No nested if-else (3 clear branches)
        - Descriptive variable names (high_symptoms_cat, high_symptoms_mmrc)
        - Returns immediately when condition matches

        Args:
            cat_score: CAT score (0-40)
            mmrc_grade: mMRC grade (0-4)

        Returns:
            GOLD ABE group: 'A' (low), 'B' (medium), or 'E' (high)
        """
        # Define symptom thresholds (domain knowledge from GOLD guidelines)
        high_symptoms_cat = cat_score >= 10
        high_symptoms_mmrc = mmrc_grade >= 2

        # Classification rules (simple, no special cases)
        if high_symptoms_cat and high_symptoms_mmrc:
            return "E"  # High risk: Both symptoms high
        elif high_symptoms_cat or high_symptoms_mmrc:
            return "B"  # Medium risk: One symptom high
        else:
            return "A"  # Low risk: Both symptoms low

    def _map_to_legacy_risk(self, gold_group: GoldGroup) -> tuple[int, RiskLevel]:
        """
        Map GOLD ABE group to legacy risk_score and risk_level

        Hybrid Strategy (ADR-014): Maintain backward compatibility with
        legacy system while using modern GOLD ABE classification internally.

        "Never break userspace" - Linus Torvalds
        We keep the old API (risk_score/risk_level) working while
        introducing the new standard (GOLD ABE group).

        Args:
            gold_group: GOLD ABE group ('A', 'B', or 'E')

        Returns:
            Tuple of (risk_score: int, risk_level: RiskLevel)

        Design Note:
            Using a dictionary for mapping eliminates if-else chains.
            "Good taste" means choosing the right data structure.
        """
        # Mapping table: Simple, declarative, no special cases
        mapping: dict[GoldGroup, tuple[int, RiskLevel]] = {
            "A": (25, "low"),      # Low risk
            "B": (50, "medium"),   # Medium risk
            "E": (75, "high"),     # High risk
        }
        return mapping[gold_group]

    def _generate_reasoning(
        self,
        gold_group: GoldGroup,
        cat_score: int,
        mmrc_grade: int,
        exacerbation_count_12m: int,
    ) -> str:
        """
        Generate human-readable explanation of risk classification

        Why reasoning matters:
        - Clinicians need to understand WHY a patient is classified in a certain group
        - Transparency builds trust in the system
        - Helps identify potential data quality issues

        Args:
            gold_group: Classified GOLD ABE group
            cat_score: CAT score used in classification
            mmrc_grade: mMRC grade used in classification
            exacerbation_count_12m: Exacerbation history (for context)

        Returns:
            Human-readable explanation string
        """
        # Build reasoning based on GOLD group
        if gold_group == "E":
            reasoning = (
                f"GOLD Group E (High Risk): "
                f"High symptom burden with CAT={cat_score} (≥10) and mMRC={mmrc_grade} (≥2). "
            )
        elif gold_group == "B":
            reasoning = (
                f"GOLD Group B (Medium Risk): "
                f"Moderate symptom burden with CAT={cat_score} or mMRC={mmrc_grade}. "
            )
        else:  # Group A
            reasoning = (
                f"GOLD Group A (Low Risk): "
                f"Low symptom burden with CAT={cat_score} (<10) and mMRC={mmrc_grade} (<2). "
            )

        # Add exacerbation context (if significant)
        if exacerbation_count_12m > 0:
            reasoning += f"Patient had {exacerbation_count_12m} exacerbation(s) in the last 12 months."

        return reasoning
