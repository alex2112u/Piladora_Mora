from datetime import date, datetime
from flask import render_template, request, flash
from app.helpers.csv_helper import respuesta_csv
from app.services import reporte_service
from config.constantes import FORMAS_PAGO


def _fecha(texto, defecto):
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return defecto


def _periodo():
    """Lee desde/hasta de la URL. Por defecto: del día 1 del mes hasta hoy."""
    hoy = date.today()
    desde = _fecha(request.args.get("desde"), hoy.replace(day=1))
    hasta = _fecha(request.args.get("hasta"), hoy)
    if desde > hasta:
        desde, hasta = hasta, desde
        flash("Las fechas estaban al revés y se intercambiaron.", "error")
    return desde, hasta


def _es_csv():
    return request.args.get("formato") == "csv"


def index():
    return render_template("reportes/index.html")


def cobros():
    desde, hasta = _periodo()
    forma = request.args.get("forma_pago", "")
    if forma not in FORMAS_PAGO:
        forma = ""
    q = request.args.get("q", "").strip()

    filas, total, por_forma = reporte_service.cobros_del_periodo(desde, hasta, forma, q)

    if _es_csv():
        lineas = [[
            c.fecha.strftime("%d/%m/%Y %H:%M") if c.fecha else "",
            c.cuenta.cliente.nombre,
            c.cuenta.cliente.documento or "",
            c.cuenta.referencia or "",
            FORMAS_PAGO.get(c.forma_pago, c.forma_pago),
            c.comprobante or "",
            f"{c.monto:.2f}",
            c.usuario.nombre if c.usuario else "",
        ] for c in filas]
        return respuesta_csv(
            f"cobros_{desde}_{hasta}.csv",
            ["Fecha y hora", "Cliente", "Cédula", "Cuenta", "Forma de pago",
             "Comprobante", "Monto", "Registró"],
            lineas)

    return render_template("reportes/cobros.html", desde=desde, hasta=hasta,
                           forma=forma, q=q, filas=filas, total=total,
                           por_forma=por_forma, formas=FORMAS_PAGO,
                           generado=datetime.now())


def deuda():
    q = request.args.get("q", "").strip()
    filas, total, rangos = reporte_service.deuda_pendiente(q)

    if _es_csv():
        lineas = [[
            c.cliente.nombre,
            c.cliente.documento or "",
            c.referencia or "",
            c.concepto,
            c.fecha.strftime("%d/%m/%Y") if c.fecha else "",
            f"{c.total:.2f}",
            f"{c.pagado:.2f}",
            f"{saldo:.2f}",
            dias,
        ] for c, saldo, dias in filas]
        return respuesta_csv(
            f"deuda_{date.today()}.csv",
            ["Cliente", "Cédula", "Referencia", "Concepto", "Fecha",
             "Total", "Pagado", "Saldo", "Días"],
            lineas)

    return render_template("reportes/deuda.html", q=q, filas=filas, total=total,
                           rangos=rangos, generado=datetime.now())


def bodega():
    desde, hasta = _periodo()
    q = request.args.get("q", "").strip()
    filas, totales = reporte_service.resumen_bodega(desde, hasta, q)

    if _es_csv():
        lineas = [[
            cliente.nombre,
            cliente.documento or "",
            "Activo" if cliente.activo else "Inactivo",
            f"{ini:g}", f"{ent:g}", f"{sal:g}", f"{fin:g}",
        ] for cliente, ini, ent, sal, fin in filas]
        return respuesta_csv(
            f"bodega_{desde}_{hasta}.csv",
            ["Cliente", "Cédula", "Estado", "Saldo inicial", "Entradas",
             "Salidas", "Saldo final"],
            lineas)

    return render_template("reportes/bodega.html", desde=desde, hasta=hasta,
                           q=q, filas=filas, totales=totales,
                           generado=datetime.now())