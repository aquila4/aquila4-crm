revision = '4ce965ed0e21'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('plot', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('property_id', nullable=False)
        batch_op.alter_column('plot_number', nullable=False)

    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.alter_column('name', nullable=False)
        batch_op.alter_column('location', nullable=True)
        batch_op.alter_column('rows', nullable=False)
        batch_op.alter_column('columns', nullable=False)
        batch_op.alter_column('total_plots', nullable=False)