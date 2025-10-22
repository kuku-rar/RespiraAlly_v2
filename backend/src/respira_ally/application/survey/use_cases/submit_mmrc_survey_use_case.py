"""
Submit mMRC Survey Use Case
Handles submission and scoring of mMRC (Modified Medical Research Council) surveys
"""
from datetime import datetime
from uuid import UUID, uuid4

from respira_ally.core.exceptions.application_exceptions import NotFoundError, ValidationError
from respira_ally.core.schemas.survey import mMRCSurveyAnswers, SurveyResponse
from respira_ally.domain.repositories.patient_repository import PatientRepository
from respira_ally.domain.repositories.survey_repository import SurveyRepository
from respira_ally.domain.services.mmrc_scorer import mMRCScorer
from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel


class SubmitMmrcSurveyUseCase:
    """
    Submit mMRC Survey Use Case

    Flow:
    1. Validate patient exists
    2. Validate and classify mMRC grade using mMRCScorer
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
        self.mmrc_scorer = mMRCScorer()

    async def execute(
        self, patient_id: UUID, answers: mMRCSurveyAnswers
    ) -> SurveyResponse:
        """
        Submit a new mMRC survey

        Args:
            patient_id: Patient's user ID
            answers: mMRC survey answers (single grade 0-4)

        Returns:
            SurveyResponse with validated grade and severity

        Raises:
            NotFoundError: If patient not found
            ValidationError: If validation fails
        """
        # Validate patient exists
        patient = await self.patient_repository.get_by_user_id(patient_id)
        if patient is None:
            raise NotFoundError(resource_type="Patient", resource_id=str(patient_id))

        # Validate grade and determine severity using domain service
        grade, severity_level = self.mmrc_scorer.score_and_classify(answers)

        # Convert answers to JSON format
        answers_json = {
            "grade": answers.grade,
        }

        # Create survey response model
        survey_response = SurveyResponseModel(
            response_id=uuid4(),
            survey_type="mMRC",
            patient_id=patient_id,
            answers=answers_json,
            total_score=grade,  # For mMRC, total_score = grade
            severity_level=severity_level,
            submitted_at=datetime.now(),
        )

        # Save to database
        saved_response = await self.survey_repository.create(survey_response)

        # TODO: Publish domain event (SurveySubmitted)
        # This will be implemented when we add domain events

        # Convert to response schema
        return SurveyResponse(
            response_id=saved_response.response_id,
            survey_type="mMRC",
            patient_id=saved_response.patient_id,
            answers=saved_response.answers,
            total_score=saved_response.total_score,
            severity_level=saved_response.severity_level,
            submitted_at=saved_response.submitted_at,
        )
