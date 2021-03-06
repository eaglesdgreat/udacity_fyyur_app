"""empty message

Revision ID: 0581b622ec12
Revises: 571fc35cdb66
Create Date: 2022-05-28 06:27:39.933230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0581b622ec12'
down_revision = '571fc35cdb66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('genres', sa.String(), nullable=True))
    
    op.execute("UPDATE venues SET genres = 'Alternate' WHERE genres IS NULL")
    
    op.alter_column('venues', 'genres', nullable=False)
    op.drop_column('venues', '_genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('_genres', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('venues', 'genres')
    # ### end Alembic commands ###
