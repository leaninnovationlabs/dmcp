"""rename queries table to tools

Revision ID: 002
Revises: 001
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename the queries table to tools
    op.rename_table('queries', 'tools')
    
    # Drop the old index
    op.drop_index('ix_queries_id', table_name='tools')
    
    # Create the new index
    op.create_index(op.f('ix_tools_id'), 'tools', ['id'], unique=False)


def downgrade() -> None:
    # Drop the new index
    op.drop_index(op.f('ix_tools_id'), table_name='tools')
    
    # Create the old index
    op.create_index(op.f('ix_queries_id'), 'tools', ['id'], unique=False)
    
    # Rename the tools table back to queries
    op.rename_table('tools', 'queries')
