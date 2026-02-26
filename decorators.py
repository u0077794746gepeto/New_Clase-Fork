from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """Redirige a la página de login si no hay usuario autenticado."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.index"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Permite el acceso sólo a usuarios cuyo rol esté en la lista.
    Se pueden pasar varios nombres de rol.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current = session.get("user_rol", "").lower()
            valid = [r.lower() for r in roles]
            if current not in valid:
                return redirect(url_for("auth.index"))
            return f(*args, **kwargs)
        return decorated
    return decorator
