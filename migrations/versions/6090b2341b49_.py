"""empty message

Revision ID: 6090b2341b49
Revises: b3a32cd1e077
Create Date: 2023-10-31 20:29:24.030004

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision = '6090b2341b49'
down_revision = 'b3a32cd1e077'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('twitter_comments', schema=None) as batch_op:
        batch_op.drop_index('ix_twitter_comments_index')

    op.drop_table('twitter_comments')
    with op.batch_alter_table('twitter_posts', schema=None) as batch_op:
        batch_op.drop_index('ix_twitter_posts_index')

    op.drop_table('twitter_posts')
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=mssql.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.Float(precision=2),
               type_=mssql.REAL(),
               existing_nullable=False)

    with op.batch_alter_table('twitter_posts', schema=None) as batch_op:
        batch_op.create_index('ix_twitter_posts_index', ['index'], unique=False)

    with op.batch_alter_table('twitter_comments', schema=None) as batch_op:
        batch_op.create_index('ix_twitter_comments_index', ['index'], unique=False)

    # ### end Alembic commands ###
