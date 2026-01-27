"""add_updated_at_to_attachments

Revision ID: 657f03fc1c65
Revises: d5bd0090ecc8
Create Date: 2026-01-25 05:22:37.807502+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '657f03fc1c65'
down_revision = 'd5bd0090ecc8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at column to attachments table
    op.add_column(
        'attachments',
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    )


def downgrade() -> None:
    # Drop updated_at column from attachments table
    op.drop_column('attachments', 'updated_at')
