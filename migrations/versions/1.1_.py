"""empty message

Revision ID: 1.1
Revises: 1.0
Create Date: 2024-05-06 23:46:17.856924

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1.1'
down_revision = '1.0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('avatar_url', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('city', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('headphones', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('sound_card', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('pc_setup', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.drop_column('pc_setup')
        batch_op.drop_column('sound_card')
        batch_op.drop_column('headphones')
        batch_op.drop_column('city')
        batch_op.drop_column('avatar_url')

    # ### end Alembic commands ###
