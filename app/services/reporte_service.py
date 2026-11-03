from datetime import date, datetime, time, timedelta
from decimal import Decimal
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.cliente import Cliente
from app.models.cobro import Cobro
from app.models.cuenta_por_cobrar import CuentaPorCobrar
from app.models.movimiento_inventario import MovimientoInventario as Mov

ESTADOS_PENDIENTES = ("PENDIENTE", "PARCIAL")


def _dec(valor):
    """Convierte lo que devuelve la base (None, float o Decimal) en Decimal."""
    return Decimal(str(valor or 0))


def _limites(desde, hasta):
    """Del inicio del día 'desde' al inicio del día SIGUIENTE a 'hasta' (excluido)."""
    return (datetime.combine(desde, time.min),
            datetime.combine(hasta + timedelta(days=1), time.min))


def _filtro_cliente(consulta, q):
    if q:
        patron = f"%{q}%"
        consulta = consulta.filter(db.or_(
            Cliente.documento.ilike(patron),
            Cliente.nombre.ilike(patron),
        ))
    return consulta


def cobros_del_periodo(desde, hasta, forma_pago="", q=""):
    """Abonos registrados en el período. Devuelve (cobros, total, total_por_forma)."""
    inicio, fin = _limites(desde, hasta)
    consulta = (Cobro.query
                .join(CuentaPorCobrar, Cobro.cuenta_id == CuentaPorCobrar.id)
                .join(Cliente, CuentaPorCobrar.cliente_id == Cliente.id)
                .options(joinedload(Cobro.cuenta).joinedload(CuentaPorCobrar.cliente),
                         joinedload(Cobro.usuario))
                .filter(Cobro.fecha >= inicio, Cobro.fecha < fin))
    if forma_pago:
        consulta = consulta.filter(Cobro.forma_pago == forma_pago)
    consulta = _filtro_cliente(consulta, q)

    cobros = consulta.order_by(Cobro.fecha.asc(), Cobro.id.asc()).all()

    total = sum((_dec(c.monto) for c in cobros), Decimal("0"))
    por_forma = {}
    for c in cobros:
        por_forma[c.forma_pago] = por_forma.get(c.forma_pago, Decimal("0")) + _dec(c.monto)
    return cobros, total, por_forma


def deuda_pendiente(q=""):
    """Cuentas con saldo. Devuelve (filas, total, por_antiguedad).
    Cada fila es (cuenta, saldo, dias_de_antiguedad)."""
    hoy = date.today()
    consulta = (CuentaPorCobrar.query
                .join(Cliente, CuentaPorCobrar.cliente_id == Cliente.id)
                .options(joinedload(CuentaPorCobrar.cliente),
                         joinedload(CuentaPorCobrar.cobros))
                .filter(CuentaPorCobrar.estado.in_(ESTADOS_PENDIENTES)))
    consulta = _filtro_cliente(consulta, q)
    cuentas = consulta.order_by(Cliente.nombre, CuentaPorCobrar.fecha.asc()).all()

    filas = []
    rangos = {"0-30": Decimal("0"), "31-60": Decimal("0"), "61+": Decimal("0")}
    for c in cuentas:
        saldo = _dec(c.saldo)
        if saldo <= 0:
            continue
        dias = (hoy - c.fecha.date()).days if c.fecha else 0
        filas.append((c, saldo, dias))
        if dias <= 30:
            rangos["0-30"] += saldo
        elif dias <= 60:
            rangos["31-60"] += saldo
        else:
            rangos["61+"] += saldo

    total = sum((f[1] for f in filas), Decimal("0"))
    return filas, total, rangos


def resumen_bodega(desde, hasta, q=""):
    """Por cliente: saldo inicial, entradas, salidas y saldo final del período.
    Devuelve (filas, totales). Cada fila es (cliente, inicial, entradas, salidas, final)."""
    inicio, fin = _limites(desde, hasta)

    firmado = db.case((Mov.tipo == "SALIDA", -Mov.cantidad), else_=Mov.cantidad)
    en_periodo = db.and_(Mov.fecha >= inicio, Mov.fecha < fin)

    saldo_inicial = db.func.sum(db.case((Mov.fecha < inicio, firmado), else_=0))
    entradas = db.func.sum(db.case(
        (db.and_(en_periodo, Mov.tipo != "SALIDA"), Mov.cantidad), else_=0))
    salidas = db.func.sum(db.case(
        (db.and_(en_periodo, Mov.tipo == "SALIDA"), Mov.cantidad), else_=0))
    saldo_final = db.func.sum(db.case((Mov.fecha < fin, firmado), else_=0))

    consulta = (db.session.query(Cliente, saldo_inicial, entradas, salidas, saldo_final)
                .join(Mov, Mov.cliente_id == Cliente.id)
                .group_by(Cliente.id))
    consulta = _filtro_cliente(consulta, q)

    filas = []
    for cliente, ini, ent, sal, fin_saldo in consulta.order_by(Cliente.nombre).all():
        fila = (cliente, _dec(ini), _dec(ent), _dec(sal), _dec(fin_saldo))
        if any(fila[1:]):  # se omiten los clientes sin ningún movimiento ni saldo
            filas.append(fila)

    totales = tuple(sum((f[i] for f in filas), Decimal("0")) for i in range(1, 5))
    return filas, totales