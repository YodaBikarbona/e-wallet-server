"""change quantity data type

Revision ID: 03cae075a9c7
Revises: 6f758000e01e
Create Date: 2019-11-04 19:36:51.809769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03cae075a9c7'
down_revision = '6f758000e01e'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('bill', 'quantity',
                    existing_type=sa.Integer,
                    type_=sa.Float)


def downgrade():
    op.alter_column('bill', 'quantity',
                    existing_type=sa.Float,
                    type_=sa.Integer)
