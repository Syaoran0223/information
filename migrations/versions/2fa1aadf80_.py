"""empty message

Revision ID: 2fa1aadf80
Revises: 2d4e6d170a9
Create Date: 2016-12-31 15:29:16.940806

"""

# revision identifiers, used by Alembic.
revision = '2fa1aadf80'
down_revision = '2d4e6d170a9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quest', sa.Column('answer_list1', sa.Text(), nullable=True))
    op.add_column('quest', sa.Column('answer_list2', sa.Text(), nullable=True))
    op.add_column('quest', sa.Column('correct_answer1', sa.Text(), nullable=True))
    op.add_column('quest', sa.Column('options1', sa.Text(), nullable=True))
    op.add_column('quest', sa.Column('options2', sa.Text(), nullable=True))
    op.add_column('quest', sa.Column('sub_items1', sa.Text(), nullable=True))
    op.add_column('quest', sa.Column('sub_items2', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('quest', 'sub_items2')
    op.drop_column('quest', 'sub_items1')
    op.drop_column('quest', 'options2')
    op.drop_column('quest', 'options1')
    op.drop_column('quest', 'correct_answer1')
    op.drop_column('quest', 'answer_list2')
    op.drop_column('quest', 'answer_list1')
    ### end Alembic commands ###