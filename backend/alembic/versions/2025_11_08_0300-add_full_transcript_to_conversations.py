"""Add full transcript storage to conversations

Revision ID: e1d2c3b4a5f6
Revises: a1b2c3d4e5f6
Create Date: 2025-11-08 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1d2c3b4a5f6'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('conversations', sa.Column('full_transcript', sa.Text(), nullable=True))
    op.execute("DELETE FROM conversation_partners WHERE LOWER(name) = 'harjyot'")


def downgrade() -> None:
    op.drop_column('conversations', 'full_transcript')
