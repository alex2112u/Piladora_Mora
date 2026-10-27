"""arroz en custodia por cliente

Revision ID: 3bd46149f027
Revises: d9b866ec94f7
Create Date: 2026-10-26 03:47:30.496034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bd46149f027'
down_revision = 'd9b866ec94f7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('lotes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cliente_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_lotes_cliente', 'clientes', ['cliente_id'], ['id'])

    with op.batch_alter_table('movimientos_inventario', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cliente_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_movimientos_cliente', 'clientes', ['cliente_id'], ['id'])


def downgrade():
    with op.batch_alter_table('movimientos_inventario', schema=None) as batch_op:
        batch_op.drop_constraint('fk_movimientos_cliente', type_='foreignkey')
        batch_op.drop_column('cliente_id')

    with op.batch_alter_table('lotes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_lotes_cliente', type_='foreignkey')
        batch_op.drop_column('cliente_id')