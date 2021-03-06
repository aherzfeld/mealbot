"""empty message

Revision ID: 8133b691af02
Revises: 241d40abc6ae
Create Date: 2018-10-31 17:52:18.341269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8133b691af02'
down_revision = '241d40abc6ae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('user_created', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'user_created')
    op.drop_column('user', 'about_me')
    # ### end Alembic commands ###
