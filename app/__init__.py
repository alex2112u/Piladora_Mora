from flask import Flask
from config.config import Config
from app.extensions import db, migrate, login_manager


def create_app():
    app = Flask(
        __name__,
        template_folder="views",
        static_folder="../public",
        static_url_path="/static",
    )
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."

    from app.models import (  # noqa
        rol, usuario, cliente, proveedor, categoria_producto,
        producto, lote, movimiento_inventario,
        tarifa, cuenta_por_cobrar, cobro, pilado,
    )

    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.bodega_routes import bodega_bp 
    
    app.register_blueprint(bodega_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    from routes.cliente_routes import clientes_bp
    app.register_blueprint(clientes_bp)

    return app