"""empty message

Revision ID: 2d4e6d170a9
Revises: 31b9735458e
Create Date: 2016-12-31 14:32:00.820335

"""

# revision identifiers, used by Alembic.
revision = '2d4e6d170a9'
down_revision = '31b9735458e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quest_judge',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('exam_id', sa.Integer(), nullable=True),
    sa.Column('quest_no', sa.Integer(), nullable=True),
    sa.Column('quest_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('operator_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('quest_judge')
    ### end Alembic commands ###
