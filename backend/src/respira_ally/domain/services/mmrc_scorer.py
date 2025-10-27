"""
mMRC Scorer - Domain Service
Calculates Modified Medical Research Council (mMRC) Dyspnea Scale

mMRC Dyspnea Scale (0-4):
- Grade 0: Only breathless with strenuous exercise
- Grade 1: Short of breath when hurrying on level or walking up slight hill
- Grade 2: Walks slower than people of same age on level, or stops for breath
- Grade 3: Stops for breath after walking 100 meters or a few minutes on level
- Grade 4: Too breathless to leave house or breathless when dressing/undressing

Reference: https://www.mrc.ac.uk/
"""

from typing import Literal

from respira_ally.core.schemas.survey import mMRCSurveyAnswers


class mMRCScorer:
    """
    mMRC Scorer Domain Service

    Responsibilities:
    - Validate mMRC grade (0-4)
    - Provide grade descriptions
    - Map grade to severity level
    """

    # Grade range
    MIN_GRADE = 0
    MAX_GRADE = 4

    # Grade descriptions (English for code, Chinese for UI)
    GRADE_DESCRIPTIONS = {
        0: {
            "en": "Only breathless with strenuous exercise",
            "zh": "只在劇烈運動時呼吸困難",
            "severity": "MILD",
        },
        1: {
            "en": "Short of breath when hurrying on level or walking up slight hill",
            "zh": "在平地快走或爬小坡時呼吸急促",
            "severity": "MILD",
        },
        2: {
            "en": "Walks slower than people of same age on level, or stops for breath",
            "zh": "因呼吸問題走得比同齡人慢，或需要停下來呼吸",
            "severity": "MODERATE",
        },
        3: {
            "en": "Stops for breath after walking 100 meters or a few minutes on level",
            "zh": "在平地走約100米或幾分鐘後需要停下來呼吸",
            "severity": "SEVERE",
        },
        4: {
            "en": "Too breathless to leave house or breathless when dressing/undressing",
            "zh": "呼吸困難到無法離開家或穿脫衣服時呼吸困難",
            "severity": "VERY_SEVERE",
        },
    }

    @staticmethod
    def validate_grade(grade: int) -> int:
        """
        Validate mMRC grade is within valid range

        Args:
            grade: mMRC dyspnea grade (0-4)

        Returns:
            Validated grade

        Raises:
            ValueError: If grade is out of range (0-4)
        """
        if not (mMRCScorer.MIN_GRADE <= grade <= mMRCScorer.MAX_GRADE):
            raise ValueError(
                f"mMRC grade must be between {mMRCScorer.MIN_GRADE} and {mMRCScorer.MAX_GRADE}"
            )
        return grade

    @staticmethod
    def get_grade_description(grade: int, language: Literal["en", "zh"] = "zh") -> str:
        """
        Get description for a specific mMRC grade

        Args:
            grade: mMRC dyspnea grade (0-4)
            language: Language for description ("en" or "zh")

        Returns:
            Grade description

        Raises:
            ValueError: If grade is out of range
        """
        mMRCScorer.validate_grade(grade)
        return mMRCScorer.GRADE_DESCRIPTIONS[grade][language]

    @staticmethod
    def determine_severity(grade: int) -> Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"]:
        """
        Determine COPD severity level based on mMRC grade

        Severity Mapping:
        - MILD (Grade 0-1):        Minimal breathlessness
        - MODERATE (Grade 2):      Moderate breathlessness
        - SEVERE (Grade 3):        Severe breathlessness
        - VERY_SEVERE (Grade 4):   Very severe breathlessness

        Args:
            grade: mMRC dyspnea grade (0-4)

        Returns:
            Severity level

        Raises:
            ValueError: If grade is out of range (0-4)
        """
        mMRCScorer.validate_grade(grade)
        return mMRCScorer.GRADE_DESCRIPTIONS[grade]["severity"]

    @classmethod
    def score_and_classify(
        cls, answers: mMRCSurveyAnswers
    ) -> tuple[int, Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"]]:
        """
        Validate grade and determine severity in one call

        Args:
            answers: mMRC survey answers

        Returns:
            Tuple of (grade, severity_level)
        """
        grade = cls.validate_grade(answers.grade)
        severity = cls.determine_severity(grade)
        return grade, severity
