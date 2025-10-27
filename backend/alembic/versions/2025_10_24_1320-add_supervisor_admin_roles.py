"""add_supervisor_admin_roles

ADR-015: RBAC Extension for MVP Flexibility

Breaking Changes:
1. ADD SUPERVISOR role to user_role_enum (MVP: Can access all patients)
2. ADD ADMIN role to user_role_enum (Future: Full system administration)

Migration Strategy:
- Use ALTER TYPE to add new enum values (PostgreSQL 9.1+)
- Update CHECK constraints to allow new roles
- Backward compatible: Existing PATIENT/THERAPIST users unaffected

Revision ID: add_supervisor_admin_roles
Revises: 4741100a10d7
Create Date: 2025-10-24 13:20:00.000000+08:00

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'add_supervisor_admin_roles'
down_revision: Union[str, None] = '4741100a10d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add SUPERVISOR and ADMIN roles to user_role_enum

    Permission Hierarchy (lowest to highest):
    - PATIENT: Can only access their own data
    - THERAPIST: Can access their assigned patients' data
    - SUPERVISOR: Can access ALL patients' data (MVP mode)
    - ADMIN: Full system access (future use)

    Design Rationale:
    - MVP Requirement: Therapists need unrestricted patient access for testing
    - Production Ready: Preserves existing THERAPIST role for future role separation
    - Extensibility: ADMIN role reserved for user management and system config
    """

    # Step 1: Add SUPERVISOR to user_role_enum
    # Note: PostgreSQL requires COMMIT between ALTER TYPE statements
    op.execute("ALTER TYPE user_role_enum ADD VALUE IF NOT EXISTS 'SUPERVISOR'")

    # Step 2: Add ADMIN to user_role_enum
    op.execute("ALTER TYPE user_role_enum ADD VALUE IF NOT EXISTS 'ADMIN'")

    # Step 3: Update CHECK constraints to allow SUPERVISOR/ADMIN roles
    # Note: SUPERVISOR and ADMIN can use either email OR LINE login
    # Existing constraints already allow NULL for both fields, so no changes needed

    # Optional: Add comment to users table documenting new roles
    op.execute("""
        COMMENT ON COLUMN users.role IS 'User role: PATIENT (self-access only), THERAPIST (assigned patients), SUPERVISOR (all patients - MVP), ADMIN (system admin - future)'
    """)


def downgrade() -> None:
    """
    Rollback: Remove SUPERVISOR and ADMIN roles

    WARNING: This will FAIL if any users have SUPERVISOR or ADMIN roles.
    Must manually delete/reassign these users before downgrade.

    Design Decision: No automatic downgrade to prevent data loss.
    Operators must explicitly handle role migration.
    """

    # Check if any users have SUPERVISOR or ADMIN roles
    op.execute("""
        DO $$
        DECLARE
            supervisor_count INTEGER;
            admin_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO supervisor_count FROM users WHERE role = 'SUPERVISOR';
            SELECT COUNT(*) INTO admin_count FROM users WHERE role = 'ADMIN';

            IF supervisor_count > 0 OR admin_count > 0 THEN
                RAISE EXCEPTION 'Cannot downgrade: % SUPERVISOR and % ADMIN users exist. Please delete or reassign them first.', supervisor_count, admin_count;
            END IF;
        END$$;
    """)

    # Note: PostgreSQL does not support removing enum values directly
    # Workaround: Create new enum without SUPERVISOR/ADMIN, rename, drop old
    # This is complex and risky, so we document the manual process instead

    op.execute("""
        COMMENT ON COLUMN users.role IS 'User role: PATIENT, THERAPIST'
    """)

    # Manual downgrade required:
    # 1. DELETE FROM users WHERE role IN ('SUPERVISOR', 'ADMIN');
    # 2. CREATE TYPE user_role_enum_new AS ENUM ('PATIENT', 'THERAPIST');
    # 3. ALTER TABLE users ALTER COLUMN role TYPE user_role_enum_new USING role::text::user_role_enum_new;
    # 4. DROP TYPE user_role_enum;
    # 5. ALTER TYPE user_role_enum_new RENAME TO user_role_enum;

    raise NotImplementedError(
        "Downgrade not implemented. "
        "To remove SUPERVISOR/ADMIN roles, manually delete affected users and recreate enum type. "
        "See migration file comments for detailed steps."
    )
