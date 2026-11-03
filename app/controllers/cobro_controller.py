from datetime import datetime
from decimal import Decimal
from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user
from app.extensions import db
from app.models.cliente import Cliente
from app.models.cuenta_por_cobrar import CuentaPorCobrar
from app.services.cobro_service import registrar_cobro
from app.validators.cobro_validator import validar_abono
from config.constantes import FORMAS_PAGO

ESTADOS_PENDIENTES = ("PENDIENTE", "PARCIAL")


def index():
    q = request.args.get("q", "").strip()
    estado = request.args.get("estado", "pendientes")

    consulta = CuentaPorCobrar.query.join(
        Cliente, CuentaPorCobrar.cliente_id == Cliente.id
    )
    if estado == "pendientes":
        consulta = consulta.filter(CuentaPorCobrar.estado.in_(ESTADOS_PENDIENTES))
    elif estado == "pagadas":
        consulta = consulta.filter(CuentaPorCobrar.estado == "PAGADA")

    if q:
        patron = f"%{q}%"
        consulta = consulta.filter(db.or_(
            Cliente.documento.ilike(patron),
            Cliente.nombre.ilike(patron),
        ))

    cuentas = (consulta.order_by(CuentaPorCobrar.fecha.desc(), CuentaPorCobrar.id.desc())
        .limit(200).all())

    # El total por cobrar es de TODAS las pendientes, con o sin filtro
    pendientes = (CuentaPorCobrar.query
                .filter(CuentaPorCobrar.estado.in_(ESTADOS_PENDIENTES)).all())
    total_por_cobrar = sum((c.saldo for c in pendientes), Decimal("0"))

    return render_template("cobros/index.html", cuentas=cuentas, q=q, estado=estado, total_por_cobrar=total_por_cobrar,
    cantidad_pendientes=len(pendientes))


def cuenta(id):
    cuenta = db.get_or_404(CuentaPorCobrar, id)

    if request.method == "POST":
        datos, errores = validar_abono(request.form)
        if not errores:
            try:
                registrar_cobro(cuenta_id=cuenta.id,
                                usuario_id=current_user.id, **datos)
                flash(f"Abono de ${datos['monto']} registrado.", "ok")
                return redirect(url_for("cobros.cuenta", id=cuenta.id))
            except ValueError as e:
                errores = [str(e)]

        for e in errores:
            flash(e, "error")
        formulario = request.form
    else:
        formulario = {"forma_pago": "EFECTIVO"}

    abonos = sorted(cuenta.cobros,
                    key=lambda c: (c.fecha or datetime.min, c.id), reverse=True)

    return render_template("cobros/cuenta.html", cuenta=cuenta, abonos=abonos, formas=FORMAS_PAGO, datos=formulario)