from app.extensions import db


class CategoriaProducto(db.Model):
    __tablename__ = "categorias_producto"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))

    def __repr__(self):
        return f"<Categoria {self.nombre}>"