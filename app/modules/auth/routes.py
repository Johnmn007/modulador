# app/modules/auth/routes.py
import jwt
import datetime
import secrets
from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlparse, urljoin
from . import auth_bp
from .forms import (LoginForm, ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm,
                    PreguntaSeguridadForm, ResponderPreguntasForm, NuevaPasswordRecuperacionForm)
from app.models import Usuario, PreguntaSeguridad
from app.extensions import db
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

# ==================== RECUPERAR CONTRASEÑA CON PREGUNTAS DE SEGURIDAD ====================

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Solicitar recuperación de contraseña - Paso 1: Ingresar email"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if not usuario:
            # Por seguridad, no revelar si el email existe
            flash('Si el correo está registrado, podrá recuperar su contraseña.', 'info')
            return redirect(url_for('auth.forgot_password'))
        
        # Verificar si tiene preguntas de seguridad configuradas
        preguntas = PreguntaSeguridad.query.filter_by(usuario_id=usuario.id).all()
        
        if len(preguntas) < 3:
            flash('Su cuenta no tiene preguntas de seguridad configuradas. Contacte al administrador.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        # Guardar email en sesión para el siguiente paso
        session['recuperacion_email'] = usuario.email
        auth_logger.info(f"Inicio de recuperación de contraseña para: {usuario.email}")
        
        return redirect(url_for('auth.responder_preguntas'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/responder-preguntas', methods=['GET', 'POST'])
def responder_preguntas():
    """Paso 2: Responder preguntas de seguridad"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Verificar que haya un email en sesión
    email = session.get('recuperacion_email')
    if not email:
        flash('Sesión expirada. Inicie el proceso de recuperación nuevamente.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        flash('Error en el proceso. Intente nuevamente.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    preguntas = PreguntaSeguridad.query.filter_by(usuario_id=usuario.id).all()
    if len(preguntas) < 3:
        flash('Error: Preguntas de seguridad no configuradas.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResponderPreguntasForm()
    
    if form.validate_on_submit():
        # Verificar respuestas (case-insensitive, trimmed)
        respuestas_usuario = [
            form.respuesta_1.data.strip().lower(),
            form.respuesta_2.data.strip().lower(),
            form.respuesta_3.data.strip().lower()
        ]
        
        respuestas_correctas = 0
        for i, pregunta in enumerate(preguntas):
            if check_password_hash(pregunta.respuesta_hash, respuestas_usuario[i]):
                respuestas_correctas += 1
        
        if respuestas_correctas == 3:
            # Respuestas correctas - permitir cambio de contraseña
            auth_logger.info(f"Preguntas de seguridad respondidas correctamente para: {email}")
            session['recuperacion_verificado'] = True
            return redirect(url_for('auth.nueva_password_recuperacion'))
        else:
            auth_logger.warning(f"Respuestas incorrectas en recuperación para: {email}")
            flash(f'Respuestas incorrectas. Intentos fallidos: {3 - respuestas_correctas}', 'danger')
            return redirect(url_for('auth.forgot_password'))
    
    return render_template('auth/responder_preguntas.html', form=form, preguntas=preguntas)

@auth_bp.route('/nueva-password-recuperacion', methods=['GET', 'POST'])
def nueva_password_recuperacion():
    """Paso 3: Establecer nueva contraseña después de verificar identidad"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Verificar que haya pasado la verificación
    if not session.get('recuperacion_verificado'):
        flash('Debe verificar su identidad primero.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    email = session.get('recuperacion_email')
    usuario = Usuario.query.filter_by(email=email).first()
    
    if not usuario:
        flash('Error en el proceso. Intente nuevamente.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = NuevaPasswordRecuperacionForm()
    
    if form.validate_on_submit():
        # Actualizar contraseña
        usuario.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        
        # Limpiar sesión
        session.pop('recuperacion_email', None)
        session.pop('recuperacion_verificado', None)
        
        auth_logger.info(f"Contraseña restablecida vía preguntas de seguridad: {email}")
        flash('Su contraseña ha sido restablecida correctamente. Ahora puede iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/nueva_password_recuperacion.html', form=form)

# ==================== CAMBIAR CONTRASEÑA (LOGUEADO) ====================

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
        db.session.commit()
        
        auth_logger.info(f"Contraseña cambiada por: {current_user.email}")
        flash('Su contraseña ha sido actualizada correctamente.', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/change_password.html', form=form)

# ==================== CONFIGURAR PREGUNTAS DE SEGURIDAD ====================

@auth_bp.route('/configurar-preguntas', methods=['GET', 'POST'])
@login_required
def configurar_preguntas():
    """Configurar preguntas de seguridad (requiere estar logueado)"""
    # Obtener preguntas existentes
    preguntas_existentes = PreguntaSeguridad.query.filter_by(usuario_id=current_user.id).all()
    
    form = PreguntaSeguridadForm()
    
    if form.validate_on_submit():
        # Eliminar preguntas existentes
        PreguntaSeguridad.query.filter_by(usuario_id=current_user.id).delete()
        
        # Crear nuevas preguntas con respuestas hasheadas
        preguntas_data = [
            (form.pregunta_1.data, form.respuesta_1.data),
            (form.pregunta_2.data, form.respuesta_2.data),
            (form.pregunta_3.data, form.respuesta_3.data)
        ]
        
        for pregunta, respuesta in preguntas_data:
            nueva_pregunta = PreguntaSeguridad(
                usuario_id=current_user.id,
                pregunta=pregunta,
                respuesta_hash=generate_password_hash(respuesta.strip().lower())
            )
            db.session.add(nueva_pregunta)
        
        db.session.commit()
        auth_logger.info(f"Preguntas de seguridad actualizadas por: {current_user.email}")
        flash('Preguntas de seguridad guardadas correctamente.', 'success')
        return redirect(url_for('dashboard.index'))
    
    # Pre-cargar preguntas existentes si las hay
    if preguntas_existentes and request.method == 'GET':
        form.pregunta_1.data = preguntas_existentes[0].pregunta if len(preguntas_existentes) > 0 else ''
        form.pregunta_2.data = preguntas_existentes[1].pregunta if len(preguntas_existentes) > 1 else ''
        form.pregunta_3.data = preguntas_existentes[2].pregunta if len(preguntas_existentes) > 2 else ''
    
    tiene_preguntas = len(preguntas_existentes) >= 3
    
    return render_template('auth/configurar_preguntas.html', form=form, tiene_preguntas=tiene_preguntas)

@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))