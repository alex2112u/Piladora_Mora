from app.extensions import db
from app.models.cliente import Cliente
from app.services.inventario_service import saldo_cliente

MOTIVOS_VALIDOS = ("DEPOSITO", "RETIRO")


def validar_movimiento(form):
    """Devuelve (datos_limpios, lista_de_errores)."""
    errores = []
    cliente = None
    sacos = None

    # --- Cliente ---
    cliente_id = form.get("cliente_id", "").strip()
    if not cliente_id.isdecimal():
        errores.append("Selecciona un cliente.")
    else:
        cliente = db.session.get(Cliente, int(cliente_id))
        if cliente is None or not cliente.activo:
            errores.append("El cliente no existe o está inactivo.")

    # --- Tipo de movimiento ---
    motivo = form.get("motivo", "")
    if motivo not in MOTIVOS_VALIDOS:
        errores.append("Elige si es depósito o retiro.")

    # --- Cantidad de sacos ---
    texto = form.get("sacos", "").strip()
    if not texto.isdecimal() or int(texto) <= 0:
        errores.append("Los sacos deben ser un número entero mayor que cero.")
    else:
        sacos = int(texto)

    # --- Regla clave: no retirar más de lo que tiene guardado ---
    if not errores and motivo == "RETIRO":
        saldo = int(saldo_cliente(cliente.id))
        if sacos > saldo:
            errores.append(
                f"{cliente.nombre} solo tiene {saldo} sacos guardados; "
                f"no puede retirar {sacos}."
            )

    datos = {
        "cliente_id": cliente.id if cliente else None,
        "motivo": motivo,
        "sacos": sacos,
        "observaciones": form.get("observaciones", "").strip(),
    }
    return datos, errores