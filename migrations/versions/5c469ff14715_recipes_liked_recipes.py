"""recipes & liked_recipes

Revision ID: 5c469ff14715
Revises: 3e7bcdf3c0c6
Create Date: 2018-10-09 11:22:36.343799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c469ff14715'
down_revision = '3e7bcdf3c0c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_json', sa.JSON(), nullable=True),
    sa.Column('added_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['added_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('liked_recipes',
    sa.Column('liker_id', sa.Integer(), nullable=True),
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['liker_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('liked_recipes')
    op.drop_table('recipe')
    # ### end Alembic commands ###
