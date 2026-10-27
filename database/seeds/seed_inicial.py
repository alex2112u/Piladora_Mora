from getpass import getpass

from app import create_app
from app.extensions import db
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.categoria_producto import CategoriaProducto
from app.models.producto import Producto


def sembrar():
    # Roles
    for nombre, desc in [("Administrador", "Acceso total"),
                         ("Operador", "Bodega, pilado y cobros")]:
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre, descripcion=desc))
    db.session.commit()

    # Producto base: lo único que se guarda en bodega
    cat = CategoriaProducto.query.filter_by(nombre="Arroz").first()
    if not cat:
        cat = CategoriaProducto(nombre="Arroz")
        db.session.add(cat)
        db.session.commit()
    if not Producto.query.filter_by(nombre="Arroz en cáscara").first():
        db.session.add(Producto(nombre="Arroz en cáscara",
                                categoria_id=cat.id, unidad="saco"))
        db.session.commit()

    # Administrador
    if Usuario.query.first():
        print("Ya existen usuarios, no se crea otro administrador.")
        return

    print("Crear usuario administrador")
    nombre = input("Nombre: ").strip()
    email = input("Correo: ").strip().lower()
    password = getpass("Contraseña (no se ve al escribir): ")

    admin = Usuario(nombre=nombre, email=email,
                    rol=Rol.query.filter_by(nombre="Administrador").first())
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("Administrador creado.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        sembrar()