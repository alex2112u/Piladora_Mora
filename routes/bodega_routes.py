from flask import Blueprint
from flask_login import login_required
from app.controllers import bodega_controller as c

bodega_bp = Blueprint("bodega", __name__, url_prefix="/bodega")

bodega_bp.add_url_rule("/", "index", login_required(c.index))
bodega_bp.add_url_rule("/registrar", "registrar", login_required(c.registrar),
                       methods=["GET", "POST"])
bodega_bp.add_url_rule("/cliente/<int:id>", "historial",
                       login_required(c.historial))