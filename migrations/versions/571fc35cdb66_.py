"""empty message

Revision ID: 571fc35cdb66
Revises: d48e1b05ea71
Create Date: 2022-05-27 23:27:15.763913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '571fc35cdb66'
down_revision = 'd48e1b05ea71'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('venues', sa.Column('_genres', sa.String(), nullable=False))
    op.add_column('venues', sa.Column('_genres', sa.String(), nullable=True))
    
    op.execute("UPDATE venues SET _genres = 'Alternate' WHERE _genres IS NULL")
    
    op.alter_column('venues', '_genres', nullable=False)
    op.drop_column('venues', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('genres', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('venues', '_genres')
    # ### end Alembic commands ###
