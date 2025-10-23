"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2025-01-02 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create datasources table with TIMESTAMPTZ for PostgreSQL compatibility
    op.create_table(
        "datasources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("database_type", sa.String(length=50), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=True),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("database", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("password", sa.String(length=255), nullable=True),
        sa.Column("connection_string", sa.Text(), nullable=True),
        sa.Column("ssl_mode", sa.String(length=50), nullable=True),
        sa.Column("additional_params", sa.JSON(), nullable=True),
        # Use TIMESTAMPTZ for PostgreSQL, DateTime for others
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_index(op.f("ix_datasources_id"), "datasources", ["id"], unique=False)

    # Create tools table (formerly queries) with TIMESTAMPTZ for PostgreSQL compatibility
    op.create_table(
        "tools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=False, default="query"),
        sa.Column("sql", sa.Text(), nullable=False),
        sa.Column("datasource_id", sa.Integer(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=True),
        # Use TIMESTAMPTZ for PostgreSQL, DateTime for others
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["datasource_id"], ["datasources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_index(op.f("ix_tools_id"), "tools", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_tools_id"), table_name="tools")
    op.drop_table("tools")
    op.drop_index(op.f("ix_datasources_id"), table_name="datasources")
    op.drop_table("datasources")
