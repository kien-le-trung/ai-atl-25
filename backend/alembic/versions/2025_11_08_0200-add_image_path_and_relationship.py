"""Add image_path and relationship fields to conversation_partners

Revision ID: a1b2c3d4e5f6
Revises: 67f74e9cc4a7
Create Date: 2025-11-08 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '67f74e9cc4a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add relationship column
    op.add_column('conversation_partners', sa.Column('relationship', sa.String(), nullable=True))

    # Add image_path column
    op.add_column('conversation_partners', sa.Column('image_path', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove columns
    op.drop_column('conversation_partners', 'image_path')
    op.drop_column('conversation_partners', 'relationship')
