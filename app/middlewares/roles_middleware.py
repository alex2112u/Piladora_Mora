from functools import wraps
from flask import abort, current_app
from flask_login import current_user


def roles_required(*roles):
    def decorador(f):
        @wraps(f)
        def envoltura(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if not current_user.rol or current_user.rol.nombre not in roles:
                abort(403)
            return f(*args, **kwargs)
        return envoltura
    return decorador