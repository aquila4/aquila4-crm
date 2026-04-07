"""add property and plot tables

Revision ID: 99b70f03561a
Revises: c63ad28faadb
Create Date: 2026-04-06 17:19:22.730253

"""
from alembic import op
import sqlalchemy as sa

revision = '99b70f03561a'
down_revision = 'c63ad28faadb'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('rows', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('columns', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('total_plots', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.drop_column('total_plots')
        batch_op.drop_column('columns')
        batch_op.drop_column('rows')
        batch_op.drop_column('name')