from flask import Blueprint
from app.controllers import tarifa_controller as c
from app.middlewares.roles_middleware import roles_required

tarifas_bp = Blueprint("tarifas", __name__, url_prefix="/tarifas")

solo_admin = roles_required("Administrador")

tarifas_bp.add_url_rule("/", "index", solo_admin(c.index))
tarifas_bp.add_url_rule("/nueva", "crear", solo_admin(c.crear),
                        methods=["GET", "POST"])