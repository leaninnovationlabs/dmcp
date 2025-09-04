"""add_users_table

Revision ID: 155f613d7a50
Revises: 003
Create Date: 2025-08-30 20:54:34.973923

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, Sequence[str], None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('roles', sa.String(length=500), nullable=False, default=""),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    

    # Insert admin user by default, set to dochangethispassword as the password
    current_time = datetime.now().isoformat()
    op.execute(f"""
        INSERT INTO users (username, password, first_name, last_name, roles, created_at, updated_at)
        VALUES ('admin', 'Z0FBQUFBQm91R1RKVkdqRnlvMFlWcVdXVW9aS2tzRkxhaENybUV0eERJN09helF5X2ltdUNJN2tuTU4tQUg1Ukt1S3dlb3QxR2djOFNoeXRhMGdFNm01U2h2UVA0TkZrTWtHSDczdlpQek83ZS0xZW55czR2QXM9', 'Admin', 'Admin', 'admin', '{current_time}', '{current_time}')
    """)

    # Create indexes
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes first
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    
    # Drop users table
    op.drop_table('users')
