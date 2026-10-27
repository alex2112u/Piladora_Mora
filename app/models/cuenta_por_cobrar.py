from decimal import Decimal
from app.extensions import db


class CuentaPorCobrar(db.Model):
    __tablename__ = "cuentas_por_cobrar"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    concepto = db.Column(db.String(20), nullable=False)   # PILADO, ALMACENAJE, VENTA
    referencia = db.Column(db.String(50))                 # nro. de pilado, venta, etc.
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, server_default=db.func.now())
    fecha_vencimiento = db.Column(db.Date)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    estado = db.Column(db.String(10), default="PENDIENTE")  # PENDIENTE, PARCIAL, PAGADA, ANULADA

    cliente = db.relationship("Cliente")
    cobros = db.relationship("Cobro", back_populates="cuenta")

    @property
    def pagado(self):
        return sum((c.monto for c in self.cobros), Decimal("0"))

    @property
    def saldo(self):
        return self.total - self.pagado

    def actualizar_estado(self):
        if self.estado == "ANULADA":
            return
        if self.saldo <= 0:
            self.estado = "PAGADA"
        elif self.pagado > 0:
            self.estado = "PARCIAL"
        else:
            self.estado = "PENDIENTE"

    def __repr__(self):
        return f"<Cuenta {self.id} {self.concepto} {self.total}>"