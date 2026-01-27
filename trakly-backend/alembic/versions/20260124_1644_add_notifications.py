"""add_notifications

Revision ID: 279d715fe60f
Revises: c172edbccafc
Create Date: 2026-01-24 16:44:43.491943+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '279d715fe60f'
down_revision = 'c172edbccafc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('notification_type', sa.Enum('issue_assigned', 'issue_status_changed', 'issue_commented', 'issue_mentioned', 'reminder_stale', 'reminder_due', 'reminder_custom', name='notificationtype'), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('issue_id', sa.String(length=36), nullable=True),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_organization_id', 'notifications', ['organization_id'])
    op.create_index('ix_notifications_notification_type', 'notifications', ['notification_type'])
    op.create_index('ix_notifications_issue_id', 'notifications', ['issue_id'])
    op.create_index('ix_notifications_project_id', 'notifications', ['project_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])

    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('notification_type', sa.Enum('issue_assigned', 'issue_status_changed', 'issue_commented', 'issue_mentioned', 'reminder_stale', 'reminder_due', 'reminder_custom', name='notificationtype'), nullable=False),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('slack_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('email_digest', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('digest_frequency', sa.String(length=20), nullable=False, server_default='daily'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_notification_preferences_user_id', 'notification_preferences', ['user_id'])


def downgrade() -> None:
    # Drop notification_preferences table
    op.drop_index('ix_notification_preferences_user_id', 'notification_preferences')
    op.drop_table('notification_preferences')

    # Drop notifications table
    op.drop_index('ix_notifications_is_read', 'notifications')
    op.drop_index('ix_notifications_project_id', 'notifications')
    op.drop_index('ix_notifications_issue_id', 'notifications')
    op.drop_index('ix_notifications_notification_type', 'notifications')
    op.drop_index('ix_notifications_organization_id', 'notifications')
    op.drop_index('ix_notifications_user_id', 'notifications')
    op.drop_table('notifications')

    # Drop enum type
    op.execute('DROP TYPE notificationtype')
