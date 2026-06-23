"""Rename hero_name to role

Revision ID: 5c8fc104e8c4
Revises: cca0a967c145
Create Date: 2026-06-23 01:21:20.231877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c8fc104e8c4'
down_revision: Union[str, Sequence[str], None] = 'cca0a967c145'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('performances', schema=None) as batch_op:
        batch_op.alter_column('hero_name', new_column_name='role')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('performances', schema=None) as batch_op:
        batch_op.alter_column('role', new_column_name='hero_name')

