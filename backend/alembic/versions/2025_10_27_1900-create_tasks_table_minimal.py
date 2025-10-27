"""create_tasks_table_minimal

Revision ID: create_tasks_minimal
Revises: add_supervisor_admin_roles
Create Date: 2025-10-27 19:00:00.000000+08:00

Sprint 5: Task Management System
MINIMAL MIGRATION: Only creates the tasks table without modifying existing tables.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'create_tasks_minimal'
down_revision: Union[str, None] = 'add_supervisor_admin_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tasks table only - minimal impact migration"""

    # Create task enums
    op.execute("CREATE TYPE task_type_enum AS ENUM ('ALERT_TRIGGERED', 'MANUAL', 'SCHEDULED')")
    op.execute("CREATE TYPE task_priority_enum AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')")
    op.execute("CREATE TYPE task_status_enum AS ENUM ('TODO', 'IN_PROGRESS', 'DONE', 'CANCELLED')")

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('task_id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('patient_id', sa.Uuid(), nullable=False, comment='Patient this task is related to'),
        sa.Column('assigned_to', sa.Uuid(), nullable=True, comment='Therapist assigned to this task'),
        sa.Column('related_alert_id', sa.Uuid(), nullable=True, comment='Alert that triggered this task (if applicable)'),
        sa.Column('created_by', sa.Uuid(), nullable=True, comment='User who created this task (for manual tasks)'),
        sa.Column('title', sa.String(length=200), nullable=False, comment='Task title (short description)'),
        sa.Column('description', sa.Text(), nullable=True, comment='Detailed task description and action items'),
        sa.Column('task_type', postgresql.ENUM('ALERT_TRIGGERED', 'MANUAL', 'SCHEDULED', name='task_type_enum', create_type=False), nullable=False, comment='Task type: ALERT_TRIGGERED/MANUAL/SCHEDULED'),
        sa.Column('priority', postgresql.ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', name='task_priority_enum', create_type=False), nullable=False, comment='Task priority: CRITICAL/HIGH/MEDIUM/LOW'),
        sa.Column('status', postgresql.ENUM('TODO', 'IN_PROGRESS', 'DONE', 'CANCELLED', name='task_status_enum', create_type=False), server_default=sa.text("'TODO'"), nullable=False, comment='Task status: TODO/IN_PROGRESS/DONE/CANCELLED'),
        sa.Column('task_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="JSON metadata: {gold_group: 'E', cat_score: 25, reason: '...', cancellation_reason: '...'}"),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True, comment='Task due date (if applicable)'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Task completion timestamp'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Task creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Task last update timestamp'),
        sa.ForeignKeyConstraint(['assigned_to'], ['development.therapist_profiles.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['development.users.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['patient_id'], ['development.patient_profiles.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_alert_id'], ['development.alerts.alert_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('task_id'),
        schema='development'
    )

    # Create indexes
    op.create_index(op.f('ix_development_tasks_assigned_to'), 'tasks', ['assigned_to'], unique=False, schema='development')
    op.create_index(op.f('ix_development_tasks_patient_id'), 'tasks', ['patient_id'], unique=False, schema='development')
    op.create_index(op.f('ix_development_tasks_related_alert_id'), 'tasks', ['related_alert_id'], unique=False, schema='development')


def downgrade() -> None:
    """Drop tasks table and enums"""
    op.drop_index(op.f('ix_development_tasks_related_alert_id'), table_name='tasks', schema='development')
    op.drop_index(op.f('ix_development_tasks_patient_id'), table_name='tasks', schema='development')
    op.drop_index(op.f('ix_development_tasks_assigned_to'), table_name='tasks', schema='development')
    op.drop_table('tasks', schema='development')

    # Drop enums
    op.execute("DROP TYPE task_status_enum")
    op.execute("DROP TYPE task_priority_enum")
    op.execute("DROP TYPE task_type_enum")
