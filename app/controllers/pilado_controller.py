from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user
from app.extensions import db
from app.models.cliente import Cliente
from app.models.pilado import Pilado
from app.controllers.bodega_controller import _clientes_con_saldo
from app.services.bodega_service import producto_arroz_cascara
from app.services.pilado_service import registrar_pilado, tarifa_pilado
from app.validators.pilado_validator import validar_pilado
from config.constantes import (
    ETIQUETA_COBRO_CORTA, LIBRAS_POR_QUINTAL, NOMBRE_NEGOCIO,
)


def _mostrar_formulario(datos):
    return render_template("pilado/nuevo.html",
                           clientes=_clientes_con_saldo(),
                           datos=datos,
                           tarifa=tarifa_pilado(),
                           etiquetas=ETIQUETA_COBRO_CORTA)


def index():
    q = request.args.get("q", "").strip()

    consulta = Pilado.query.join(Cliente, Pilado.cliente_id == Cliente.id)
    if q:
        patron = f"%{q}%"
        consulta = consulta.filter(db.or_(
            Cliente.documento.ilike(patron),
            Cliente.nombre.ilike(patron),
        ))
    pilados = (consulta.order_by(Pilado.fecha.desc(), Pilado.id.desc())
               .limit(50).all())

    return render_template("pilado/index.html", pilados=pilados, q=q,
                           etiquetas=ETIQUETA_COBRO_CORTA)


def nuevo():
    if request.method == "POST":
        datos, errores = validar_pilado(request.form)

        if not errores:
            try:
                pilado = registrar_pilado(
                    usuario_id=current_user.id,
                    producto_cascara_id=producto_arroz_cascara().id,
                    **datos,
                )
                flash(f"Pilado registrado. Total a cobrar: ${pilado.total}.", "ok")
                return redirect(url_for("pilado.ticket", id=pilado.id))
            except (ValueError, RuntimeError) as e:
                errores = [str(e)]

        for e in errores:
            flash(e, "error")
        return _mostrar_formulario(request.form)

    # GET: formulario vacío, o con cliente/origen preseleccionados por la URL
    datos = {
        "cliente_id": request.args.get("cliente_id", ""),
        "origen": request.args.get("origen", "CUSTODIA"),
    }
    return _mostrar_formulario(datos)


def ticket(id):
    pilado = db.get_or_404(Pilado, id)
    return render_template("pilado/ticket.html", p=pilado,
                           etiquetas=ETIQUETA_COBRO_CORTA,
                           libras_por_quintal=LIBRAS_POR_QUINTAL,
                           negocio=NOMBRE_NEGOCIO)