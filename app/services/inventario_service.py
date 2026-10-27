from sqlalchemy import case, func
from app.extensions import db
from app.models.movimiento_inventario import MovimientoInventario as M


def saldo_cliente(cliente_id, producto_id=None):
    """Cantidad de arroz que el cliente tiene guardado en la bodega."""
    signo = case((M.tipo == "SALIDA", -M.cantidad), else_=M.cantidad)
    q = db.session.query(func.coalesce(func.sum(signo), 0)).filter(
        M.cliente_id == cliente_id
    )
    if producto_id:
        q = q.filter(M.producto_id == producto_id)
    return q.scalar()