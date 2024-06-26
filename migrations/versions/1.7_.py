"""empty message

Revision ID: 1.7
Revises: 1.6
Create Date: 2024-05-24 12:42:02.448043

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1.7'
down_revision = '1.6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('calendar')
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.drop_index('telegram_id')
        batch_op.drop_index('username')

    op.drop_table('admins')
    with op.batch_alter_table('stream_emails', schema=None) as batch_op:
        batch_op.drop_index('ix_stream_emails_id')

    op.drop_table('stream_emails')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stream_emails',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('stream_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mariadb_collate='utf8mb4_general_ci',
    mariadb_default_charset='utf8mb4',
    mariadb_engine='InnoDB'
    )
    with op.batch_alter_table('stream_emails', schema=None) as batch_op:
        batch_op.create_index('ix_stream_emails_id', ['id'], unique=False)

    op.create_table('admins',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('telegram_id', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('password_hash', mysql.VARCHAR(length=256), nullable=True),
    sa.Column('is_admin', mysql.TINYINT(display_width=1), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mariadb_collate='utf8mb4_general_ci',
    mariadb_default_charset='utf8mb4',
    mariadb_engine='InnoDB'
    )
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.create_index('username', ['username'], unique=True)
        batch_op.create_index('telegram_id', ['telegram_id'], unique=True)

    op.create_table('calendar',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('end_time', mysql.TIMESTAMP(), server_default=sa.text('current_timestamp()'), nullable=False),
    mariadb_collate='utf8mb4_general_ci',
    mariadb_default_charset='utf8mb4',
    mariadb_engine='InnoDB'
    )
    with op.batch_alter_table('calendar', schema=None) as batch_op:
        batch_op.create_index('id', ['id'], unique=True)

    # ### end Alembic commands ###
