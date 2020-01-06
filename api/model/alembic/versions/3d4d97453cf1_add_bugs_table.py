"""add_bugs_table

Revision ID: 3d4d97453cf1
Revises: 6eda6e299d59
Create Date: 2020-01-06 11:27:42.705147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d4d97453cf1'
down_revision = '6eda6e299d59'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'bugs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime),
        sa.Column('comment', sa.Unicode(255), nullable=False),
        sa.Column('is_fixed', sa.Boolean, default=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
    )


def downgrade():
    op.drop_table('bugs')
