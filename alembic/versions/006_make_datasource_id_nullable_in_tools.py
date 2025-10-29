"""make_datasource_id_nullable_in_tools

Revision ID: 006
Revises: 005
Create Date: 2025-10-28 13:21:32.742706

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, Sequence[str], None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make datasource_id nullable to support code tools without datasources
    op.alter_column("tools", "datasource_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make datasource_id NOT NULL again
    op.alter_column("tools", "datasource_id", existing_type=sa.Integer(), nullable=False)
