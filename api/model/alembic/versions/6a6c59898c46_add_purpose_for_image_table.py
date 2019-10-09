"""add purpose for image table

Revision ID: 6a6c59898c46
Revises: fbfe6389c361
Create Date: 2019-10-09 13:57:42.260723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a6c59898c46'
down_revision = 'fbfe6389c361'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('image', sa.Column('image_purpose', sa.Unicode(255)))


def downgrade():
    op.drop_column('image', 'image_purpose')
