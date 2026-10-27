from flask import Blueprint
from flask_login import login_required
from app.controllers import cliente_controller as c

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

clientes_bp.add_url_rule("/", "index", login_required(c.index))
clientes_bp.add_url_rule("/nuevo", "crear", login_required(c.crear),
                         methods=["GET", "POST"])
clientes_bp.add_url_rule("/<int:id>", "detalle", login_required(c.detalle))
clientes_bp.add_url_rule("/<int:id>/editar", "editar", login_required(c.editar),
                         methods=["GET", "POST"])
clientes_bp.add_url_rule("/<int:id>/estado", "cambiar_estado",
                         login_required(c.cambiar_estado), methods=["POST"])