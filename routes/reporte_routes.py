"""reporte_routes - pendiente de implementar."""
from flask import Blueprint
from app.controllers import reporte_controller as c
from app.middlewares.roles_middleware import roles_required

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")

solo_admin = roles_required("Administrador")

reportes_bp.add_url_rule("/", "index", solo_admin(c.index))
reportes_bp.add_url_rule("/cobros", "cobros", solo_admin(c.cobros))
reportes_bp.add_url_rule("/deuda", "deuda", solo_admin(c.deuda))
reportes_bp.add_url_rule("/bodega", "bodega", solo_admin(c.bodega))