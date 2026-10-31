from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from app.extensions import db
from app.models.tarifa import Tarifa
from app.models.pilado import Pilado
from app.models.cuenta_por_cobrar import CuentaPorCobrar
from app.models.movimiento_inventario import MovimientoInventario
from app.services.inventario_service import saldo_cliente
from config.constantes import LIBRAS_POR_QUINTAL, ETIQUETA_COBRO_CORTA


def _tarifa_pilado():
    return (
        Tarifa.query.filter_by(servicio="PILADO", activo=True)
        .order_by(Tarifa.vigente_desde.desc(), Tarifa.id.desc())
        .first()
    )


def calcular_total_pilado(unidad, precio, libras_pilado, sacos_cascara):
    """Total a cobrar según la unidad de la tarifa."""
    if unidad == "qq_pilado":
        cantidad = libras_pilado / LIBRAS_POR_QUINTAL
    elif unidad == "lb_pilado":
        cantidad = libras_pilado
    elif unidad == "saco":
        cantidad = sacos_cascara
    else:
        raise ValueError(
            f"La unidad '{unidad}' no sirve para cobrar pilado. "
            "Registra una tarifa nueva en Tarifas."
        )
    return (cantidad * precio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def registrar_pilado(cliente_id, origen, libras_pilado=0, cantidad_cascara=0,
                     cantidad_polvillo=0, cantidad_tamo=0,
                     producto_cascara_id=None, usuario_id=None,
                     observaciones=None):
    """
    Registra un pilado y genera su cuenta por cobrar.
    origen: "CUSTODIA" (arroz guardado en bodega) o "EXTERNO" (lo trae el cliente).
    libras_pilado: libras de arroz pilado que se lleva el cliente.
    cantidad_cascara: sacos de cáscara que entran a la máquina.
    """
    origen = origen.upper()
    if origen not in ("CUSTODIA", "EXTERNO"):
        raise ValueError("El origen debe ser CUSTODIA o EXTERNO")

    libras = Decimal(str(libras_pilado))
    sacos = Decimal(str(cantidad_cascara))
    if libras < 0 or sacos < 0:
        raise ValueError("Las cantidades no pueden ser negativas")

    tarifa = _tarifa_pilado()
    if tarifa is None:
        raise ValueError("No hay tarifa de pilado configurada")
    precio = Decimal(str(tarifa.precio))

    # Qué dato es obligatorio depende de cómo se cobra
    if tarifa.unidad in ("qq_pilado", "lb_pilado") and libras <= 0:
        raise ValueError("Indica las libras de arroz pilado")
    if tarifa.unidad == "saco" and sacos <= 0:
        raise ValueError("Indica los sacos de arroz en cáscara")

    if origen == "CUSTODIA":
        if sacos <= 0:
            raise ValueError("Indica cuántos sacos de cáscara salen de la bodega")
        if producto_cascara_id is None:
            raise ValueError("Indica el producto arroz en cáscara")
        disponible = Decimal(str(saldo_cliente(cliente_id, producto_cascara_id)))
        if sacos > disponible:
            raise ValueError(f"El cliente solo tiene {int(disponible)} sacos guardados")

    total = calcular_total_pilado(tarifa.unidad, precio, libras, sacos)
    ahora = datetime.now()

    if tarifa.unidad == "saco":
        detalle = f"{sacos:g} sacos"
    else:
        detalle = f"{libras:g} lb"
    etiqueta = ETIQUETA_COBRO_CORTA.get(tarifa.unidad, tarifa.unidad)

    try:
        pilado = Pilado(
            cliente_id=cliente_id,
            usuario_id=usuario_id,
            origen=origen,
            fecha=ahora,
            cantidad_cascara=sacos,
            cantidad_arroz=libras,
            cantidad_polvillo=Decimal(str(cantidad_polvillo)),
            cantidad_tamo=Decimal(str(cantidad_tamo)),
            precio_unitario=precio,
            unidad_cobro=tarifa.unidad,
            total=total,
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
                cantidad=sacos,
                referencia=f"PIL-{pilado.id}",
                fecha=ahora,
            ))

        # El pilado se cobra siempre, sea custodia o externo
        cuenta = CuentaPorCobrar(
            cliente_id=cliente_id,
            concepto="PILADO",
            referencia=f"PIL-{pilado.id}",
            descripcion=f"Pilado {origen.lower()}: {detalle} a ${precio} por {etiqueta}",
            fecha=ahora,
            total=total,
        )
        db.session.add(cuenta)
        db.session.flush()
        pilado.cuenta_id = cuenta.id

        db.session.commit()
        return pilado
    except Exception:
        db.session.rollback()
        raise