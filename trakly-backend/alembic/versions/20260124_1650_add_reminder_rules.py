"""add_reminder_rules

Revision ID: 8a9f3e4d1c2b
Revises: c172edbccafc
Create Date: 2026-01-24 16:50:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '8a9f3e4d1c2b'
down_revision = '279d715fe60f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reminder_rules table
    op.create_table(
        'reminder_rules',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('conditions', mysql.JSON(), nullable=False),
        sa.Column('notification_title', sa.String(length=500), nullable=False),
        sa.Column('notification_message', sa.String(length=2000), nullable=False),
        sa.Column('notify_assignee', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('notify_watchers', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('check_frequency_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('last_executed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_reminder_rules_project_id', 'reminder_rules', ['project_id'])
    op.create_index('ix_reminder_rules_is_enabled', 'reminder_rules', ['is_enabled'])
    op.create_index('ix_reminder_rules_last_executed_at', 'reminder_rules', ['last_executed_at'])


def downgrade() -> None:
    # Drop reminder_rules table
    op.drop_index('ix_reminder_rules_last_executed_at', 'reminder_rules')
    op.drop_index('ix_reminder_rules_is_enabled', 'reminder_rules')
    op.drop_index('ix_reminder_rules_project_id', 'reminder_rules')
    op.drop_table('reminder_rules')
