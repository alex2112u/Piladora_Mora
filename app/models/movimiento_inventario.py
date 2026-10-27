from app.extensions import db


class MovimientoInventario(db.Model):
    __tablename__ = "movimientos_inventario"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    lote_id = db.Column(db.Integer, db.ForeignKey("lotes.id"))
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"))  # de quién es el arroz
    tipo = db.Column(db.String(10), nullable=False)    # ENTRADA, SALIDA, AJUSTE
    motivo = db.Column(db.String(30))                  # compra, pilado, venta, ajuste
    cantidad = db.Column(db.Numeric(12, 2), nullable=False)
    referencia = db.Column(db.String(50))              # nro. de venta, recepción, etc.
    observaciones = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, server_default=db.func.now())

    producto = db.relationship("Producto", back_populates="movimientos")
    lote = db.relationship("Lote", back_populates="movimientos")
    usuario = db.relationship("Usuario")
    cliente = db.relationship("Cliente")

    def __repr__(self):
        return f"<Movimiento {self.tipo} {self.cantidad}>"