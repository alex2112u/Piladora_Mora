from decimal import Decimal
from flask import render_template, redirect, url_for, request, flash
from app.extensions import db
from app.models.cliente import Cliente
from app.models.cuenta_por_cobrar import CuentaPorCobrar
from app.services.inventario_service import saldo_cliente
from app.validators.cliente_validator import validar_cliente


def index():
    q = request.args.get("q", "").strip()
    estado = request.args.get("estado", "activos")

    consulta = Cliente.query
    if q:
        patron = f"%{q}%"
        consulta = consulta.filter(db.or_(
            Cliente.nombre.ilike(patron),
            Cliente.documento.ilike(patron),
            Cliente.telefono.ilike(patron),
        ))
    if estado == "activos":
        consulta = consulta.filter(Cliente.activo.is_(True))
    elif estado == "inactivos":
        consulta = consulta.filter(Cliente.activo.is_(False))

    clientes = consulta.order_by(Cliente.nombre).all()
    return render_template("clientes/index.html",
                           clientes=clientes, q=q, estado=estado)


def crear():
    if request.method == "POST":
        datos, errores = validar_cliente(request.form)
        if not errores:
            cliente = Cliente(**datos)
            db.session.add(cliente)
            db.session.commit()
            flash("Cliente creado.", "ok")
            return redirect(url_for("clientes.detalle", id=cliente.id))
        for e in errores:
            flash(e, "error")
        return render_template("clientes/crear.html", datos=request.form)

    return render_template("clientes/crear.html", datos={})


def detalle(id):
    cliente = db.get_or_404(Cliente, id)
    sacos = saldo_cliente(cliente.id)
    cuentas = CuentaPorCobrar.query.filter(
        CuentaPorCobrar.cliente_id == cliente.id,
        CuentaPorCobrar.estado != "ANULADA",
    ).all()
    deuda = sum((c.saldo for c in cuentas), Decimal("0"))
    return render_template("clientes/detalle.html",
                           cliente=cliente, sacos=sacos, deuda=deuda)


def editar(id):
    cliente = db.get_or_404(Cliente, id)

    if request.method == "POST":
        datos, errores = validar_cliente(request.form, cliente_id=cliente.id)
        if not errores:
            for campo, valor in datos.items():
                setattr(cliente, campo, valor)
            db.session.commit()
            flash("Cliente actualizado.", "ok")
            return redirect(url_for("clientes.detalle", id=cliente.id))
        for e in errores:
            flash(e, "error")
        return render_template("clientes/editar.html",
                               cliente=cliente, datos=request.form)

    datos = {
        "nombre": cliente.nombre,
        "documento": cliente.documento,
        "telefono": cliente.telefono,
        "email": cliente.email,
        "direccion": cliente.direccion,
        "limite_credito": cliente.limite_credito,
    }
    return render_template("clientes/editar.html", cliente=cliente, datos=datos)


def cambiar_estado(id):
    cliente = db.get_or_404(Cliente, id)
    cliente.activo = not cliente.activo
    db.session.commit()
    flash("Cliente activado." if cliente.activo else "Cliente desactivado.", "ok")
    return redirect(url_for("clientes.detalle", id=cliente.id))