"""add_tool_type_column

Revision ID: 003
Revises: 002
Create Date: 2025-07-02 23:42:57.991519

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
    # Create the enum type first
    tool_type_enum = sa.Enum('QUERY', 'HTTP', 'CODE', name='tooltype')
    tool_type_enum.create(op.get_bind())
    
    # Add the column with the enum type
    op.add_column('tools', sa.Column('type', tool_type_enum, nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the column first
    op.drop_column('tools', 'type')
    
    # Drop the enum type
    tool_type_enum = sa.Enum('QUERY', 'HTTP', 'CODE', name='tooltype')
    tool_type_enum.drop(op.get_bind())
