"""add_sprints_and_watchers

Revision ID: c172edbccafc
Revises: 278190315932
Create Date: 2026-01-24 16:41:10.777467+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c172edbccafc'
down_revision = '278190315932'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sprints table
    op.create_table(
        'sprints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('sprint_number', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_sprints_project_id', 'sprints', ['project_id'])
    op.create_index('ix_sprints_start_date', 'sprints', ['start_date'])
    op.create_index('ix_sprints_end_date', 'sprints', ['end_date'])
    op.create_index('ix_sprints_is_active', 'sprints', ['is_active'])

    # Create issue_watchers table
    op.create_table(
        'issue_watchers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('issue_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('subscription_type', sa.String(length=20), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('issue_id', 'user_id', name='uq_issue_watcher'),
    )
    op.create_index('ix_issue_watchers_issue_id', 'issue_watchers', ['issue_id'])
    op.create_index('ix_issue_watchers_user_id', 'issue_watchers', ['user_id'])

    # Add sprint_id column to issues table
    op.add_column('issues', sa.Column('sprint_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('fk_issues_sprint_id', 'issues', 'sprints', ['sprint_id'], ['id'])
    op.create_index('ix_issues_sprint_id', 'issues', ['sprint_id'])


def downgrade() -> None:
    # Remove sprint_id from issues table
    op.drop_index('ix_issues_sprint_id', 'issues')
    op.drop_constraint('fk_issues_sprint_id', 'issues', type_='foreignkey')
    op.drop_column('issues', 'sprint_id')

    # Drop issue_watchers table
    op.drop_index('ix_issue_watchers_user_id', 'issue_watchers')
    op.drop_index('ix_issue_watchers_issue_id', 'issue_watchers')
    op.drop_table('issue_watchers')

    # Drop sprints table
    op.drop_index('ix_sprints_is_active', 'sprints')
    op.drop_index('ix_sprints_end_date', 'sprints')
    op.drop_index('ix_sprints_start_date', 'sprints')
    op.drop_index('ix_sprints_project_id', 'sprints')
    op.drop_table('sprints')
