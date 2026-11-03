
from flask import Blueprint
from flask_login import login_required
from app.controllers import cobro_controller as c

cobros_bp = Blueprint("cobros", __name__, url_prefix="/cobros")

cobros_bp.add_url_rule("/", "index", login_required(c.index))
cobros_bp.add_url_rule("/cuenta/<int:id>", "cuenta", login_required(c.cuenta),
methods=["GET", "POST"])