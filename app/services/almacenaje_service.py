from datetime import date
from decimal import Decimal
from app.extensions import db
from app.models.tarifa import Tarifa
from app.models.cuenta_por_cobrar import CuentaPorCobrar
from app.services.inventario_service import saldo_cliente
from app.models.movimiento_inventario import MovimientoInventario

def tarifa_vigente(servicio):
    return (
        Tarifa.query.filter_by(servicio=servicio, activo=True)
        .order_by(Tarifa.vigente_desde.desc(), Tarifa.id.desc())
        .first()
    )


def generar_cobro_almacenaje(cliente_id, producto_id=None, fecha=None):
    """Genera la cuenta por cobrar del mes por los sacos guardados."""
    hoy = fecha or date.today()
    referencia = f"ALM-{cliente_id}-{hoy.strftime('%Y-%m')}"

    ya_existe = (
        CuentaPorCobrar.query.filter_by(referencia=referencia)
        .filter(CuentaPorCobrar.estado != "ANULADA")
        .first()
    )
    if ya_existe:
        raise ValueError("Ya se generó el cobro de almacenaje de este mes")

    sacos = Decimal(str(saldo_cliente(cliente_id, producto_id)))
    if sacos <= 0:
        raise ValueError("El cliente no tiene arroz guardado")

    tarifa = tarifa_vigente("ALMACENAJE")
    if tarifa is None:
        raise ValueError("No hay tarifa de almacenaje configurada")

    cuenta = CuentaPorCobrar(
        cliente_id=cliente_id,
        concepto="ALMACENAJE",
        referencia=referencia,
        descripcion=f"Almacenaje {hoy.strftime('%m/%Y')}: {sacos} sacos x {tarifa.precio}",
        total=sacos * tarifa.precio,
    )
    db.session.add(cuenta)
    db.session.commit()
    return cuenta

def generar_cobros_del_mes(fecha=None):
    """Genera el cobro de almacenaje de todos los clientes con arroz guardado."""
    ids = [
        fila[0]
        for fila in db.session.query(MovimientoInventario.cliente_id)
        .filter(MovimientoInventario.cliente_id.isnot(None))
        .distinct()
    ]
    generadas, omitidas = [], []
    for cliente_id in ids:
        try:
            generadas.append(generar_cobro_almacenaje(cliente_id, fecha=fecha))
        except ValueError as e:
            omitidas.append((cliente_id, str(e)))
    return generadas, omitidas