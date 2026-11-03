from decimal import Decimal, InvalidOperation
from config.constantes import FORMAS_PAGO

FORMAS_CON_COMPROBANTE = ("TRANSFERENCIA", "CHEQUE")


def validar_abono(form):
    """Revisa el FORMATO del abono. Devuelve (datos_limpios, errores)."""
    errores = []

    # --- Monto ---
    monto = None
    texto = form.get("monto", "").strip().replace(",", ".")
    try:
        monto = Decimal(texto).quantize(Decimal("0.01"))
        if monto <= 0 or monto > Decimal("999999.99"):
            raise InvalidOperation
    except InvalidOperation:
        errores.append("El monto debe ser un número mayor que cero.")
        monto = None

    # --- Forma de pago ---
    forma_pago = form.get("forma_pago", "")
    if forma_pago not in FORMAS_PAGO:
        errores.append("Elige una forma de pago.")

    # --- Comprobante: obligatorio si no es efectivo ---
    comprobante = form.get("comprobante", "").strip()
    if forma_pago in FORMAS_CON_COMPROBANTE and not comprobante:
        errores.append("Escribe el número de la transferencia o del cheque.")
    if len(comprobante) > 255:
        errores.append("El comprobante es muy largo (máximo 255 caracteres).")

    # --- Observaciones ---
    observaciones = form.get("observaciones", "").strip()
    if len(observaciones) > 255:
        errores.append("Las observaciones son muy largas (máximo 255 caracteres).")

    datos = {
        "monto": monto,
        "forma_pago": forma_pago,
        "comprobante": comprobante or None,
        "observaciones": observaciones or None,
    }
    return datos, errores