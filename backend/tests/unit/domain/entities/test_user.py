"""
Unit tests for User Entity

Tests cover:
- Invariant validation (TD-003.1)
- Domain Events publishing (TD-003.3)
- Business logic (role change, soft delete, authentication methods)
- Factory methods (create_patient, create_therapist)
- Role-based authentication validation
"""

from uuid import uuid4

import pytest

from respira_ally.domain.entities.user import (
    User,
    UserCreatedEvent,
    UserDeletedEvent,
    UserRole,
    UserRoleChangedEvent,
)
from respira_ally.domain.exceptions import BusinessRuleViolationError


class TestUserCreation:
    """Test User creation and basic validation."""

    def test_create_patient_with_line(self):
        """Test creating a patient user with LINE OAuth."""
        patient = User.create_patient(line_user_id="LINE_U1234567890")

        assert patient.user_id is not None
        assert patient.role == UserRole.PATIENT
        assert patient.line_user_id == "LINE_U1234567890"
        assert patient.email is None
        assert patient.hashed_password is None
        assert not patient.is_deleted()

        # Check domain events
        events = patient.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserCreatedEvent)
        assert events[0].user_id == patient.user_id
        assert events[0].role == UserRole.PATIENT
        assert events[0].line_user_id == "LINE_U1234567890"

    def test_create_patient_without_line(self):
        """Test creating a patient user without LINE OAuth (before binding)."""
        patient = User.create_patient()

        assert patient.user_id is not None
        assert patient.role == UserRole.PATIENT
        assert patient.line_user_id is None
        assert patient.email is None
        assert patient.hashed_password is None
        assert not patient.is_deleted()

    def test_create_therapist(self):
        """Test creating a therapist user."""
        therapist = User.create_therapist(
            email="doctor@example.com",
            hashed_password="$2b$12$xyz",
        )

        assert therapist.user_id is not None
        assert therapist.role == UserRole.THERAPIST
        assert therapist.email == "doctor@example.com"
        assert therapist.hashed_password == "$2b$12$xyz"
        assert therapist.line_user_id is None
        assert not therapist.is_deleted()

        # Check domain events
        events = therapist.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserCreatedEvent)
        assert events[0].user_id == therapist.user_id
        assert events[0].role == UserRole.THERAPIST
        assert events[0].email == "doctor@example.com"

    def test_therapist_must_have_email(self):
        """Test that THERAPIST must have email."""
        with pytest.raises(BusinessRuleViolationError, match="THERAPIST must have email"):
            User(
                user_id=uuid4(),
                role=UserRole.THERAPIST,
                email=None,
                hashed_password="$2b$12$xyz",
            )

    def test_supervisor_must_have_login_method(self):
        """Test that SUPERVISOR must have at least one login method."""
        with pytest.raises(
            BusinessRuleViolationError,
            match="SUPERVISOR must have at least one login method",
        ):
            User(
                user_id=uuid4(),
                role=UserRole.SUPERVISOR,
                email=None,
                line_user_id=None,
            )

    def test_admin_must_have_login_method(self):
        """Test that ADMIN must have at least one login method."""
        with pytest.raises(
            BusinessRuleViolationError,
            match="ADMIN must have at least one login method",
        ):
            User(
                user_id=uuid4(),
                role=UserRole.ADMIN,
                email=None,
                line_user_id=None,
            )

    def test_enum_auto_conversion_from_string(self):
        """Test that role string is automatically converted to UserRole enum."""
        user = User(
            user_id=uuid4(),
            role="THERAPIST",  # type: ignore
            email="doctor@example.com",
            hashed_password="$2b$12$xyz",
        )

        assert user.role == UserRole.THERAPIST
        assert isinstance(user.role, UserRole)

    def test_invalid_role_string_raises_error(self):
        """Test that invalid role string raises BusinessRuleViolationError."""
        with pytest.raises(BusinessRuleViolationError, match="Invalid role"):
            User(
                user_id=uuid4(),
                role="INVALID_ROLE",  # type: ignore
                email="user@example.com",
            )


class TestUserBusinessLogic:
    """Test User business logic methods."""

    def test_change_role_patient_to_therapist_fails_without_email(self):
        """Test that changing PATIENT to THERAPIST fails if no email."""
        patient = User.create_patient(line_user_id="LINE_U123")

        with pytest.raises(
            BusinessRuleViolationError,
            match="Cannot change role to THERAPIST",
        ):
            patient.change_role(UserRole.THERAPIST)

    def test_change_role_therapist_to_supervisor(self):
        """Test changing THERAPIST to SUPERVISOR."""
        therapist = User.create_therapist(
            email="doctor@example.com",
            hashed_password="$2b$12$xyz",
        )
        therapist.clear_domain_events()  # Clear creation event

        therapist.change_role(UserRole.SUPERVISOR)

        assert therapist.role == UserRole.SUPERVISOR

        # Check domain events
        events = therapist.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserRoleChangedEvent)
        assert events[0].previous_role == UserRole.THERAPIST
        assert events[0].new_role == UserRole.SUPERVISOR

    def test_change_role_to_same_role_raises_error(self):
        """Test that changing to the same role raises error."""
        patient = User.create_patient(line_user_id="LINE_U123")

        with pytest.raises(
            BusinessRuleViolationError,
            match="User already has role PATIENT",
        ):
            patient.change_role(UserRole.PATIENT)

    def test_soft_delete(self):
        """Test soft deleting a user."""
        patient = User.create_patient(line_user_id="LINE_U123")
        patient.clear_domain_events()  # Clear creation event

        patient.soft_delete()

        assert patient.is_deleted()
        assert patient.deleted_at is not None

        # Check domain events
        events = patient.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserDeletedEvent)
        assert events[0].user_id == patient.user_id
        assert events[0].role == UserRole.PATIENT

    def test_cannot_soft_delete_already_deleted_user(self):
        """Test that soft deleting an already deleted user raises error."""
        patient = User.create_patient(line_user_id="LINE_U123")
        patient.soft_delete()

        with pytest.raises(BusinessRuleViolationError, match="User is already deleted"):
            patient.soft_delete()


class TestUserAuthenticationMethods:
    """Test User authentication-related methods."""

    def test_is_patient(self):
        """Test is_patient() method."""
        patient = User.create_patient()
        therapist = User.create_therapist(email="doctor@example.com", hashed_password="$2b$12$xyz")

        assert patient.is_patient()
        assert not therapist.is_patient()

    def test_is_therapist(self):
        """Test is_therapist() method."""
        patient = User.create_patient()
        therapist = User.create_therapist(email="doctor@example.com", hashed_password="$2b$12$xyz")

        assert therapist.is_therapist()
        assert not patient.is_therapist()

    def test_has_line_auth(self):
        """Test has_line_auth() method."""
        patient_with_line = User.create_patient(line_user_id="LINE_U123")
        patient_without_line = User.create_patient()

        assert patient_with_line.has_line_auth()
        assert not patient_without_line.has_line_auth()

    def test_has_email_auth(self):
        """Test has_email_auth() method."""
        therapist = User.create_therapist(email="doctor@example.com", hashed_password="$2b$12$xyz")
        patient = User.create_patient(line_user_id="LINE_U123")

        assert therapist.has_email_auth()
        assert not patient.has_email_auth()


class TestUserDomainEvents:
    """Test User domain events management."""

    def test_get_domain_events_returns_copy(self):
        """Test that get_domain_events() returns a copy, not the original list."""
        patient = User.create_patient(line_user_id="LINE_U123")

        events1 = patient.get_domain_events()
        events2 = patient.get_domain_events()

        assert events1 is not events2
        assert events1 == events2

    def test_clear_domain_events(self):
        """Test clearing domain events."""
        patient = User.create_patient(line_user_id="LINE_U123")

        assert len(patient.get_domain_events()) == 1

        patient.clear_domain_events()

        assert len(patient.get_domain_events()) == 0
