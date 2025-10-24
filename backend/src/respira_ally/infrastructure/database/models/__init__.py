"""
Database Models Package

Import all models here for Alembic autogenerate to detect them.
"""

from respira_ally.infrastructure.database.models.alert import AlertModel
from respira_ally.infrastructure.database.models.daily_log import DailyLogModel
from respira_ally.infrastructure.database.models.event_log import EventLogModel
from respira_ally.infrastructure.database.models.exacerbation import ExacerbationModel
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.risk_assessment import RiskAssessmentModel
from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel
from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel
from respira_ally.infrastructure.database.models.user import UserModel

__all__ = [
    "UserModel",
    "PatientProfileModel",
    "TherapistProfileModel",
    "DailyLogModel",
    "SurveyResponseModel",
    "EventLogModel",
    # Sprint 4: Risk Engine & Alert System
    "ExacerbationModel",
    "RiskAssessmentModel",
    "AlertModel",
]
