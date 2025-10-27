"""redesign_daily_log_schema_flexible_tracking

ADR-001: Daily Log Schema Redesign for Flexible COPD Patient Tracking

Breaking Changes:
1. steps_count → exercise_minutes (RENAME)
2. medication_taken, water_intake_ml → nullable (SCHEMA CHANGE)
3. ADD smoking_count (NEW COLUMN)

Migration Strategy:
- Convert existing steps_count to exercise_minutes (10000 steps ≈ 80 minutes)
- Allow NULL values for flexible tracking

Revision ID: 4741100a10d7
Revises: 2c0639c3091b
Create Date: 2025-10-22 04:26:24.249525+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4741100a10d7'
down_revision: Union[str, None] = '2c0639c3091b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Redesign daily_logs schema for flexible COPD tracking

    Changes:
    1. Rename steps_count → exercise_minutes
    2. Make medication_taken nullable (remove default)
    3. Make water_intake_ml nullable
    4. Add smoking_count column
    5. Update CHECK constraints
    """

    # Step 1: Drop old CHECK constraints (will recreate with new names)
    op.drop_constraint('daily_logs_water_intake_check', 'daily_logs', type_='check')
    op.drop_constraint('daily_logs_steps_count_check', 'daily_logs', type_='check')

    # Step 2: Modify medication_taken (remove NOT NULL and default)
    op.alter_column('daily_logs', 'medication_taken',
                    existing_type=sa.Boolean(),
                    nullable=True,
                    server_default=None,
                    comment="Whether medication was taken (NULL = not recorded)")

    # Step 3: Modify water_intake_ml (allow NULL)
    op.alter_column('daily_logs', 'water_intake_ml',
                    existing_type=sa.Integer(),
                    nullable=True,
                    comment="Daily water intake in milliliters (NULL = not recorded)")

    # Step 4: Rename steps_count → exercise_minutes
    op.alter_column('daily_logs', 'steps_count',
                    new_column_name='exercise_minutes',
                    existing_type=sa.Integer(),
                    nullable=True,
                    comment="Daily exercise duration in minutes (replaces steps_count)")

    # Step 5: Convert existing data (10000 steps ≈ 80 minutes)
    op.execute("""
        UPDATE daily_logs
        SET exercise_minutes = ROUND(exercise_minutes * 0.008)
        WHERE exercise_minutes IS NOT NULL
    """)

    # Step 6: Add smoking_count column
    op.add_column('daily_logs',
                  sa.Column('smoking_count', sa.Integer(), nullable=True,
                            comment="Number of cigarettes smoked (COPD risk factor)"))

    # Step 7: Recreate CHECK constraints with new names
    op.create_check_constraint(
        'daily_logs_water_intake_check',
        'daily_logs',
        'water_intake_ml IS NULL OR (water_intake_ml >= 0 AND water_intake_ml <= 10000)'
    )
    op.create_check_constraint(
        'daily_logs_exercise_minutes_check',
        'daily_logs',
        'exercise_minutes IS NULL OR (exercise_minutes >= 0 AND exercise_minutes <= 480)'
    )
    op.create_check_constraint(
        'daily_logs_smoking_count_check',
        'daily_logs',
        'smoking_count IS NULL OR (smoking_count >= 0 AND smoking_count <= 100)'
    )


def downgrade() -> None:
    """
    Rollback to old schema

    WARNING: This will cause data loss for smoking_count!
    """

    # Step 1: Drop new CHECK constraints
    op.drop_constraint('daily_logs_smoking_count_check', 'daily_logs', type_='check')
    op.drop_constraint('daily_logs_exercise_minutes_check', 'daily_logs', type_='check')
    op.drop_constraint('daily_logs_water_intake_check', 'daily_logs', type_='check')

    # Step 2: Drop smoking_count column (DATA LOSS)
    op.drop_column('daily_logs', 'smoking_count')

    # Step 3: Convert exercise_minutes back to steps_count (reverse formula)
    op.execute("""
        UPDATE daily_logs
        SET exercise_minutes = ROUND(exercise_minutes / 0.008)
        WHERE exercise_minutes IS NOT NULL
    """)

    # Step 4: Rename exercise_minutes → steps_count
    op.alter_column('daily_logs', 'exercise_minutes',
                    new_column_name='steps_count',
                    existing_type=sa.Integer(),
                    nullable=True,
                    comment="Daily step count")

    # Step 5: Restore water_intake_ml NOT NULL (set default 0 for NULL values)
    op.execute("UPDATE daily_logs SET water_intake_ml = 0 WHERE water_intake_ml IS NULL")
    op.alter_column('daily_logs', 'water_intake_ml',
                    existing_type=sa.Integer(),
                    nullable=False,
                    comment="Daily water intake in milliliters")

    # Step 6: Restore medication_taken NOT NULL and default
    op.execute("UPDATE daily_logs SET medication_taken = false WHERE medication_taken IS NULL")
    op.alter_column('daily_logs', 'medication_taken',
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default=sa.text("false"),
                    comment=None)

    # Step 7: Recreate old CHECK constraints
    op.create_check_constraint(
        'daily_logs_water_intake_check',
        'daily_logs',
        'water_intake_ml >= 0 AND water_intake_ml <= 10000'
    )
    op.create_check_constraint(
        'daily_logs_steps_count_check',
        'daily_logs',
        'steps_count IS NULL OR (steps_count >= 0 AND steps_count <= 100000)'
    )
