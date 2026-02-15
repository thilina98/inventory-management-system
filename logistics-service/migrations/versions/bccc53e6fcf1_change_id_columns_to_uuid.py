"""Change id columns to UUID

Revision ID: bccc53e6fcf1
Revises: ec016f944df1
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bccc53e6fcf1'
down_revision = 'ec016f944df1'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Create the custom Enum type in the database
    order_status_enum = postgresql.ENUM('PENDING', 'SHIPPED', 'CANCELLED', name='orderstatus')
    order_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Now add the column using that type
    op.add_column('orders', sa.Column('status', order_status_enum, nullable=False))
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'], unique=False)

def downgrade():
    # 1. Drop the index and column
    op.drop_index(op.f('ix_orders_status'), table_name='orders')
    op.drop_column('orders', 'status')

    # 2. Drop the custom Enum type
    order_status_enum = postgresql.ENUM('PENDING', 'SHIPPED', 'CANCELLED', name='orderstatus')
    order_status_enum.drop(op.get_bind(), checkfirst=True)