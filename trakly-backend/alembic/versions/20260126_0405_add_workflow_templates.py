"""add_workflow_templates

Revision ID: a72e66d1d67f
Revises: f7471a48ee51
Create Date: 2026-01-26 04:05:48.401226+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a72e66d1d67f'
down_revision = 'f7471a48ee51'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workflow_templates table
    op.create_table(
        'workflow_templates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_system', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_workflow_templates_organization_id', 'workflow_templates', ['organization_id'])

    # Create workflow_columns table
    op.create_table(
        'workflow_columns',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('template_id', sa.String(36), sa.ForeignKey('workflow_templates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('wip_limit', sa.Integer(), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_workflow_columns_template_id', 'workflow_columns', ['template_id'])

    # Add workflow_template_id to projects table
    op.add_column('projects', sa.Column('workflow_template_id', sa.String(36), sa.ForeignKey('workflow_templates.id'), nullable=True))
    op.create_index('ix_projects_workflow_template_id', 'projects', ['workflow_template_id'])

    # Add workflow_column_id to issues table
    op.add_column('issues', sa.Column('workflow_column_id', sa.String(36), sa.ForeignKey('workflow_columns.id'), nullable=True))
    op.create_index('ix_issues_workflow_column_id', 'issues', ['workflow_column_id'])


def downgrade() -> None:
    # Remove workflow_column_id from issues table
    op.drop_index('ix_issues_workflow_column_id', 'issues')
    op.drop_column('issues', 'workflow_column_id')

    # Remove workflow_template_id from projects table
    op.drop_index('ix_projects_workflow_template_id', 'projects')
    op.drop_column('projects', 'workflow_template_id')

    # Drop workflow_columns table
    op.drop_index('ix_workflow_columns_template_id', 'workflow_columns')
    op.drop_table('workflow_columns')

    # Drop workflow_templates table
    op.drop_index('ix_workflow_templates_organization_id', 'workflow_templates')
    op.drop_table('workflow_templates')
