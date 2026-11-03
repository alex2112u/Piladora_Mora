from datetime import datetime
from decimal import Decimal
from app.extensions import db
from app.models.cobro import Cobro
from app.models.cuenta_por_cobrar import CuentaPorCobrar
from config.constantes import FORMAS_PAGO


def registrar_cobro(cuenta_id, monto, forma_pago="EFECTIVO", usuario_id=None,
                    comprobante=None, observaciones=None):
    """Registra un abono (total o parcial) a una cuenta por cobrar."""
    cuenta = db.session.get(CuentaPorCobrar, cuenta_id)
    if cuenta is None:
        raise ValueError("La cuenta no existe")
    if cuenta.estado in ("PAGADA", "ANULADA"):
        raise ValueError(f"La cuenta ya está {cuenta.estado.lower()}")
    if forma_pago not in FORMAS_PAGO:
        raise ValueError("La forma de pago no es válida")

    monto = Decimal(str(monto))
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")

    saldo = cuenta.saldo
    if monto > saldo:
        raise ValueError(
            f"El monto (${monto:.2f}) supera el saldo pendiente (${saldo:.2f})"
        )

    try:
        cobro = Cobro(
            cuenta=cuenta,
            monto=monto,
            forma_pago=forma_pago,
            usuario_id=usuario_id,
            comprobante=comprobante or None,
            observaciones=observaciones or None,
            fecha=datetime.now(),
        )
        db.session.add(cobro)
        cuenta.actualizar_estado()
        db.session.commit()
        return cobro
    except Exception:
        db.session.rollback()
        raise