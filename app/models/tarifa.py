from app.extensions import db


class Tarifa(db.Model):
    __tablename__ = "tarifas"

    id = db.Column(db.Integer, primary_key=True)
    servicio = db.Column(db.String(20), nullable=False)   # PILADO, ALMACENAJE
    unidad = db.Column(db.String(20), nullable=False)     # saco, qq, kg, saco_mes
    precio = db.Column(db.Numeric(12, 2), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    vigente_desde = db.Column(db.Date, server_default=db.func.current_date())

    def __repr__(self):
        return f"<Tarifa {self.servicio} {self.precio}/{self.unidad}>"