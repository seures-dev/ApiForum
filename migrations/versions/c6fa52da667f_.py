"""empty message

Revision ID: c6fa52da667f
Revises: a67bcb1a20a7
Create Date: 2024-02-04 06:03:49.136379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6fa52da667f'
down_revision = 'a67bcb1a20a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('into_branch_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('into_branch_id', sa.INTEGER(), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
