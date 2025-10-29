"""add_tool_code_to_tools

Revision ID: 005
Revises: 004
Create Date: 2025-10-28 12:57:55.293942

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, Sequence[str], None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add tool_code column to tools table
    op.add_column("tools", sa.Column("tool_code", sa.Text(), nullable=True))

    # Make sql column nullable (it was previously NOT NULL)
    op.alter_column("tools", "sql", existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make sql column NOT NULL again
    op.alter_column("tools", "sql", existing_type=sa.Text(), nullable=False)

    # Remove tool_code column
    op.drop_column("tools", "tool_code")
