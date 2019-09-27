"""add monthly limit for specific user currency

Revision ID: 51d22c9ec079
Revises: 
Create Date: 2019-09-27 19:33:11.646349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51d22c9ec079'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('user_currency', sa.Column('monthly_cost_limit', sa.Float(), default=1000))
    except Exception as ex:
        print(ex)


def downgrade():
    try:
        op.drop_column('user_currency', 'monthly_cost_limit')
    except Exception as ex:
        print(ex)
