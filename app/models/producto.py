from app.extensions import db


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True)
    nombre = db.Column(db.String(120), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_producto.id"))
    unidad = db.Column(db.String(20), default="saco")  # saco, qq, kg
    peso_unidad_kg = db.Column(db.Numeric(10, 2))      # kg por saco o quintal
    precio_venta = db.Column(db.Numeric(12, 2), default=0)
    stock_minimo = db.Column(db.Numeric(12, 2), default=0)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    categoria = db.relationship("CategoriaProducto")
    lotes = db.relationship("Lote", back_populates="producto")
    movimientos = db.relationship("MovimientoInventario", back_populates="producto")

    def __repr__(self):
        return f"<Producto {self.nombre}>"