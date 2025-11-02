"""
User Domain Entity - Core Authentication
Sprint 3: User Management - Multi-role authentication system

This Entity represents the business logic and invariants for user authentication.
Following Clean Architecture and Linus "Good Taste" principles.

Business Rules (TD-003.1):
1. PATIENT can use LINE OAuth (line_user_id) or exist without login method (before LINE binding)
2. THERAPIST must have email + hashed_password
3. Role must be one of: PATIENT, THERAPIST, SUPERVISOR, ADMIN
4. At least one login method required (except unbound PATIENT)
5. Soft delete supported (deleted_at timestamp)

Domain Events (TD-003.3):
- UserCreatedEvent: When user is created
- UserRoleChangedEvent: When role changes
- UserDeletedEvent: When user is soft-deleted
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from respira_ally.domain.events.base import DomainEvent
from respira_ally.domain.exceptions import BusinessRuleViolationError


# ============================================================================
# User Enums
# ============================================================================


class UserRole(str, Enum):
    """User roles in the system"""

    PATIENT = "PATIENT"  # Patient using LINE OAuth
    THERAPIST = "THERAPIST"  # Healthcare provider using email/password
    SUPERVISOR = "SUPERVISOR"  # MVP unrestricted access
    ADMIN = "ADMIN"  # System administrator


# ============================================================================
# Domain Events
# ============================================================================


@dataclass(frozen=True)
class UserCreatedEvent(DomainEvent):
    """Emitted when a new user is created"""

    user_id: UUID
    role: UserRole
    email: Optional[str]
    line_user_id: Optional[str]
    created_at: datetime


@dataclass(frozen=True)
class UserRoleChangedEvent(DomainEvent):
    """Emitted when user role is changed"""

    user_id: UUID
    previous_role: UserRole
    new_role: UserRole
    changed_at: datetime


@dataclass(frozen=True)
class UserDeletedEvent(DomainEvent):
    """Emitted when user is soft-deleted"""

    user_id: UUID
    role: UserRole
    deleted_at: datetime


# ============================================================================
# User Entity
# ============================================================================


@dataclass
class User:
    """
    User Domain Entity - Core authentication entity

    Linus "Good Taste" Principles Applied:
    1. No special cases - Authentication method validation unified
    2. Single source of truth - Role determines authentication requirements
    3. Clear invariants - All business rules enforced in __post_init__
    4. Simple data structure - Minimal fields, maximum clarity

    Business Rules:
    - PATIENT: Can have line_user_id (LINE OAuth) or neither (before binding)
    - THERAPIST: Must have email + hashed_password
    - SUPERVISOR/ADMIN: Must have at least one login method
    - Role changes publish domain events
    - Soft delete preserves data for audit trail
    """

    # Identifier
    user_id: UUID

    # Authentication Fields
    role: UserRole
    line_user_id: Optional[str] = None
    email: Optional[str] = None
    hashed_password: Optional[str] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    # Domain Events (not persisted)
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate invariants after initialization (TD-003.1)

        Linus "Good Taste": All validation in one place, no scattered checks.
        """
        # Validate role enum
        if not isinstance(self.role, UserRole):
            if isinstance(self.role, str):
                try:
                    self.role = UserRole(self.role)
                except ValueError:
                    raise BusinessRuleViolationError(
                        f"Invalid role. Must be one of {[r.value for r in UserRole]}"
                    )
            else:
                raise BusinessRuleViolationError("role must be UserRole enum or string")

        # Validate authentication based on role
        self._validate_authentication()

    def _validate_authentication(self) -> None:
        """
        Validate authentication fields based on user role

        Business Rules:
        - PATIENT: Can have line_user_id OR neither (before LINE binding)
        - THERAPIST: Must have email
        - Other roles: Must have at least one login method
        """
        if self.role == UserRole.THERAPIST:
            # THERAPIST must have email
            if not self.email:
                raise BusinessRuleViolationError("THERAPIST must have email")

        elif self.role != UserRole.PATIENT:
            # SUPERVISOR/ADMIN must have at least one login method
            if not self.line_user_id and not self.email:
                raise BusinessRuleViolationError(
                    f"{self.role.value} must have at least one login method (line_user_id or email)"
                )

        # PATIENT can have line_user_id OR neither (before LINE binding) - no validation needed

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def change_role(self, new_role: UserRole) -> None:
        """
        Change user role

        Business Rules:
        - New role must be different from current
        - New role must have valid authentication for that role
        - Publishes UserRoleChangedEvent

        Args:
            new_role: New UserRole to assign

        Raises:
            BusinessRuleViolationError: If role change is invalid

        Publishes:
            UserRoleChangedEvent
        """
        if self.role == new_role:
            raise BusinessRuleViolationError(
                f"User already has role {new_role.value}"
            )

        previous_role = self.role
        self.role = new_role
        self.updated_at = datetime.utcnow()

        # Validate authentication after role change
        try:
            self._validate_authentication()
        except BusinessRuleViolationError as e:
            # Roll back role change if validation fails
            self.role = previous_role
            raise BusinessRuleViolationError(
                f"Cannot change role to {new_role.value}: {str(e)}"
            )

        # Publish domain event (TD-003.3)
        self._add_domain_event(
            UserRoleChangedEvent(
                user_id=self.user_id,
                previous_role=previous_role,
                new_role=new_role,
                changed_at=self.updated_at,
            )
        )

    def soft_delete(self) -> None:
        """
        Soft delete user

        Business Rules:
        - Cannot delete already deleted user
        - Sets deleted_at timestamp
        - Publishes UserDeletedEvent

        Raises:
            BusinessRuleViolationError: If user is already deleted

        Publishes:
            UserDeletedEvent
        """
        if self.deleted_at is not None:
            raise BusinessRuleViolationError("User is already deleted")

        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Publish domain event (TD-003.3)
        self._add_domain_event(
            UserDeletedEvent(
                user_id=self.user_id,
                role=self.role,
                deleted_at=self.deleted_at,
            )
        )

    def is_deleted(self) -> bool:
        """Check if user is soft-deleted"""
        return self.deleted_at is not None

    def is_patient(self) -> bool:
        """Check if user is a patient"""
        return self.role == UserRole.PATIENT

    def is_therapist(self) -> bool:
        """Check if user is a therapist"""
        return self.role == UserRole.THERAPIST

    def has_line_auth(self) -> bool:
        """Check if user has LINE OAuth authentication"""
        return self.line_user_id is not None

    def has_email_auth(self) -> bool:
        """Check if user has email/password authentication"""
        return self.email is not None and self.hashed_password is not None

    # ========================================================================
    # Domain Events Management (TD-003.3)
    # ========================================================================

    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to internal list (not persisted)"""
        self._domain_events.append(event)

    def get_domain_events(self) -> list[DomainEvent]:
        """Get all domain events for Application Service to publish"""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear domain events after Application Service publishes them"""
        self._domain_events.clear()

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create_patient(
        cls,
        line_user_id: Optional[str] = None,
    ) -> "User":
        """
        Factory method to create a new patient user

        Automatically publishes UserCreatedEvent

        Args:
            line_user_id: Optional LINE User ID (can be None before LINE binding)

        Returns:
            New User instance with PATIENT role and UserCreatedEvent published
        """
        user = cls(
            user_id=uuid4(),
            role=UserRole.PATIENT,
            line_user_id=line_user_id,
        )

        # Publish domain event (TD-003.3)
        user._add_domain_event(
            UserCreatedEvent(
                user_id=user.user_id,
                role=UserRole.PATIENT,
                email=None,
                line_user_id=line_user_id,
                created_at=user.created_at,
            )
        )

        return user

    @classmethod
    def create_therapist(
        cls,
        email: str,
        hashed_password: str,
    ) -> "User":
        """
        Factory method to create a new therapist user

        Automatically publishes UserCreatedEvent

        Args:
            email: Therapist email address
            hashed_password: Bcrypt hashed password

        Returns:
            New User instance with THERAPIST role and UserCreatedEvent published
        """
        user = cls(
            user_id=uuid4(),
            role=UserRole.THERAPIST,
            email=email,
            hashed_password=hashed_password,
        )

        # Publish domain event (TD-003.3)
        user._add_domain_event(
            UserCreatedEvent(
                user_id=user.user_id,
                role=UserRole.THERAPIST,
                email=email,
                line_user_id=None,
                created_at=user.created_at,
            )
        )

        return user

    def __repr__(self) -> str:
        return (
            f"<User(id={self.user_id}, "
            f"role={self.role.value}, "
            f"deleted={self.is_deleted()})>"
        )
