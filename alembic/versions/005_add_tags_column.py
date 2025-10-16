"""add_tags_column

Revision ID: 005
Revises: 004
Create Date: 2025-10-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, Sequence[str], None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tools', sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'))
    
    op.execute("UPDATE tools SET tags = '[]' WHERE tags IS NULL OR tags = 'null'")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tools', 'tags')
