"""add_saved_searches

Revision ID: 2a53ecb27366
Revises: 569ff48dc9ca
Create Date: 2026-01-25 04:13:47.123825+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a53ecb27366'
down_revision = '569ff48dc9ca'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create saved_searches table
    op.create_table(
        'saved_searches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('filter_config', sa.JSON(), nullable=False),
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_saved_searches_project_id', 'saved_searches', ['project_id'])
    op.create_index('ix_saved_searches_created_by', 'saved_searches', ['created_by'])
    op.create_index('ix_saved_searches_is_shared', 'saved_searches', ['is_shared'])


def downgrade() -> None:
    # Drop saved_searches table
    op.drop_index('ix_saved_searches_is_shared', 'saved_searches')
    op.drop_index('ix_saved_searches_created_by', 'saved_searches')
    op.drop_index('ix_saved_searches_project_id', 'saved_searches')
    op.drop_table('saved_searches')
