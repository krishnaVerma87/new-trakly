"""update_activity_entity_types

Revision ID: 9b0e5f6d2c3a
Revises: 8a9f3e4d1c2b
Create Date: 2026-01-24 16:51:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b0e5f6d2c3a'
down_revision = '8a9f3e4d1c2b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'sprint' and 'notification' to the entity_type enum
    # MySQL doesn't support ALTER TYPE for enums, so we need to use ALTER TABLE MODIFY
    op.execute("""
        ALTER TABLE activities
        MODIFY COLUMN entity_type
        ENUM('issue', 'feature', 'project', 'comment', 'sprint', 'notification')
        NOT NULL
    """)


def downgrade() -> None:
    # Remove 'sprint' and 'notification' from the entity_type enum
    op.execute("""
        ALTER TABLE activities
        MODIFY COLUMN entity_type
        ENUM('issue', 'feature', 'project', 'comment')
        NOT NULL
    """)
