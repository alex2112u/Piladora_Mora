from flask import Blueprint
from flask_login import login_required
from app.controllers import pilado_controller as c

pilado_bp = Blueprint("pilado", __name__, url_prefix="/pilado")

pilado_bp.add_url_rule("/", "index", login_required(c.index))
pilado_bp.add_url_rule("/nuevo", "nuevo", login_required(c.nuevo),
                       methods=["GET", "POST"])
pilado_bp.add_url_rule("/<int:id>/ticket", "ticket", login_required(c.ticket))