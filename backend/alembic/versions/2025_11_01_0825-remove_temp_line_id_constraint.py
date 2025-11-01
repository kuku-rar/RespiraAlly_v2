"""Remove temp_line_id constraint and clean up temporary data (TD-002)

Revision ID: 2025_11_01_0825
Revises: daa11447efa1
Create Date: 2025-11-01 08:25:00.000000+08:00

Technical Debt: TD-002 - Remove temp_line_id design flaw
Problem: Using temporary field `temp_line_id` to store permanent LINE User ID
Solution: Allow line_user_id to be NULL for patients not yet linked to LINE

Changes:
1. DROP CheckConstraint 'users_patient_line_check' (PATIENT must have line_user_id)
2. UPDATE existing temp_line_id values to NULL
3. Keep 'users_login_method_check' (at least one login method required)

Impact: Backward compatible - existing functionality preserved
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_01_0825'
down_revision: Union[str, None] = 'add_supervisor_admin_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove temp_line_id constraint and clean up data.

    Steps:
    1. Update all temp_line_id values (starting with 'temp_') to NULL
    2. Drop the 'users_patient_line_check' constraint
    3. Relax 'users_login_method_check' to allow PATIENT without login method

    Rationale:
    - PATIENT records can be created by therapists before LINE binding
    - LOGIN functionality requires line_user_id, but PATIENT record can exist without it
    - When PATIENT first logs in via LINE, line_user_id will be set
    """
    # Step 1: Clean up temporary LINE IDs
    # Update all line_user_id values that start with 'temp_' to NULL
    op.execute(
        """
        UPDATE users
        SET line_user_id = NULL
        WHERE line_user_id LIKE 'temp_%'
        """
    )

    # Step 2: Drop the old constraint that requires PATIENT to have line_user_id
    op.drop_constraint('users_patient_line_check', 'users', type_='check')

    # Step 3: Relax the login method check to allow PATIENT without login method
    # (PATIENT can exist as a record before LINE binding)
    op.drop_constraint('users_login_method_check', 'users', type_='check')
    op.create_check_constraint(
        'users_login_method_check',
        'users',
        "role = 'PATIENT' OR (line_user_id IS NOT NULL OR email IS NOT NULL)"
    )


def downgrade() -> None:
    """
    Restore the old constraints (NOT RECOMMENDED - will fail if NULL line_user_id exists).

    WARNING: This downgrade will fail if any PATIENT users have NULL line_user_id.
    Only use this if you're reverting immediately after upgrade with no new data.
    """
    # Step 1: Restore the stricter login method check
    op.drop_constraint('users_login_method_check', 'users', type_='check')
    op.create_check_constraint(
        'users_login_method_check',
        'users',
        'line_user_id IS NOT NULL OR email IS NOT NULL'
    )

    # Step 2: Restore the constraint: PATIENT must have line_user_id
    op.create_check_constraint(
        'users_patient_line_check',
        'users',
        "role != 'PATIENT' OR line_user_id IS NOT NULL"
    )

    # Note: We don't restore temp_line_id values as they were temporary data
