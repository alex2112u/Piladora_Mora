from app.extensions import db


class Lote(db.Model):
    __tablename__ = "lotes"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"))
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"))  # dueño si es arroz en custodia
    fecha_ingreso = db.Column(db.Date, server_default=db.func.current_date())
    cantidad_inicial = db.Column(db.Numeric(12, 2), nullable=False)
    cantidad_actual = db.Column(db.Numeric(12, 2), nullable=False)
    costo_unitario = db.Column(db.Numeric(12, 2), default=0)
    humedad = db.Column(db.Numeric(5, 2))  # % de humedad al recibir
    observaciones = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)

    producto = db.relationship("Producto", back_populates="lotes")
    proveedor = db.relationship("Proveedor")
    cliente = db.relationship("Cliente")
    movimientos = db.relationship("MovimientoInventario", back_populates="lote")

    def __repr__(self):
        return f"<Lote {self.codigo}>"