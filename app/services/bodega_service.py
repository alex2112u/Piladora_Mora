from datetime import datetime
from app.extensions import db
from app.models.producto import Producto
from app.models.movimiento_inventario import MovimientoInventario


def producto_arroz_cascara():
    producto = Producto.query.filter_by(nombre="Arroz en cáscara").first()
    if producto is None:
        raise RuntimeError(
            "No existe el producto 'Arroz en cáscara'. Ejecuta el seed inicial."
        )
    return producto


def registrar_movimiento(cliente_id, motivo, sacos, usuario_id, observaciones=""):
    """Guarda un depósito (ENTRADA) o retiro (SALIDA) de arroz en custodia."""
    tipo = "ENTRADA" if motivo == "DEPOSITO" else "SALIDA"

    movimiento = MovimientoInventario(
        producto_id=producto_arroz_cascara().id,
        cliente_id=cliente_id,
        usuario_id=usuario_id,
        tipo=tipo,
        motivo=motivo,
        cantidad=sacos,
        observaciones=observaciones or None,
        fecha=datetime.now(),
    )
    db.session.add(movimiento)
    db.session.commit()
    return movimiento