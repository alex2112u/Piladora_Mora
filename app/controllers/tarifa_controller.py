from datetime import date
from flask import render_template, redirect, url_for, request, flash
from app.extensions import db
from app.models.tarifa import Tarifa
from app.validators.tarifa_validator import validar_tarifa
from config.constantes import UNIDADES_POR_SERVICIO, NOMBRES_SERVICIO


def index():
    vigentes = (Tarifa.query.filter_by(activo=True)
                .order_by(Tarifa.servicio).all())
    anteriores = (Tarifa.query.filter_by(activo=False)
                  .order_by(Tarifa.vigente_desde.desc(), Tarifa.id.desc()).all())
    return render_template("tarifas/index.html",
                           vigentes=vigentes, anteriores=anteriores,
                           unidades=UNIDADES_POR_SERVICIO,
                           nombres=NOMBRES_SERVICIO)


def crear():
    if request.method == "POST":
        datos, errores = validar_tarifa(request.form)
        if not errores:
            # Las tarifas activas anteriores del mismo servicio pasan al historial
            (Tarifa.query
             .filter_by(servicio=datos["servicio"], activo=True)
             .update({"activo": False}))

            db.session.add(Tarifa(vigente_desde=date.today(), **datos))
            db.session.commit()
            flash("Tarifa registrada. Los nuevos cobros usarán este precio.", "ok")
            return redirect(url_for("tarifas.index"))

        for e in errores:
            flash(e, "error")
        return render_template("tarifas/crear.html",
                               datos=request.form,
                               unidades=UNIDADES_POR_SERVICIO,
                               nombres=NOMBRES_SERVICIO)

    return render_template("tarifas/crear.html", datos={},
                           unidades=UNIDADES_POR_SERVICIO,
                           nombres=NOMBRES_SERVICIO)