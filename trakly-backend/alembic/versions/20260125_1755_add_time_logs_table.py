"""add_time_logs_table

Revision ID: 8e647f888bab
Revises: 1511c4176f46
Create Date: 2026-01-25 17:55:57.138415+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e647f888bab'
down_revision = '1511c4176f46'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'time_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('issue_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_time_logs_issue_id'), 'time_logs', ['issue_id'], unique=False)
    op.create_index(op.f('ix_time_logs_user_id'), 'time_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_time_logs_user_id'), table_name='time_logs')
    op.drop_index(op.f('ix_time_logs_issue_id'), table_name='time_logs')
    op.drop_table('time_logs')
