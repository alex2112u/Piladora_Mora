import csv
import io
from flask import Response


def respuesta_csv(nombre_archivo, encabezados, filas):
    """Arma una descarga CSV que Excel abre bien, con tildes incluidas."""
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(encabezados)
    escritor.writerows(filas)

    contenido = "\ufeff" + salida.getvalue()  # BOM: avisa a Excel que es UTF-8
    return Response(
        contenido,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )