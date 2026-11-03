NOMBRE_NEGOCIO = "Piladora La Constancia" 

LIBRAS_POR_QUINTAL = 100

NOMBRES_SERVICIO = {
    "PILADO": "Pilado (sin polvillo)",
    "PILADO_POLVILLO": "Pilado con polvillo",
    "ALMACENAJE": "Almacenaje",
}

# Para cada servicio: las formas de cobrarlo permitidas.
# clave = lo que se guarda en la base de datos
# texto = lo que lee el administrador en pantalla
_UNIDADES_PILADO = {
    "qq_pilado": f"Por quintal de arroz pilado ({LIBRAS_POR_QUINTAL} libras)",
    "lb_pilado": "Por libra de arroz pilado",
    "saco": "Por saco de arroz en cáscara",
}
UNIDADES_POR_SERVICIO = {
    "PILADO": _UNIDADES_PILADO,
    "PILADO_POLVILLO": _UNIDADES_PILADO,
    "ALMACENAJE": {"saco_mes": "Por saco, cada mes"},
}

ETIQUETA_COBRO_CORTA = {
    "qq_pilado": "quintal",
    "lb_pilado": "libra",
    "saco": "saco",
    "saco_mes": "saco por mes",
}
FORMAS_PAGO = {
    "EFECTIVO": "Efectivo",
    "TRANSFERENCIA": "Transferencia",
    "CHEQUE": "Cheque",
}
