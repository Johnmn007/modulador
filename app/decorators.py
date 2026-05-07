from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def roles_required(*roles):
    """
    Decorador para restringir el acceso a ciertas rutas basado en roles.
    Uso: @roles_required('administrador', 'coordinador')
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.rol not in roles:
                flash('No tiene permisos para acceder a esta sección.', 'danger')
                return redirect(url_for('dashboard.index'))
                
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
