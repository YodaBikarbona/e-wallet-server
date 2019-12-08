"""application_user_rating

Revision ID: 6eda6e299d59
Revises: cc6d5d622628
Create Date: 2019-12-08 14:09:36.863369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6eda6e299d59'
down_revision = 'cc6d5d622628'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('application_rating', sa.Integer))


def downgrade():
    op.drop_column('users', 'application_rating')
