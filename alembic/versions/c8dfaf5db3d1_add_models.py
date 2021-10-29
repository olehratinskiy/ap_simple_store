"""add models

Revision ID: c8dfaf5db3d1
Revises: 
Create Date: 2021-10-22 22:57:10.794599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8dfaf5db3d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=45), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('sold out', 'available'), nullable=True),
    sa.PrimaryKeyConstraint('item_id')
    )
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=45), nullable=False),
    sa.Column('first_name', sa.String(length=45), nullable=False),
    sa.Column('last_name', sa.String(length=45), nullable=False),
    sa.Column('email', sa.String(length=45), nullable=False),
    sa.Column('password', sa.String(length=45), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('orders',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.item_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('order_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    op.drop_table('user')
    op.drop_table('item')
    # ### end Alembic commands ###