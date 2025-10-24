"""
Authorization Helper Module
Centralized permission checking logic for RBAC (Role-Based Access Control)

Design Principles:
- DRY (Don't Repeat Yourself): Unified permission logic
- Single Source of Truth: All permission rules in one place
- Extensibility: Easy to add new roles or permission rules
- Testability: Pure functions with clear inputs/outputs

Design Decision: ADR-015 - RBAC Extension for MVP Flexibility
Reference: Linus Torvalds - "Good taste is about eliminating special cases"
"""

from uuid import UUID

from respira_ally.core.schemas.auth import TokenData, UserRole


# ============================================================================
# Patient Data Access Permissions
# ============================================================================


def can_access_patient(
    current_user: TokenData, patient_id: UUID, patient_therapist_id: UUID
) -> bool:
    """
    Check if current user can READ patient data

    Permission Rules (Hierarchical):
    1. ADMIN/SUPERVISOR: Can access ALL patients (MVP mode for flexibility)
    2. THERAPIST: Can only access their own assigned patients
    3. PATIENT: Can only access their own data

    Args:
        current_user: Current authenticated user (from JWT token)
        patient_id: Target patient UUID
        patient_therapist_id: Patient's assigned therapist UUID

    Returns:
        True if access allowed, False otherwise

    Examples:
        >>> # SUPERVISOR can access any patient
        >>> can_access_patient(supervisor_user, patient_123, therapist_456)
        True

        >>> # THERAPIST can only access their own patients
        >>> can_access_patient(therapist_456, patient_123, therapist_456)
        True
        >>> can_access_patient(therapist_456, patient_789, therapist_999)
        False

        >>> # PATIENT can only access themselves
        >>> can_access_patient(patient_123, patient_123, therapist_456)
        True
        >>> can_access_patient(patient_123, patient_789, therapist_456)
        False
    """
    # ADMIN and SUPERVISOR can access all patients (MVP mode)
    # Design: No special cases - these roles simply have unrestricted access
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        return True

    # THERAPIST can only access their own patients
    if current_user.role == UserRole.THERAPIST:
        return current_user.user_id == patient_therapist_id

    # PATIENT can only access themselves
    if current_user.role == UserRole.PATIENT:
        return current_user.user_id == patient_id

    # Default deny (defensive programming)
    return False


def can_modify_patient(current_user: TokenData, patient_therapist_id: UUID) -> bool:
    """
    Check if current user can MODIFY patient data (Create, Update, Delete)

    Permission Rules (Hierarchical):
    1. ADMIN/SUPERVISOR: Can modify ALL patients (MVP mode)
    2. THERAPIST: Can only modify their own assigned patients
    3. PATIENT: Cannot modify patient profiles (read-only)

    Args:
        current_user: Current authenticated user (from JWT token)
        patient_therapist_id: Patient's assigned therapist UUID

    Returns:
        True if modification allowed, False otherwise

    Examples:
        >>> # SUPERVISOR can modify any patient
        >>> can_modify_patient(supervisor_user, therapist_456)
        True

        >>> # THERAPIST can only modify their own patients
        >>> can_modify_patient(therapist_456, therapist_456)
        True
        >>> can_modify_patient(therapist_456, therapist_999)
        False

        >>> # PATIENT cannot modify patient profiles
        >>> can_modify_patient(patient_123, therapist_456)
        False
    """
    # ADMIN and SUPERVISOR can modify all patients (MVP mode)
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        return True

    # THERAPIST can only modify their own patients
    if current_user.role == UserRole.THERAPIST:
        return current_user.user_id == patient_therapist_id

    # PATIENT cannot modify patient profiles (only read access)
    # Design: Patients can view their own data but cannot change profiles
    return False


def can_create_patient(current_user: TokenData) -> bool:
    """
    Check if current user can CREATE new patient profiles

    Permission Rules:
    - ADMIN/SUPERVISOR/THERAPIST: Can create patients
    - PATIENT: Cannot create patients

    Args:
        current_user: Current authenticated user

    Returns:
        True if creation allowed, False otherwise
    """
    return current_user.role in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.THERAPIST]


# ============================================================================
# Clinical Data Access Permissions (Exacerbation, Daily Logs, Surveys)
# ============================================================================


def can_access_clinical_data(
    current_user: TokenData, patient_id: UUID, patient_therapist_id: UUID
) -> bool:
    """
    Check if current user can READ clinical data (exacerbations, daily logs, surveys)

    Permission Rules: Same as patient data access
    - ADMIN/SUPERVISOR: Can access all patients' clinical data
    - THERAPIST: Can only access their own patients' clinical data
    - PATIENT: Can only access their own clinical data

    Args:
        current_user: Current authenticated user
        patient_id: Target patient UUID
        patient_therapist_id: Patient's assigned therapist UUID

    Returns:
        True if access allowed, False otherwise

    Note:
        This is an alias of can_access_patient() for semantic clarity.
        Clinical data follows the same access rules as patient data.
    """
    return can_access_patient(current_user, patient_id, patient_therapist_id)


def can_modify_clinical_data(current_user: TokenData, patient_therapist_id: UUID) -> bool:
    """
    Check if current user can MODIFY clinical data (exacerbations, daily logs, surveys)

    Permission Rules:
    - ADMIN/SUPERVISOR: Can modify all patients' clinical data
    - THERAPIST: Can only modify their own patients' clinical data
    - PATIENT: Can create/modify their own daily logs and surveys (but not exacerbations)

    Args:
        current_user: Current authenticated user
        patient_therapist_id: Patient's assigned therapist UUID

    Returns:
        True if modification allowed, False otherwise

    Note:
        For patient self-service features (daily logs, surveys), use more specific
        permission checks in the respective endpoints.
    """
    # ADMIN and SUPERVISOR can modify all clinical data
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        return True

    # THERAPIST can only modify their own patients' clinical data
    if current_user.role == UserRole.THERAPIST:
        return current_user.user_id == patient_therapist_id

    # PATIENT: Handled by specific endpoint logic (can create their own logs/surveys)
    return False


# ============================================================================
# Role-Based Helpers
# ============================================================================


def is_privileged_user(current_user: TokenData) -> bool:
    """
    Check if user has privileged access (ADMIN or SUPERVISOR)

    Privileged users can access all patients without restrictions.
    Useful for MVP testing and administrative tasks.

    Args:
        current_user: Current authenticated user

    Returns:
        True if user is ADMIN or SUPERVISOR, False otherwise
    """
    return current_user.role in [UserRole.ADMIN, UserRole.SUPERVISOR]


def is_therapist_or_higher(current_user: TokenData) -> bool:
    """
    Check if user is a therapist or has higher privileges

    Useful for endpoints that require clinical staff access.

    Args:
        current_user: Current authenticated user

    Returns:
        True if user is THERAPIST, SUPERVISOR, or ADMIN
    """
    return current_user.role in [UserRole.THERAPIST, UserRole.SUPERVISOR, UserRole.ADMIN]


# ============================================================================
# Permission Error Messages
# ============================================================================


def get_access_denied_message(current_user: TokenData, resource: str) -> str:
    """
    Generate user-friendly access denied message

    Args:
        current_user: Current authenticated user
        resource: Resource being accessed (e.g., "patient data", "exacerbation records")

    Returns:
        Formatted error message
    """
    if current_user.role == UserRole.PATIENT:
        return f"You can only access your own {resource}"
    elif current_user.role == UserRole.THERAPIST:
        return f"You can only access {resource} for your assigned patients"
    else:
        return f"You do not have permission to access this {resource}"
