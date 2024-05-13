"""empty message

Revision ID: 1.5
Revises: 1.4
Create Date: 2024-05-13 20:59:42.881935

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1.5'
down_revision = '1.4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('global_balance', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=mysql.BIGINT(display_width=20),
               type_=sa.Numeric(precision=20, scale=4),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('global_balance', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.Numeric(precision=20, scale=4),
               type_=mysql.BIGINT(display_width=20),
               existing_nullable=True)

    # ### end Alembic commands ###
