from app.extensions import db


class Pilado(db.Model):
    __tablename__ = "pilados"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    cuenta_id = db.Column(db.Integer, db.ForeignKey("cuentas_por_cobrar.id"))
    origen = db.Column(db.String(10), nullable=False)      # CUSTODIA o EXTERNO
    fecha = db.Column(db.DateTime, server_default=db.func.now())

    cantidad_cascara = db.Column(db.Numeric(12, 2), nullable=False)  # SACOS de cáscara que entran
    cantidad_arroz = db.Column(db.Numeric(12, 2), default=0)  
    cantidad_polvillo = db.Column(db.Numeric(12, 2), default=0)
    cantidad_tamo = db.Column(db.Numeric(12, 2), default=0)

    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    unidad_cobro = db.Column(db.String(20))  # unidad de la tarifa usada: qq_pilado, lb_pilado, saco
    total = db.Column(db.Numeric(12, 2), nullable=False)
    observaciones = db.Column(db.String(255))

    cliente = db.relationship("Cliente")
    usuario = db.relationship("Usuario")
    cuenta = db.relationship("CuentaPorCobrar")

    
    def __repr__(self):
        return f"<Pilado {self.id} {self.origen}>"