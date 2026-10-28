from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user
from app.extensions import db
from app.models.cliente import Cliente
from app.models.movimiento_inventario import MovimientoInventario
from app.services import bodega_service
from app.services.inventario_service import saldo_cliente
from app.validators.bodega_validator import validar_movimiento


def _clientes_con_saldo(q=""):
    """Lista de (cliente, sacos). Si hay texto q, filtra por cédula o nombre."""
    consulta = Cliente.query.filter(Cliente.activo.is_(True))
    if q:
        patron = f"%{q}%"
        consulta = consulta.filter(db.or_(
            Cliente.documento.ilike(patron),
            Cliente.nombre.ilike(patron),
        ))
    clientes = consulta.order_by(Cliente.nombre).all()
    return [(c, int(saldo_cliente(c.id))) for c in clientes]


def index():
    q = request.args.get("q", "").strip()

    # El total en custodia siempre es de TODOS los clientes, haya búsqueda o no
    todos = _clientes_con_saldo()
    total_sacos = sum(s for _, s in todos)

    if q:
        # Con búsqueda: todos los que coinciden, incluso con 0 sacos
        lista = _clientes_con_saldo(q)
    else:
        # Sin búsqueda: solo los que tienen arroz guardado, de mayor a menor
        lista = sorted([t for t in todos if t[1] > 0],
                       key=lambda t: t[1], reverse=True)

    movimientos = MovimientoInventario.query.filter(
        MovimientoInventario.cliente_id.isnot(None)
    )
    if q:
        ids = [cliente.id for cliente, _ in lista]
        movimientos = movimientos.filter(MovimientoInventario.cliente_id.in_(ids))
    ultimos = (movimientos.order_by(MovimientoInventario.fecha.desc())
               .limit(10).all())

    return render_template("bodega/index.html",
                           q=q, lista=lista,
                           total_sacos=total_sacos, ultimos=ultimos)


def registrar():
    if request.method == "POST":
        datos, errores = validar_movimiento(request.form)
        if not errores:
            bodega_service.registrar_movimiento(
                usuario_id=current_user.id, **datos
            )
            accion = "Depósito" if datos["motivo"] == "DEPOSITO" else "Retiro"
            flash(f"{accion} de {datos['sacos']} sacos registrado.", "ok")
            return redirect(url_for("bodega.historial", id=datos["cliente_id"]))

        for e in errores:
            flash(e, "error")
        return render_template("bodega/registrar.html",
                               clientes=_clientes_con_saldo(),
                               datos=request.form)

    # GET: formulario vacío (o con cliente/tipo preseleccionado por la URL)
    datos = {
        "cliente_id": request.args.get("cliente_id", ""),
        "motivo": request.args.get("motivo", "DEPOSITO"),
    }
    return render_template("bodega/registrar.html",
                           clientes=_clientes_con_saldo(), datos=datos)


def historial(id):
    cliente = db.get_or_404(Cliente, id)

    movimientos = (MovimientoInventario.query
                   .filter(MovimientoInventario.cliente_id == cliente.id)
                   .order_by(MovimientoInventario.fecha.asc(),
                             MovimientoInventario.id.asc()).all())

    # Saldo acumulado después de cada movimiento
    acumulado = 0
    filas = []
    for m in movimientos:
        cantidad = int(m.cantidad)
        acumulado += -cantidad if m.tipo == "SALIDA" else cantidad
        filas.append((m, acumulado))
    filas.reverse()  # el más reciente arriba

    return render_template("bodega/historial.html",
                           cliente=cliente, filas=filas, saldo=acumulado)