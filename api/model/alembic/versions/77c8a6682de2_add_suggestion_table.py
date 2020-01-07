"""add_suggestion_table

Revision ID: 77c8a6682de2
Revises: 3d4d97453cf1
Create Date: 2020-01-07 11:55:49.624435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77c8a6682de2'
down_revision = '3d4d97453cf1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'suggestions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime),
        sa.Column('comment', sa.Unicode(255), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
    )


def downgrade():
    op.drop_table('suggestions')
