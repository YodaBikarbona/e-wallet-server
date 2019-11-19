"""new subcategory translation table

Revision ID: cc6d5d622628
Revises: 021af24a3d90
Create Date: 2019-11-19 16:34:23.420196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc6d5d622628'
down_revision = '021af24a3d90'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'translation_bill_sub_category',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime),
        sa.Column('original_subcategory_name', sa.Unicode(255), nullable=False),
        sa.Column('translation_subcategory_name', sa.Unicode(255), nullable=False),
        sa.Column('lang_code', sa.Unicode(10), nullable=False),
        sa.Column('bill_sub_category_id', sa.Integer, sa.ForeignKey('bill_sub_category.id'))
    )


def downgrade():
    op.drop_table('translation_bill_sub_category')
