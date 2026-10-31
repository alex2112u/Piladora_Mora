from decimal import Decimal, InvalidOperation
from app.extensions import db
from app.models.cliente import Cliente

ORIGENES_VALIDOS = ("CUSTODIA", "EXTERNO")
MAX_LIBRAS = Decimal("1000000")
MAX_SACOS = 100000


def validar_pilado(form):
    """Revisa el FORMATO de los datos. Devuelve (datos_limpios, errores)."""
    errores = []
    cliente = None

    # --- Cliente ---
    cliente_id = form.get("cliente_id", "").strip()
    if not cliente_id.isdecimal():
        errores.append("Selecciona un cliente.")
    else:
        cliente = db.session.get(Cliente, int(cliente_id))
        if cliente is None or not cliente.activo:
            errores.append("El cliente no existe o está inactivo.")

    # --- Origen del arroz ---
    origen = form.get("origen", "")
    if origen not in ORIGENES_VALIDOS:
        errores.append("Elige si el arroz es de custodia o del cliente.")

    # --- Sacos de cáscara (vacío = 0; si hay valor, entero) ---
    sacos = 0
    texto_sacos = form.get("sacos", "").strip()
    if texto_sacos:
        if texto_sacos.isdecimal() and int(texto_sacos) <= MAX_SACOS:
            sacos = int(texto_sacos)
        else:
            errores.append("Los sacos de cáscara deben ser un número entero válido.")

    # --- Libras de arroz pilado (vacío = 0) ---
    libras = Decimal("0")
    texto_libras = form.get("libras", "").strip().replace(",", ".")
    if texto_libras:
        try:
            libras = Decimal(texto_libras).quantize(Decimal("0.01"))
            if libras < 0 or libras > MAX_LIBRAS:
                raise InvalidOperation
        except InvalidOperation:
            errores.append("Las libras de arroz pilado deben ser un número válido.")
            libras = Decimal("0")

    # --- Observaciones ---
    observaciones = form.get("observaciones", "").strip()
    if len(observaciones) > 255:
        errores.append("Las observaciones son muy largas (máximo 255 caracteres).")

    datos = {
        "cliente_id": cliente.id if cliente else None,
        "origen": origen,
        "cantidad_cascara": sacos,
        "libras_pilado": libras,
        "observaciones": observaciones or None,
    }
    return datos, errores