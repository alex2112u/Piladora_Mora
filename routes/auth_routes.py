from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__)

auth_bp.add_url_rule("/login", "login", auth_controller.login,
                     methods=["GET", "POST"])
auth_bp.add_url_rule("/logout", "logout", auth_controller.logout,
                     methods=["POST"])