"""add team to performance

Revision ID: d4b8e23f1a09
Revises: 5c8fc104e8c4
Create Date: 2026-06-25 04:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4b8e23f1a09'
down_revision = '5c8fc104e8c4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('performances', sa.Column('team', sa.String(), nullable=True))


def downgrade():
    op.drop_column('performances', 'team')
