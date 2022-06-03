"""empty message

Revision ID: 2d18568343ff
Revises: 53ae74461f4a
Create Date: 2022-05-28 16:37:23.103915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d18568343ff'
down_revision = '53ae74461f4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('uid', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'uid')
    # ### end Alembic commands ###