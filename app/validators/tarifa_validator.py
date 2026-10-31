from decimal import Decimal, InvalidOperation
from config.constantes import UNIDADES_POR_SERVICIO


def validar_tarifa(form):
    """Devuelve (datos_limpios, lista_de_errores)."""
    errores = []

    # --- Servicio y unidad vienen juntos: "PILADO:qq_pilado" ---
    tipo = form.get("tipo", "")
    servicio, _, unidad = tipo.partition(":")
    if servicio not in UNIDADES_POR_SERVICIO or \
            unidad not in UNIDADES_POR_SERVICIO[servicio]:
        errores.append("Elige qué servicio se cobra y en qué unidad.")

    # --- Precio ---
    precio = None
    texto = form.get("precio", "").strip().replace(",", ".")
    try:
        precio = Decimal(texto).quantize(Decimal("0.01"))
        if precio <= 0 or precio > Decimal("9999.99"):
            raise InvalidOperation
    except InvalidOperation:
        errores.append("El precio debe ser un número mayor que cero (máximo 9999.99).")
        precio = None

    datos = {"servicio": servicio, "unidad": unidad, "precio": precio}
    return datos, errores