"""add_attachments

Revision ID: d5bd0090ecc8
Revises: 2a53ecb27366
Create Date: 2026-01-25 04:20:34.126150+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5bd0090ecc8'
down_revision = '2a53ecb27366'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create attachments table
    op.create_table(
        'attachments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('issue_id', sa.String(length=36), nullable=True),
        sa.Column('feature_id', sa.String(length=36), nullable=True),
        sa.Column('uploaded_by', sa.String(length=36), nullable=False),
        sa.Column('filename', sa.String(length=500), nullable=False),
        sa.Column('original_filename', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('storage_path', sa.String(length=1000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['feature_id'], ['features.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
        # Check constraint: either issue_id OR feature_id must be set
        sa.CheckConstraint('issue_id IS NOT NULL OR feature_id IS NOT NULL', name='chk_attachment_entity'),
    )
    op.create_index('ix_attachments_issue_id', 'attachments', ['issue_id'])
    op.create_index('ix_attachments_feature_id', 'attachments', ['feature_id'])
    op.create_index('ix_attachments_uploaded_by', 'attachments', ['uploaded_by'])


def downgrade() -> None:
    # Drop attachments table
    op.drop_index('ix_attachments_uploaded_by', 'attachments')
    op.drop_index('ix_attachments_feature_id', 'attachments')
    op.drop_index('ix_attachments_issue_id', 'attachments')
    op.drop_table('attachments')
