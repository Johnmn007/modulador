# app/modules/auth/routes.py
import jwt
import datetime
import secrets
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlparse, urljoin
from . import auth_bp
from .forms import LoginForm, ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm
from app.models import Usuario
from app.services.logger import auth_logger

@auth_bp.route('/')
def index():
    """Ruta raíz del blueprint auth - redirige al login"""
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario and check_password_hash(usuario.password_hash, form.password.data):
            if usuario.activo:
                login_user(usuario)
                auth_logger.info(f"Login exitoso: {usuario.email} desde {request.remote_addr}")
                flash(f'Bienvenido {usuario.username}!', 'success')
                
                next_page = request.args.get('next')
                if next_page and _is_safe_url(next_page):
                    return redirect(next_page)
                
                return redirect(url_for('dashboard.index'))
            else:
                auth_logger.warning(f"Intento de login en cuenta desactivada: {form.email.data} desde {request.remote_addr}")
                flash('Cuenta desactivada. Contacte al administrador.', 'danger')
        else:
            auth_logger.warning(f"Login fallido: {form.email.data} desde {request.remote_addr}")
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html', form=form)

def _is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def _generate_reset_token(usuario_id, email):
    """Generar token JWT para recuperación de contraseña (expira en 15 minutos)"""
    payload = {
        'user_id': usuario_id,
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'iat': datetime.datetime.utcnow(),
        'jti': secrets.token_hex(16)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def _verify_reset_token(token):
    """Verificar token JWT de recuperación de contraseña"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        usuario = Usuario.query.get(payload['user_id'])
        if usuario and usuario.email == payload['email']:
            return usuario
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    return None

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Solicitar recuperación de contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario:
            token = _generate_reset_token(usuario.id, usuario.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            auth_logger.info(f"Token de recuperación generado para: {usuario.email}")
            
            # En producción, aquí enviarías el email con reset_url
            # Por ahora, mostramos el enlace directamente
            flash(f'Enlace de recuperación generado. Use este enlace para restablecer su contraseña.', 'success')
            return render_template('auth/reset_link.html', reset_url=reset_url, email=usuario.email)
        else:
            # Por seguridad, no revelar si el email existe o no
            flash('Si el correo está registrado, recibirá un enlace de recuperación.', 'info')
            return redirect(url_for('auth.forgot_password'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Restablecer contraseña con token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    usuario = _verify_reset_token(token)
    if not usuario:
        flash('El enlace de recuperación es inválido o ha expirado. Solicite uno nuevo.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        usuario.password_hash = generate_password_hash(form.password.data)
        from app import db
        db.session.commit()
        
        auth_logger.info(f"Contraseña restablecida para: {usuario.email}")
        flash('Su contraseña ha sido restablecida correctamente. Ahora puede iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña (requiere estar logueado)"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('auth/change_password.html', form=form)
        
        current_user.password_hash = generate_password_hash(form.new_password.data)
        from app import db
        db.session.commit()
        
        auth_logger.info(f"Contraseña cambiada por: {current_user.email}")
        flash('Su contraseña ha sido actualizada correctamente.', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))