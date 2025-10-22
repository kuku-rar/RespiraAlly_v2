"""
CAT Scorer - Domain Service
Calculates COPD Assessment Test (CAT) score and severity level

CAT Score Ranges:
- 0-10:   MILD impact
- 11-20:  MODERATE impact
- 21-30:  SEVERE impact
- 31-40:  VERY SEVERE impact

Reference: https://www.catestonline.org
"""
from typing import Literal

from respira_ally.core.schemas.survey import CATSurveyAnswers


class CATScorer:
    """
    CAT Scorer Domain Service

    Responsibilities:
    - Calculate total CAT score (sum of 8 questions)
    - Determine severity level based on total score
    - Validate score ranges
    """

    # Severity thresholds
    MILD_MAX = 10
    MODERATE_MAX = 20
    SEVERE_MAX = 30
    MAX_SCORE = 40

    @staticmethod
    def calculate_total_score(answers: CATSurveyAnswers) -> int:
        """
        Calculate total CAT score (sum of all 8 questions)

        Args:
            answers: CAT survey answers (8 questions, each 0-5)

        Returns:
            Total score (0-40)
        """
        return (
            answers.q1_cough
            + answers.q2_mucus
            + answers.q3_chest_tightness
            + answers.q4_breathlessness_stairs
            + answers.q5_activity_limitation
            + answers.q6_confidence_leaving_home
            + answers.q7_sleep_quality
            + answers.q8_energy_level
        )

    @staticmethod
    def determine_severity(total_score: int) -> Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"]:
        """
        Determine COPD severity level based on CAT score

        Severity Levels:
        - MILD (0-10):        Low impact on daily life
        - MODERATE (11-20):   Moderate impact on daily life
        - SEVERE (21-30):     Severe impact on daily life
        - VERY_SEVERE (31-40): Very severe impact on daily life

        Args:
            total_score: CAT total score (0-40)

        Returns:
            Severity level

        Raises:
            ValueError: If total_score is out of range (0-40)
        """
        if not (0 <= total_score <= CATScorer.MAX_SCORE):
            raise ValueError(f"CAT score must be between 0 and {CATScorer.MAX_SCORE}")

        if total_score <= CATScorer.MILD_MAX:
            return "MILD"
        elif total_score <= CATScorer.MODERATE_MAX:
            return "MODERATE"
        elif total_score <= CATScorer.SEVERE_MAX:
            return "SEVERE"
        else:
            return "VERY_SEVERE"

    @classmethod
    def score_and_classify(cls, answers: CATSurveyAnswers) -> tuple[int, Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"]]:
        """
        Calculate score and determine severity in one call

        Args:
            answers: CAT survey answers

        Returns:
            Tuple of (total_score, severity_level)
        """
        total_score = cls.calculate_total_score(answers)
        severity = cls.determine_severity(total_score)
        return total_score, severity
