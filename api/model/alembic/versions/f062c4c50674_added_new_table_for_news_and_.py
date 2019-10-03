"""added new table for news and information (pool)

Revision ID: f062c4c50674
Revises: 51d22c9ec079
Create Date: 2019-10-03 16:06:14.810383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f062c4c50674'
down_revision = '51d22c9ec079'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.create_table(
            'news',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('created', sa.DateTime),
            sa.Column('title', sa.Unicode(255), nullable=False),
            sa.Column('content', sa.Unicode(500), nullable=False),
            sa.Column('type', sa.Unicode(255), nullable=False),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
        )
    except Exception as ex:
        print(ex)


def downgrade():
    try:
        op.drop_table('news')
    except Exception as ex:
        print(ex)
