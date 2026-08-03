# app/modules/admin/routes.py

from app.services.config_service import (
    cargar_configuracion, guardar_configuracion, 
    obtener_semestre_actual, validar_configuracion,
    actualizar_semestre, CONFIG_DEFAULT
)
from app.services.logger import app_logger
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from . import admin_bp
from .forms import ConfiguracionForm, CrearUsuarioForm, EditarUsuarioForm, CicloForm
from app.models import Usuario
from app.extensions import db
import json
import os
import re
from datetime import datetime


@admin_bp.route('/')
@login_required
def index():
    """Panel de administración principal"""
    if current_user.rol != 'administrador':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('dashboard.index'))
    
    config = cargar_configuracion()
    
    stats = {
        'total_usuarios': Usuario.query.count(),
        'usuarios_activos': Usuario.query.filter_by(activo=True).count(),
        'administradores': Usuario.query.filter_by(rol='administrador').count()
    }
    
    return render_template('admin/index.html', config=config, stats=stats)

@admin_bp.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    """Configuración del sistema"""
    if current_user.rol != 'administrador':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('dashboard.index'))
    
    config = cargar_configuracion()
    form = ConfiguracionForm(data=config)
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            nueva_config = {
                'umbral_amarillo': form.umbral_amarillo.data,
                'umbral_rojo': form.umbral_rojo.data,
                'peso_rendimiento': form.peso_rendimiento.data,
                'peso_asistencia': form.peso_asistencia.data,
                'peso_distribucion': form.peso_distribucion.data,
                'peso_historial': form.peso_historial.data,
                'semestre_actual': request.form.get('semestre_actual', obtener_semestre_actual()),
                'nota_minima_aprobatoria': form.nota_minima_aprobatoria.data,
                'porcentaje_asistencia_minimo': form.porcentaje_asistencia_minimo.data
            }
            
            total_pesos = (nueva_config['peso_rendimiento'] + 
                          nueva_config['peso_asistencia'] + 
                          nueva_config['peso_distribucion'] +
                          nueva_config['peso_historial'])
            
            if abs(total_pesos - 1.0) > 0.01:
                flash(f'Los pesos de los factores deben sumar exactamente 1.0 (Suma actual: {total_pesos:.2f})', 'danger')
            else:
                guardar_configuracion(nueva_config)
                flash('Configuración institucional actualizada exitosamente', 'success')
                
        except Exception as e:
            app_logger.error(f"Error en admin: {str(e)}")
            db.session.rollback()
            flash('Ocurrió un error al guardar la configuración. Intente de nuevo.', 'danger')
        
        return redirect(url_for('admin.configuracion'))
    
    return render_template('admin/configuracion.html', config=config, form=form)

@admin_bp.route('/cambiar-semestre', methods=['POST'])
@login_required
def cambiar_semestre():
    """Cambiar solo el semestre actual"""
    if current_user.rol != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        nuevo_semestre = request.form.get('semestre')
        
        if not nuevo_semestre:
            flash('El semestre no puede estar vacío', 'danger')
            return redirect(url_for('admin.configuracion'))
        
        # Validar formato de semestre (YYYY-N)
        if not re.match(r'^\d{4}-[12]$', nuevo_semestre):
            flash('Formato de semestre inválido. Use: AÑO-SEMESTRE (ej: 2025-1, 2025-2)', 'danger')
            return redirect(url_for('admin.configuracion'))
        
        # Cargar configuración actual
        config = cargar_configuracion()
        
        # Actualizar solo el semestre
        config['semestre_actual'] = nuevo_semestre
        
        # Guardar configuración actualizada
        guardar_configuracion(config)
        
        flash(f'Semestre cambiado exitosamente a {nuevo_semestre}', 'success')
        
    except Exception as e:
        flash('Ocurrió un error al cambiar el semestre. Intente de nuevo.', 'danger')
    
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/usuarios')
@login_required
def usuarios():
    """Gestión de usuarios del sistema"""
    if current_user.rol != 'administrador':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('dashboard.index'))
    
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/crear', methods=['POST'])
@login_required
def crear_usuario():
    """Crear nuevo usuario"""
    if current_user.rol != 'administrador':
        flash('No tiene permisos para esta acción', 'danger')
        return redirect(url_for('admin.usuarios'))
    
    form = CrearUsuarioForm()
    if form.validate_on_submit():
        try:
            if Usuario.query.filter_by(username=form.username.data).first():
                flash('El nombre de usuario ya existe', 'danger')
                return redirect(url_for('admin.usuarios'))
                
            if Usuario.query.filter_by(email=form.email.data).first():
                flash('El email ya está registrado', 'danger')
                return redirect(url_for('admin.usuarios'))
            
            nuevo_usuario = Usuario(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                rol=form.rol.data,
                activo=True
            )
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash('Usuario creado exitosamente', 'success')
            
        except Exception as e:
            app_logger.error(f"Error en admin: {str(e)}")
            db.session.rollback()
            flash('Ocurrió un error al crear el usuario. Intente de nuevo.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/usuarios/<int:usuario_id>/toggle', methods=['POST'])
@login_required
def toggle_usuario(usuario_id):
    """Activar/desactivar usuario"""
    if current_user.rol != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # No permitir desactivarse a sí mismo
        if usuario.id == current_user.id:
            return jsonify({'error': 'No puede cambiar su propio estado'}), 400
            
        usuario.activo = not usuario.activo
        db.session.commit()
        
        return jsonify({
            'success': True,
            'nuevo_estado': 'Activo' if usuario.activo else 'Inactivo',
            'message': f'Usuario {"activado" if usuario.activo else "desactivado"} exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al cambiar el estado del usuario'}), 500

@admin_bp.route('/usuarios/<int:usuario_id>/cambiar-rol', methods=['POST'])
@login_required
def cambiar_rol_usuario(usuario_id):
    """Cambiar rol de usuario"""
    if current_user.rol != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        data = request.get_json()
        nuevo_rol = data.get('rol')
        
        if nuevo_rol not in ['administrador', 'coordinador', 'docente']:
            return jsonify({'error': 'Rol inválido'}), 400
            
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # No permitir cambiar el propio rol
        if usuario.id == current_user.id:
            return jsonify({'error': 'No puede cambiar su propio rol'}), 400
            
        usuario.rol = nuevo_rol
        db.session.commit()
        
        return jsonify({
            'success': True,
            'nuevo_rol': nuevo_rol,
            'message': f'Rol cambiado a {nuevo_rol} exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al cambiar el rol del usuario'}), 500

@admin_bp.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    """Eliminar usuario"""
    if current_user.rol != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # No permitir eliminarse a sí mismo
        if usuario.id == current_user.id:
            return jsonify({'error': 'No puede eliminarse a sí mismo'}), 400
            
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuario eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar el usuario'}), 500

@admin_bp.route('/usuarios/<int:usuario_id>/editar', methods=['POST'])
@login_required
def editar_usuario(usuario_id):
    """Editar datos de un usuario existente (username, email, contraseña)"""
    if current_user.rol != 'administrador':
        flash('No tiene permisos para esta acción', 'danger')
        return redirect(url_for('admin.usuarios'))

    form = EditarUsuarioForm()
    try:
        usuario = Usuario.query.get_or_404(usuario_id)

        if not form.validate_on_submit():
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
            return redirect(url_for('admin.usuarios'))

        nuevo_username = form.username.data.strip()
        nuevo_email = form.email.data.strip()
        nueva_password = form.password.data.strip() if form.password.data else ''

        if Usuario.query.filter(
            Usuario.username == nuevo_username,
            Usuario.id != usuario_id
        ).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('admin.usuarios'))

        if Usuario.query.filter(
            Usuario.email == nuevo_email,
            Usuario.id != usuario_id
        ).first():
            flash('El email ya está registrado.', 'danger')
            return redirect(url_for('admin.usuarios'))

        usuario.username = nuevo_username
        usuario.email = nuevo_email

        if nueva_password:
            usuario.password_hash = generate_password_hash(nueva_password)

        db.session.commit()
        flash(f'Usuario "{nuevo_username}" actualizado correctamente.', 'success')

    except Exception as e:
        app_logger.error(f"Error editando usuario {usuario_id}: {str(e)}")
        db.session.rollback()
        flash('Ocurrió un error al actualizar el usuario. Intente de nuevo.', 'danger')

    return redirect(url_for('admin.usuarios'))



@admin_bp.route('/ciclos', methods=['GET', 'POST'])
@login_required
def ciclos():
    """Gestión de ciclos académicos y cierre/apertura"""
    if current_user.rol != 'administrador':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('dashboard.index'))
    
    from app.models import Ciclo
    config = cargar_configuracion()
    form = CicloForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            nuevo_ciclo = Ciclo(
                nombre=form.nombre.data,
                codigo_ciclo=form.codigo.data,
                fecha_inicio=form.fecha_inicio.data,
                fecha_fin=form.fecha_fin.data,
                activo=True
            )
            
            Ciclo.query.update({Ciclo.activo: False})
            
            db.session.add(nuevo_ciclo)
            
            config['semestre_actual'] = form.codigo.data
            guardar_configuracion(config)
            
            db.session.commit()
            flash(f'¡Ciclo {form.nombre.data} iniciado exitosamente! El sistema ahora opera en el periodo {form.codigo.data}.', 'success')
            return redirect(url_for('admin.ciclos'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al crear el ciclo. Intente de nuevo.', 'danger')
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    ciclos_historial = Ciclo.query.order_by(Ciclo.fecha_inicio.desc()).all()
    return render_template('admin/ciclos.html', ciclos=ciclos_historial, config=config, form=form)

@admin_bp.route('/backup')
@login_required
def backup():
    """Panel de backup y restauración"""
    if current_user.rol != 'administrador':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('admin/backup.html')

@admin_bp.route('/logs')
@login_required
def logs():
    """Visualización de logs del sistema"""
    if current_user.rol != 'administrador':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('dashboard.index'))
    
    import os
    from datetime import datetime
    
    log_entries = []
    log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    
    if os.path.exists(log_dir):
        for log_file in ['app.log', 'auth.log', 'riesgo.log']:
            log_path = os.path.join(log_dir, log_file)
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[-50:]
                        for line in lines:
                            line = line.strip()
                            if line:
                                parts = line.split(' - ', 3)
                                if len(parts) >= 4:
                                    log_entries.append({
                                        'fecha': parts[0],
                                        'nivel': parts[2],
                                        'mensaje': parts[3][:100]
                                    })
                except Exception:
                    pass
    
    log_entries.sort(key=lambda x: x.get('fecha', ''), reverse=True)
    log_entries = log_entries[:50]
    
    if not log_entries:
        log_entries = [
            {'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'nivel': 'INFO', 'mensaje': 'Sistema iniciado correctamente'},
        ]
    
    return render_template('admin/logs.html', logs=log_entries)