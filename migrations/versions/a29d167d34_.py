"""empty message

Revision ID: a29d167d34
Revises: 4ab6d39eefb
Create Date: 2017-08-23 20:58:10.568213

"""

# revision identifiers, used by Alembic.
revision = 'a29d167d34'
down_revision = '4ab6d39eefb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('exam', sa.Column('is_fast', sa.Integer(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('exam', 'is_fast')
    ### end Alembic commands ###