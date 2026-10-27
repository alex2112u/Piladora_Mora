from decimal import Decimal
from app.extensions import db
from app.models.tarifa import Tarifa
from app.models.pilado import Pilado
from app.models.cuenta_por_cobrar import CuentaPorCobrar
from app.models.movimiento_inventario import MovimientoInventario
from app.services.inventario_service import saldo_cliente


def _tarifa_pilado():
    return (
        Tarifa.query.filter_by(servicio="PILADO", activo=True)
        .order_by(Tarifa.vigente_desde.desc(), Tarifa.id.desc())
        .first()
    )


def registrar_pilado(cliente_id, origen, cantidad_cascara,
                     cantidad_arroz=0, cantidad_polvillo=0, cantidad_tamo=0,
                     producto_cascara_id=None, usuario_id=None,
                     observaciones=None):
    """
    Registra un pilado y genera su cuenta por cobrar.
    origen: "CUSTODIA" (arroz guardado en bodega) o "EXTERNO" (lo trae el cliente).
    """
    origen = origen.upper()
    if origen not in ("CUSTODIA", "EXTERNO"):
        raise ValueError("El origen debe ser CUSTODIA o EXTERNO")

    cascara = Decimal(str(cantidad_cascara))
    if cascara <= 0:
        raise ValueError("La cantidad de cáscara debe ser mayor a cero")

    tarifa = _tarifa_pilado()
    if tarifa is None:
        raise ValueError("No hay tarifa de pilado configurada")

    if origen == "CUSTODIA":
        if producto_cascara_id is None:
            raise ValueError("Indica el producto arroz en cáscara")
        disponible = Decimal(str(saldo_cliente(cliente_id, producto_cascara_id)))
        if cascara > disponible:
            raise ValueError(f"El cliente solo tiene {disponible} guardado")

    try:
        pilado = Pilado(
            cliente_id=cliente_id,
            usuario_id=usuario_id,
            origen=origen,
            cantidad_cascara=cascara,
            cantidad_arroz=Decimal(str(cantidad_arroz)),
            cantidad_polvillo=Decimal(str(cantidad_polvillo)),
            cantidad_tamo=Decimal(str(cantidad_tamo)),
            precio_unitario=tarifa.precio,
            total=cascara * tarifa.precio,
            observaciones=observaciones,
        )
        db.session.add(pilado)
        db.session.flush()  # genera el id del pilado

        # Solo el arroz de custodia sale del inventario
        if origen == "CUSTODIA":
            db.session.add(MovimientoInventario(
                producto_id=producto_cascara_id,
                cliente_id=cliente_id,
                usuario_id=usuario_id,
                tipo="SALIDA",
                motivo="PILADO",
                cantidad=cascara,
                referencia=f"PIL-{pilado.id}",
            ))

        # El pilado se cobra siempre, sea custodia o externo
        cuenta = CuentaPorCobrar(
            cliente_id=cliente_id,
            concepto="PILADO",
            referencia=f"PIL-{pilado.id}",
            descripcion=f"Pilado {origen.lower()}: {cascara} x {tarifa.precio}",
            total=pilado.total,
        )
        db.session.add(cuenta)
        db.session.flush()
        pilado.cuenta_id = cuenta.id

        db.session.commit()
        return pilado
    except Exception:
        db.session.rollback()
        raise