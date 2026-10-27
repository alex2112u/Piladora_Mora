from decimal import Decimal
from app.extensions import db
from app.models.cobro import Cobro
from app.models.cuenta_por_cobrar import CuentaPorCobrar


def registrar_cobro(cuenta_id, monto, forma_pago="EFECTIVO",
                    usuario_id=None, comprobante=None):
    cuenta = db.session.get(CuentaPorCobrar, cuenta_id)
    if cuenta is None:
        raise ValueError("La cuenta no existe")

    monto = Decimal(str(monto))
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")
    if monto > cuenta.saldo:
        raise ValueError(f"El monto supera el saldo pendiente ({cuenta.saldo})")

    cobro = Cobro(cuenta=cuenta, monto=monto, forma_pago=forma_pago,usuario_id=usuario_id, comprobante=comprobante)
    db.session.add(cobro)
    cuenta.actualizar_estado()
    db.session.commit()
    return cobro