from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from . import auth_bp
from .forms import LoginForm
from app.models import Usuario
from app.extensions import db
from app.modules.auth.forms import LoginForm



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(correo=form.correo.data).first()
        if usuario and check_password_hash(usuario.contrasena, form.contrasena.data):
            login_user(usuario)
            # Redirigir según el rol
            if usuario.rol.nombre == 'administrador':
                return redirect(url_for('admin.dashboard'))
            elif usuario.rol.nombre == 'docente':
                return redirect(url_for('docente.dashboard'))
            elif usuario.rol.nombre == 'estudiante':
                return redirect(url_for('estudiante.dashboard'))
            else:
                flash("Rol desconocido", "danger")
                return redirect(url_for('auth.login'))
        flash("Credenciales inválidas", "danger")
    return render_template('auth/login.html', form=form)
