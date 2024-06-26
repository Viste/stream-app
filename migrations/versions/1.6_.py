"""empty message

Revision ID: 1.6
Revises: 1.5
Create Date: 2024-05-17 13:22:47.352834

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1.6'
down_revision = '1.5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course_registrations',
    sa.Column('course_id', mysql.BIGINT(display_width=20, unsigned=True), nullable=False),
    sa.Column('customer_id', mysql.BIGINT(display_width=20, unsigned=True), nullable=False),
    sa.Column('registration_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('course_id', 'customer_id')
    )
    op.drop_table('chat_members')
    with op.batch_alter_table('courses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('end_date', sa.DateTime(), nullable=True))

    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_podpivas', sa.Boolean(), nullable=False))
        batch_op.alter_column('pc_setup',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=True)

    with op.batch_alter_table('global_balance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interesting_fact', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('global_balance', schema=None) as batch_op:
        batch_op.drop_column('interesting_fact')

    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.alter_column('pc_setup',
               existing_type=sa.Text(),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.drop_column('is_podpivas')

    with op.batch_alter_table('courses', schema=None) as batch_op:
        batch_op.drop_column('end_date')
        batch_op.drop_column('start_date')

    op.create_table('chat_members',
    sa.Column('id', mysql.BIGINT(display_width=20), autoincrement=True, nullable=False),
    sa.Column('telegram_id', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('telegram_username', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('chat_name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('chat_id', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('status', mysql.VARCHAR(length=50), server_default=sa.text("'active'"), nullable=False),
    sa.Column('banned', mysql.TINYINT(display_width=1), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mariadb_collate='utf8mb4_general_ci',
    mariadb_default_charset='utf8mb4',
    mariadb_engine='InnoDB'
    )
    op.drop_table('course_registrations')
    # ### end Alembic commands ###
