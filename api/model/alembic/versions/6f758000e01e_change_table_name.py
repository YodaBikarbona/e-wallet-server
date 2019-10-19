"""change table name

Revision ID: 6f758000e01e
Revises: ff9dc542fe6e
Create Date: 2019-10-19 16:52:47.399641

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f758000e01e'
down_revision = 'ff9dc542fe6e'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('user', 'users')
    op.execute('ALTER SEQUENCE user_id_seq RENAME TO users_id_seq')
    op.execute('ALTER INDEX user_pkey RENAME TO users_pkey')


def downgrade():
    op.rename_table('users', 'user')
    op.execute('ALTER SEQUENCE users_id_seq RENAME TO user_id_seq')
    op.execute('ALTER INDEX users_pkey RENAME TO user_pkey')
