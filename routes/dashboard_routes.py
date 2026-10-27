from flask import Blueprint
from flask_login import login_required
from app.controllers import dashboard_controller

dashboard_bp = Blueprint("dashboard", __name__)

dashboard_bp.add_url_rule("/", "index",
                          login_required(dashboard_controller.index))