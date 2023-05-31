"""add create_by column in mdlilts

Revision ID: d2cb39496df9
Revises: 
Create Date: 2023-05-24 19:47:54.984218

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2cb39496df9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('Ilts', sa.Column('created_by', sa.String))
    pass


def downgrade() -> None:
    pass
