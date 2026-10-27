from decimal import Decimal, InvalidOperation
from app.models.cliente import Cliente


def validar_cliente(form, cliente_id=None):
    """Devuelve (datos_limpios, lista_de_errores)."""
    errores = []

    nombre = form.get("nombre", "").strip()
    documento = form.get("documento", "").strip() or None
    telefono = form.get("telefono", "").strip() or None
    email = form.get("email", "").strip() or None
    direccion = form.get("direccion", "").strip() or None
    limite_texto = form.get("limite_credito", "").strip() or "0"

    if not nombre:
        errores.append("El nombre es obligatorio.")

    if email and ("@" not in email or "." not in email.split("@")[-1]):
        errores.append("El correo no es válido.")

    try:
        limite = Decimal(limite_texto.replace(",", "."))
        if not limite.is_finite() or limite < 0:
            raise InvalidOperation
    except InvalidOperation:
        errores.append("El límite de crédito debe ser un número mayor o igual a 0.")
        limite = Decimal("0")

    if documento:
        repetido = Cliente.query.filter(Cliente.documento == documento)
        if cliente_id:  # al editar, no compararse consigo mismo
            repetido = repetido.filter(Cliente.id != cliente_id)
        if repetido.first():
            errores.append("Ya existe un cliente con ese documento.")

    datos = {
        "nombre": nombre,
        "documento": documento,
        "telefono": telefono,
        "email": email,
        "direccion": direccion,
        "limite_credito": limite,
    }
    return datos, errores