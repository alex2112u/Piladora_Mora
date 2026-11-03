from datetime import date, datetime, time
from decimal import Decimal
from flask import render_template
from app.extensions import db
from app.models.cliente import Cliente
from app.models.cobro import Cobro
from app.models.cuenta_por_cobrar import CuentaPorCobrar
from app.models.movimiento_inventario import MovimientoInventario
from app.models.pilado import Pilado

ESTADOS_PENDIENTES = ("PENDIENTE", "PARCIAL")


def _dec(valor):
    """Convierte lo que devuelve la base (None, float o Decimal) en Decimal."""
    return Decimal(str(valor or 0))


def _resumen_bodega():
    """Sacos guardados y cuántos clientes tienen arroz (solo clientes activos)."""
    saldo = db.func.sum(db.case(
        (MovimientoInventario.tipo == "SALIDA", -MovimientoInventario.cantidad),
        else_=MovimientoInventario.cantidad,
    ))
    filas = (db.session.query(MovimientoInventario.cliente_id, saldo)
             .join(Cliente, Cliente.id == MovimientoInventario.cliente_id)
             .filter(Cliente.activo.is_(True))
             .group_by(MovimientoInventario.cliente_id)
             .all())

    con_saldo = [s for s in (_dec(s) for _, s in filas) if s > 0]
    return int(sum(con_saldo)), len(con_saldo)


def _resumen_cobros():
    """Total por cobrar, cuentas pendientes y los 5 clientes que más deben."""
    pendiente = CuentaPorCobrar.estado.in_(ESTADOS_PENDIENTES)

    # Lo facturado por cliente en cuentas pendientes
    facturado = dict(
        db.session.query(CuentaPorCobrar.cliente_id,
                         db.func.sum(CuentaPorCobrar.total))
        .filter(pendiente)
        .group_by(CuentaPorCobrar.cliente_id).all()
    )
    # Lo que ya abonó cada cliente sobre esas mismas cuentas
    abonado = dict(
        db.session.query(CuentaPorCobrar.cliente_id,
                         db.func.sum(Cobro.monto))
        .join(Cobro, Cobro.cuenta_id == CuentaPorCobrar.id)
        .filter(pendiente)
        .group_by(CuentaPorCobrar.cliente_id).all()
    )
    cuentas_pendientes = CuentaPorCobrar.query.filter(pendiente).count()

    deudas = {cid: _dec(total) - _dec(abonado.get(cid))
              for cid, total in facturado.items()}
    deudas = {cid: d for cid, d in deudas.items() if d > 0}

    total = sum(deudas.values(), Decimal("0"))

    top_ids = sorted(deudas, key=deudas.get, reverse=True)[:5]
    clientes = {c.id: c for c in
                Cliente.query.filter(Cliente.id.in_(top_ids)).all()}
    mayores = [(clientes[i], deudas[i]) for i in top_ids]

    return total, cuentas_pendientes, mayores


def _resumen_periodo():
    """Pilados y cobros de hoy, y lo cobrado en el mes."""
    hoy = date.today()
    inicio_dia = datetime.combine(hoy, time.min)
    inicio_mes = datetime.combine(hoy.replace(day=1), time.min)

    cantidad, libras, facturado = (
        db.session.query(db.func.count(Pilado.id),
                         db.func.sum(Pilado.cantidad_arroz),
                         db.func.sum(Pilado.total))
        .filter(Pilado.fecha >= inicio_dia)
        .one()
    )
    cobrado_hoy = (db.session.query(db.func.sum(Cobro.monto))
                   .filter(Cobro.fecha >= inicio_dia).scalar())
    cobrado_mes = (db.session.query(db.func.sum(Cobro.monto))
                   .filter(Cobro.fecha >= inicio_mes).scalar())

    return (cantidad, _dec(libras), _dec(facturado),
            _dec(cobrado_hoy), _dec(cobrado_mes))


def index():
    sacos_bodega, clientes_con_arroz = _resumen_bodega()
    por_cobrar, cuentas_pendientes, mayores_deudas = _resumen_cobros()
    (pilados_hoy, libras_hoy, facturado_hoy,
     cobrado_hoy, cobrado_mes) = _resumen_periodo()

    ultimos_pilados = (Pilado.query
                       .order_by(Pilado.fecha.desc(), Pilado.id.desc())
                       .limit(5).all())
    clientes_activos = Cliente.query.filter(Cliente.activo.is_(True)).count()

    return render_template(
        "dashboard/index.html",
        hoy=date.today(),
        sacos_bodega=sacos_bodega, clientes_con_arroz=clientes_con_arroz,
        por_cobrar=por_cobrar, cuentas_pendientes=cuentas_pendientes,
        mayores_deudas=mayores_deudas,
        pilados_hoy=pilados_hoy, libras_hoy=libras_hoy,
        facturado_hoy=facturado_hoy,
        cobrado_hoy=cobrado_hoy, cobrado_mes=cobrado_mes,
        ultimos_pilados=ultimos_pilados,
        clientes_activos=clientes_activos,
    )