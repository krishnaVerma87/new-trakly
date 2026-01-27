"""add_feature_watchers

Revision ID: 569ff48dc9ca
Revises: d62fb217e075
Create Date: 2026-01-25 03:52:02.922912+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '569ff48dc9ca'
down_revision = 'd62fb217e075'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create feature_watchers table
    op.create_table(
        'feature_watchers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('feature_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('subscription_type', sa.String(length=20), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['feature_id'], ['features.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('feature_id', 'user_id', name='uq_feature_watcher'),
    )
    op.create_index('ix_feature_watchers_feature_id', 'feature_watchers', ['feature_id'])
    op.create_index('ix_feature_watchers_user_id', 'feature_watchers', ['user_id'])


def downgrade() -> None:
    # Drop feature_watchers table
    op.drop_index('ix_feature_watchers_user_id', 'feature_watchers')
    op.drop_index('ix_feature_watchers_feature_id', 'feature_watchers')
    op.drop_table('feature_watchers')
