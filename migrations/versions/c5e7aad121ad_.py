"""empty message

Revision ID: c5e7aad121ad
Revises:
Create Date: 2023-10-26 17:38:00.262032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5e7aad121ad'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_table('keyterms_generated',
    # sa.Column('id', sa.Integer(), nullable=False),
    # sa.Column('text', sa.String(length=80), nullable=False),
    # sa.Column('keyterms', sa.String(length=2000), nullable=True),
    # sa.PrimaryKeyConstraint('id')
    # )
    # op.create_table('stores',
    # sa.Column('id', sa.Integer(), nullable=False),
    # sa.Column('name', sa.String(length=80), nullable=False),
    # sa.PrimaryKeyConstraint('id'),
    # sa.UniqueConstraint('name')
    # )
    # op.create_table('users',
    # sa.Column('id', sa.Integer(), nullable=False),
    # sa.Column('username', sa.String(length=80), nullable=False),
    # sa.Column('password', sa.String(length=80), nullable=False),
    # sa.PrimaryKeyConstraint('id'),
    # sa.UniqueConstraint('username')
    # )
    # op.create_table('items',
    # sa.Column('id', sa.Integer(), nullable=False),
    # sa.Column('name', sa.String(length=80), nullable=False),
    # sa.Column('price', sa.Float(precision=2), nullable=False),
    # sa.Column('store_id', sa.Integer(), nullable=False),
    # sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    # sa.PrimaryKeyConstraint('id')
    # )
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('items')
    # op.drop_table('users')
    # op.drop_table('stores')
    # op.drop_table('keyterms_generated')
    pass
    # ### end Alembic commands ###
