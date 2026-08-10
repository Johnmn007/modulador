from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

# Jerarquía de roles: cada rol incluye los permisos de los roles que le siguen
JERARQUIA_ROLES = {
    'administrador': {'administrador', 'coordinador', 'docente'},
    'coordinador': {'coordinador', 'docente'},
    'docente': {'docente'}
}

def usuario_tiene_permiso(rol_usuario, *roles_requeridos):
    """Verifica si un usuario tiene al menos uno de los roles requeridos (considerando herencia)."""
    roles_disponibles = JERARQUIA_ROLES.get(rol_usuario, {rol_usuario})
    return bool(roles_disponibles & set(roles_requeridos))

def usuario_es_docente(usuario=None):
    """Verifica si un usuario tiene permisos de docente (coordinadores incluidos)."""
    u = usuario or current_user
    return u.rol in ('docente', 'coordinador')

def roles_required(*roles):
    """
    Decorador para restringir el acceso a ciertas rutas basado en roles.
    Implementa herencia de permisos: coordinador hereda permisos de docente.
    Uso: @roles_required('administrador', 'coordinador')
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if not usuario_tiene_permiso(current_user.rol, *roles):
                flash('No tiene permisos para acceder a esta sección.', 'danger')
                return redirect(url_for('dashboard.index'))
                
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def curso_pertenece_al_usuario(curso, usuario=None):
    """
    Verifica si un curso pertenece al usuario actual.
    - Administradores ven todos los cursos.
    - Coordinadores y docentes solo ven sus cursos asignados.
    Retorna True si el usuario tiene acceso al curso.
    """
    u = usuario or current_user
    if u.rol == 'administrador':
        return True
    return curso.docente_id == u.id
