"""added quantity on bills and not_my_city

Revision ID: ff9dc542fe6e
Revises: 6a6c59898c46
Create Date: 2019-10-17 13:32:15.688047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff9dc542fe6e'
down_revision = '6a6c59898c46'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bill', sa.Column('quantity', sa.Integer(), default=1))
    op.add_column('bill', sa.Column('not_my_city', sa.Boolean(), default=False))


def downgrade():
    op.drop_column('bill', 'quantity')
    op.drop_column('bill', 'not_my_city')
