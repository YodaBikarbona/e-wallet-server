"""new category translation table

Revision ID: 021af24a3d90
Revises: 03cae075a9c7
Create Date: 2019-11-19 14:16:46.267447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '021af24a3d90'
down_revision = '03cae075a9c7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'translation_bill_category',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime),
        sa.Column('original_category_name', sa.Unicode(255), nullable=False),
        sa.Column('translation_category_name', sa.Unicode(255), nullable=False),
        sa.Column('lang_code', sa.Unicode(10), nullable=False),
        sa.Column('bill_category_id', sa.Integer, sa.ForeignKey('bill_category.id'))
    )


def downgrade():
    op.drop_table('translation_bill_category')
