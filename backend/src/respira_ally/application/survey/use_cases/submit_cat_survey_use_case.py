"""
Submit CAT Survey Use Case
Handles submission and scoring of CAT (COPD Assessment Test) surveys
"""

from datetime import datetime
from uuid import UUID, uuid4

from respira_ally.core.exceptions.application_exceptions import (
    ResourceNotFoundError,
)
from respira_ally.core.schemas.survey import CATSurveyAnswers, SurveyResponse
from respira_ally.domain.repositories.patient_repository import PatientRepository
from respira_ally.domain.repositories.survey_repository import SurveyRepository
from respira_ally.domain.services.cat_scorer import CATScorer
from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel


class SubmitCATSurveyUseCase:
    """
    Submit CAT Survey Use Case

    Flow:
    1. Validate patient exists
    2. Calculate CAT score and severity using CATScorer
    3. Convert answers to JSON format
    4. Create SurveyResponseModel
    5. Save to database via repository
    6. Return survey response
    """

    def __init__(
        self,
        survey_repository: SurveyRepository,
        patient_repository: PatientRepository,
    ):
        self.survey_repository = survey_repository
        self.patient_repository = patient_repository
        self.cat_scorer = CATScorer()

    async def execute(self, patient_id: UUID, answers: CATSurveyAnswers) -> SurveyResponse:
        """
        Submit a new CAT survey

        Args:
            patient_id: Patient's user ID
            answers: CAT survey answers (8 questions)

        Returns:
            SurveyResponse with calculated score and severity

        Raises:
            ResourceNotFoundError: If patient not found
            ValidationError: If validation fails
        """
        # Validate patient exists
        patient = await self.patient_repository.get_by_id(patient_id)
        if patient is None:
            raise ResourceNotFoundError(resource_type="Patient", resource_id=str(patient_id))

        # Calculate score and severity using domain service
        total_score, severity_level = self.cat_scorer.score_and_classify(answers)

        # Convert answers to JSON format
        answers_json = {
            "q1_cough": answers.q1_cough,
            "q2_mucus": answers.q2_mucus,
            "q3_chest_tightness": answers.q3_chest_tightness,
            "q4_breathlessness_stairs": answers.q4_breathlessness_stairs,
            "q5_activity_limitation": answers.q5_activity_limitation,
            "q6_confidence_leaving_home": answers.q6_confidence_leaving_home,
            "q7_sleep_quality": answers.q7_sleep_quality,
            "q8_energy_level": answers.q8_energy_level,
        }

        # Create survey response model
        survey_response = SurveyResponseModel(
            response_id=uuid4(),
            survey_type="CAT",
            patient_id=patient_id,
            answers=answers_json,
            total_score=total_score,
            severity_level=severity_level,
            submitted_at=datetime.now(),
        )

        # Save to database
        saved_response = await self.survey_repository.create(survey_response)

        # TODO: Publish domain event (SurveySurveySubmitted)
        # This will be implemented when we add domain events

        # Convert to response schema
        return SurveyResponse(
            response_id=saved_response.response_id,
            survey_type="CAT",
            patient_id=saved_response.patient_id,
            answers=saved_response.answers,
            total_score=saved_response.total_score,
            severity_level=saved_response.severity_level,
            submitted_at=saved_response.submitted_at,
        )
