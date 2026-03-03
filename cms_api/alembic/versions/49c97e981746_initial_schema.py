"""initial schema
Revision ID: 49c97e981746
Revises:
Create Date: 2026-03-03 18:04:16.332026
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '49c97e981746'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enum type already exists in public schema — no alter needed
    # op.alter_column('post', 'status', ...)  ← skipped, enum already correct
    # op.alter_column('user', 'role', ...)    ← skipped, enum already correct

    # Drop index that exists in DB but not in ORM models (not in schema.sql either)
    op.drop_index('idx_post_status', table_name='post', schema='mg_schema')


def downgrade() -> None:
    # Recreate the index if rolling back
    op.create_index('idx_post_status', 'post', ['status'], unique=False, schema='mg_schema')