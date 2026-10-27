from app.extensions import db


class Cobro(db.Model):
    __tablename__ = "cobros"

    id = db.Column(db.Integer, primary_key=True)
    cuenta_id = db.Column(db.Integer, db.ForeignKey("cuentas_por_cobrar.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    fecha = db.Column(db.DateTime, server_default=db.func.now())
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    forma_pago = db.Column(db.String(20), default="EFECTIVO")  # EFECTIVO, TRANSFERENCIA, CHEQUE
    comprobante = db.Column(db.String(255))                    # archivo o nro. de transferencia
    observaciones = db.Column(db.String(255))

    cuenta = db.relationship("CuentaPorCobrar", back_populates="cobros")
    usuario = db.relationship("Usuario")

    def __repr__(self):
        return f"<Cobro {self.monto}>"