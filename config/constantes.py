LIBRAS_POR_QUINTAL = 100

NOMBRES_SERVICIO = {
    "PILADO": "Pilado",
    "ALMACENAJE": "Almacenaje",
}

# Para cada servicio: las formas de cobrarlo permitidas.
# clave = lo que se guarda en la base de datos
# texto = lo que lee el administrador en pantalla
UNIDADES_POR_SERVICIO = {
    "PILADO": {
        "qq_pilado": f"Por quintal de arroz pilado ({LIBRAS_POR_QUINTAL} libras)",
        "lb_pilado": "Por libra de arroz pilado",
        "saco": "Por saco de arroz en cáscara",
    },
    "ALMACENAJE": {
        "saco_mes": "Por saco, cada mes",
    },
}

ETIQUETA_COBRO_CORTA = {
    "qq_pilado": "quintal",
    "lb_pilado": "libra",
    "saco": "saco",
    "saco_mes": "saco por mes",
}

NOMBRE_NEGOCIO = "Piladora"  # cámbialo por el nombre real de tu piladora