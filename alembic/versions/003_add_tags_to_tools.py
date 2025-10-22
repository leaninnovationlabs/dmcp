"""add_tags_to_tools

Revision ID: 003
Revises: 002
Create Date: 2025-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, Sequence[str], None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tools', sa.Column('tags', sa.JSON(), nullable=True))
    
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE tools SET tags = '[]' WHERE tags IS NULL"))
    

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tools', 'tags')
