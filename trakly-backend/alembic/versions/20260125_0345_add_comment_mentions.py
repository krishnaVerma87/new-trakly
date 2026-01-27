"""add_comment_mentions

Revision ID: d62fb217e075
Revises: 9b0e5f6d2c3a
Create Date: 2026-01-25 03:45:26.751907+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd62fb217e075'
down_revision = '9b0e5f6d2c3a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create comment_mentions table
    op.create_table(
        'comment_mentions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('comment_id', sa.String(length=36), nullable=False),
        sa.Column('mentioned_user_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mentioned_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('comment_id', 'mentioned_user_id', name='uq_comment_mention'),
    )
    op.create_index('ix_comment_mentions_comment_id', 'comment_mentions', ['comment_id'])
    op.create_index('ix_comment_mentions_mentioned_user_id', 'comment_mentions', ['mentioned_user_id'])


def downgrade() -> None:
    # Drop comment_mentions table
    op.drop_index('ix_comment_mentions_mentioned_user_id', 'comment_mentions')
    op.drop_index('ix_comment_mentions_comment_id', 'comment_mentions')
    op.drop_table('comment_mentions')
