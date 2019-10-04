"""new_relationship_table_for_user_and_news

Revision ID: fbfe6389c361
Revises: f062c4c50674
Create Date: 2019-10-04 09:39:04.355950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbfe6389c361'
down_revision = 'f062c4c50674'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.create_table(
            'user_news',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('positive_choice', sa.Boolean),
            sa.Column('hidden', sa.Boolean, default=False),
            sa.Column('news_id', sa.Integer, sa.ForeignKey('news.id')),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
        )
    except Exception as ex:
        print(ex)


def downgrade():
    try:
        op.drop_table('user_news')
    except Exception as ex:
        print(ex)
