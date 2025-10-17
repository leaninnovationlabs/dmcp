"""add_users_table

Revision ID: 002
Revises: 001
Create Date: 2025-01-02 00:00:01.000000

"""

from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table with TIMESTAMPTZ for PostgreSQL compatibility
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("roles", sa.String(length=500), nullable=False, default=""),
        # Use DateTime with timezone=True for PostgreSQL compatibility
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create default admin user by default
    # Create indexes
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # Insert admin user by default, set to dochangethispassword as the password
    current_time = datetime.now(timezone.utc)

    connection = op.get_bind()
    connection.execute(
        sa.text("""
        INSERT INTO users (username, password, first_name, last_name, roles, created_at, updated_at)
        VALUES (:username, :password, :first_name, :last_name, :roles, :created_at, :updated_at)
    """),
        {
            "username": "admin",
            "password": "Z0FBQUFBQm91R1RKVkdqRnlvMFlWcVdXVW9aS2tzRkxhaENybUV0eERJN09helF5X2ltdUNJN2tuTU4tQUg1Ukt1S3dlb3QxR2djOFNoeXRhMGdFNm01U2h2UVA0TkZrTWtHSDczdlpQek83ZS0xZW55czR2QXM9",
            "first_name": "Admin",
            "last_name": "Admin",
            "roles": "admin",
            "created_at": current_time,
            "updated_at": current_time,
        },
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes first
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")

    # Drop users table
    op.drop_table("users")
