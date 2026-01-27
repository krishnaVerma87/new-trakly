"""add_wiki_pages

Revision ID: f7471a48ee51
Revises: 8e647f888bab
Create Date: 2026-01-26 03:24:13.799168+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7471a48ee51'
down_revision = '8e647f888bab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'wiki_pages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('wiki_pages.id', ondelete='CASCADE'), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('updated_by', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('position', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

    # Create indexes
    op.create_index('ix_wiki_pages_project_id', 'wiki_pages', ['project_id'])
    op.create_index('ix_wiki_pages_parent_id', 'wiki_pages', ['parent_id'])
    op.create_index('ix_wiki_pages_slug', 'wiki_pages', ['project_id', 'slug'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_wiki_pages_slug', 'wiki_pages')
    op.drop_index('ix_wiki_pages_parent_id', 'wiki_pages')
    op.drop_index('ix_wiki_pages_project_id', 'wiki_pages')
    op.drop_table('wiki_pages')
