# app/modules/asistencias/routes.py
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import asistencias_bp
from app.models import Asistencia, Inscripcion, Estudiante, Curso
from app.extensions import db
from app.decorators import roles_required, curso_pertenece_al_usuario
from .forms import AsistenciaForm, AsistenciaMasivaForm
from datetime import datetime

@asistencias_bp.route('/')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def index():
    """Lista de todas las asistencias"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Query base con joins
    asistencias_query = Asistencia.query.join(Inscripcion).join(Estudiante).join(Curso)

    # Filtro por rol: docentes y coordinadores solo ven asistencias de sus cursos
    if current_user.rol in ('docente', 'coordinador'):
        asistencias_query = asistencias_query.filter(Curso.docente_id == current_user.id)

    # Filtros
    estudiante_id = request.args.get('estudiante_id', type=int)
    curso_id = request.args.get('curso_id', type=int)
    fecha = request.args.get('fecha', '')
    estado_asistencia = request.args.get('estado_asistencia', '')
    
    if estudiante_id:
        asistencias_query = asistencias_query.filter(Inscripcion.estudiante_id == estudiante_id)
    if curso_id:
        asistencias_query = asistencias_query.filter(Inscripcion.curso_id == curso_id)
    if fecha:
        asistencias_query = asistencias_query.filter(Asistencia.fecha == fecha)
    if estado_asistencia:
        if estado_asistencia == 'PRESENTE':
            asistencias_query = asistencias_query.filter(Asistencia.presente == True)
        elif estado_asistencia == 'AUSENTE':
            asistencias_query = asistencias_query.filter(Asistencia.presente == False)

    asistencias = asistencias_query.order_by(
        Asistencia.fecha.desc(), Curso.nombre_curso, Estudiante.apellidos
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Para los filtros: cursos del ciclo activo
    from app.services.config_service import cargar_configuracion
    from app.models import Ciclo
    config = cargar_configuracion()
    ciclo = Ciclo.query.filter_by(codigo_ciclo=config.get('semestre_actual')).first()

    estudiantes = Estudiante.query.filter_by(activo=True).order_by('nombres', 'apellidos').all()
    if ciclo:
        if current_user.rol in ('docente', 'coordinador'):
            cursos = Curso.query.filter_by(activo=True, docente_id=current_user.id, ciclo_id=ciclo.id).order_by('semestre', 'nombre_curso').all()
        else:
            cursos = Curso.query.filter_by(activo=True, ciclo_id=ciclo.id).order_by('semestre', 'nombre_curso').all()
    else:
        cursos = []

    return render_template('asistencias/index.html',
                         asistencias=asistencias,
                         estudiantes=estudiantes,
                         cursos=cursos,
                         estudiante_id=estudiante_id,
                         curso_id=curso_id,
                         fecha=fecha,
                         estado_asistencia=estado_asistencia)

@asistencias_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def crear():
    """Registrar nueva asistencia individual"""
    form = AsistenciaForm()
    
    if form.validate_on_submit():
        try:
            # Verificar pertenencia del curso (docentes y coordinadores)
            if current_user.rol in ('docente', 'coordinador'):
                inscripcion = Inscripcion.query.get(form.inscripcion_id.data)
                if not inscripcion or not curso_pertenece_al_usuario(inscripcion.curso):
                    flash('No tiene permisos para registrar asistencias en este curso', 'danger')
                    return redirect(url_for('asistencias.index'))
            
            # Verificar si ya existe registro para esta inscripción y fecha
            asistencia_existente = Asistencia.query.filter_by(
                inscripcion_id=form.inscripcion_id.data,
                fecha=form.fecha.data
            ).first()
            
            if asistencia_existente:
                flash('Ya existe un registro de asistencia para este estudiante en esta fecha', 'danger')
                return render_template('asistencias/crear.html', form=form)
            
            # Crear nueva asistencia
            nueva_asistencia = Asistencia(
                inscripcion_id=form.inscripcion_id.data,
                fecha=form.fecha.data,
                presente=form.presente.data,
                justificado=form.justificado.data,
                observaciones=form.observaciones.data or None
            )
            
            db.session.add(nueva_asistencia)
            db.session.commit()
            
            flash('Asistencia registrada exitosamente', 'success')
            return redirect(url_for('asistencias.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al registrar la asistencia. Intente de nuevo.', 'danger')
    
    return render_template('asistencias/crear.html', form=form)

@asistencias_bp.route('/masiva', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def crear_masiva():
    """Registro masivo de asistencias por curso"""
    form = AsistenciaMasivaForm()
    
    # Todos los usuarios solo ven cursos del ciclo activo en el selector
    from app.services.config_service import cargar_configuracion
    from app.models import Ciclo
    config = cargar_configuracion()
    ciclo = Ciclo.query.filter_by(codigo_ciclo=config.get('semestre_actual')).first()
    ciclo_id_actual = ciclo.id if ciclo else None

    if ciclo_id_actual:
        if current_user.rol in ('docente', 'coordinador'):
            cursos_disponibles = Curso.query.filter_by(activo=True, docente_id=current_user.id, ciclo_id=ciclo_id_actual).all()
        else:
            cursos_disponibles = Curso.query.filter_by(activo=True, ciclo_id=ciclo_id_actual).all()
    else:
        cursos_disponibles = []

    form.curso_id.choices = [(c.id, f"{c.codigo_curso} - {c.nombre_curso} (Nivel {c.semestre})") for c in cursos_disponibles]
    
    if form.validate_on_submit():
        try:
            curso_id_seleccionado = form.curso_id.data
            curso = Curso.query.get(curso_id_seleccionado)

            if not curso:
                flash('El curso seleccionado no existe', 'danger')
                return redirect(url_for('asistencias.crear_masiva'))

            if not ciclo_id_actual:
                flash('No hay un ciclo activo configurado. No se pueden registrar asistencias.', 'danger')
                return redirect(url_for('asistencias.crear_masiva'))

            if curso.ciclo_id != ciclo_id_actual:
                flash('Este curso no pertenece al ciclo actual. Solo puede pasar lista de cursos del ciclo activo.', 'danger')
                return redirect(url_for('asistencias.crear_masiva'))

            # Verificar pertenencia del curso (docentes y coordinadores)
            if current_user.rol in ('docente', 'coordinador'):
                if not curso_pertenece_al_usuario(curso):
                    flash('No tiene permisos para registrar asistencias en este curso', 'danger')
                    return redirect(url_for('asistencias.index'))
            
            # Obtener todas las inscripciones activas del curso
            inscripciones = Inscripcion.query.join(Estudiante).filter(
                Inscripcion.curso_id == form.curso_id.data,
                Inscripcion.estado == 'ACTIVO',
                Estudiante.activo == True
            ).order_by(Estudiante.nombres, Estudiante.apellidos).all()
            
            if not inscripciones:
                flash('No hay estudiantes inscritos en este curso', 'warning')
                return render_template('asistencias/crear_masiva.html', form=form)
            
            return render_template('asistencias/formulario_masivo.html',
                                 curso_id=form.curso_id.data,
                                 fecha=form.fecha.data,
                                 inscripciones=inscripciones)
            
        except Exception as e:
            flash('Ocurrió un error al generar el formulario masivo. Intente de nuevo.', 'danger')
    
    return render_template('asistencias/crear_masiva.html', form=form)

@asistencias_bp.route('/masiva/procesar', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def procesar_masiva():
    """Procesar el formulario masivo de asistencias"""
    try:
        curso_id = request.form.get('curso_id')
        fecha_str = request.form.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        # Verificar pertenencia del curso (docentes y coordinadores)
        if current_user.rol in ('docente', 'coordinador'):
            curso = Curso.query.get(curso_id)
            if not curso or not curso_pertenece_al_usuario(curso):
                flash('No tiene permisos para registrar asistencias en este curso', 'danger')
                return redirect(url_for('asistencias.index'))
        
        # Obtener todas las inscripciones del curso
        inscripciones = Inscripcion.query.join(Estudiante).filter(
            Inscripcion.curso_id == curso_id,
            Inscripcion.estado == 'ACTIVO'
        ).order_by(Estudiante.nombres, Estudiante.apellidos).all()
        
        registros_procesados = 0
        
        for inscripcion in inscripciones:
            # Verificar si ya existe registro para esta fecha
            asistencia_existente = Asistencia.query.filter_by(
                inscripcion_id=inscripcion.id,
                fecha=fecha
            ).first()
            
            if asistencia_existente:
                # Actualizar registro existente
                presente = request.form.get(f'presente_{inscripcion.id}') == 'on'
                justificado = request.form.get(f'justificado_{inscripcion.id}') == 'on'
                observaciones = request.form.get(f'observaciones_{inscripcion.id}', '')
                
                asistencia_existente.presente = presente
                asistencia_existente.justificado = justificado
                asistencia_existente.observaciones = observaciones
                registros_procesados += 1
            else:
                # Crear nuevo registro
                presente = request.form.get(f'presente_{inscripcion.id}') == 'on'
                justificado = request.form.get(f'justificado_{inscripcion.id}') == 'on'
                observaciones = request.form.get(f'observaciones_{inscripcion.id}', '')
                
                nueva_asistencia = Asistencia(
                    inscripcion_id=inscripcion.id,
                    fecha=fecha,
                    presente=presente,
                    justificado=justificado,
                    observaciones=observaciones or None
                )
                db.session.add(nueva_asistencia)
                registros_procesados += 1
        
        db.session.commit()
        
        # RECALCULAR RIESGO PARA ESTOS ESTUDIANTES
        from app.services.seguimiento_service import SeguimientoService
        for inscripcion in inscripciones:
            SeguimientoService.recalcular_estudiante(inscripcion.estudiante_id)
            
        flash(f'Asistencias procesadas exitosamente: {registros_procesados} registros y riesgo actualizado', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al procesar las asistencias. Intente de nuevo.', 'danger')
    
    return redirect(url_for('asistencias.index'))

@asistencias_bp.route('/<int:asistencia_id>')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def detalle(asistencia_id):
    """Detalle de una asistencia específica"""
    asistencia = Asistencia.query.get_or_404(asistencia_id)
    
    # Verificar pertenencia del curso (docentes y coordinadores)
    if current_user.rol in ('docente', 'coordinador'):
        inscripcion = Inscripcion.query.get(asistencia.inscripcion_id)
        if not inscripcion or not curso_pertenece_al_usuario(inscripcion.curso):
            flash('No tiene permisos para ver esta asistencia', 'danger')
            return redirect(url_for('asistencias.index'))
    
    return render_template('asistencias/detalle.html', asistencia=asistencia)

@asistencias_bp.route('/<int:asistencia_id>/editar', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def editar(asistencia_id):
    """Editar asistencia existente"""
    asistencia = Asistencia.query.get_or_404(asistencia_id)
    
    # Verificar pertenencia del curso (docentes y coordinadores)
    if current_user.rol in ('docente', 'coordinador'):
        inscripcion = Inscripcion.query.get(asistencia.inscripcion_id)
        if not inscripcion or not curso_pertenece_al_usuario(inscripcion.curso):
            flash('No tiene permisos para editar esta asistencia', 'danger')
            return redirect(url_for('asistencias.index'))
    
    form = AsistenciaForm(obj=asistencia)
    
    if form.validate_on_submit():
        try:
            # Verificar si ya existe registro (excluyendo el actual)
            asistencia_existente = Asistencia.query.filter(
                Asistencia.inscripcion_id == form.inscripcion_id.data,
                Asistencia.fecha == form.fecha.data,
                Asistencia.id != asistencia_id
            ).first()
            
            if asistencia_existente:
                flash('Ya existe un registro de asistencia para este estudiante en esta fecha', 'danger')
                return render_template('asistencias/editar.html', form=form, asistencia=asistencia)
            
            # Actualizar asistencia
            asistencia.inscripcion_id = form.inscripcion_id.data
            asistencia.fecha = form.fecha.data
            asistencia.presente = form.presente.data
            asistencia.justificado = form.justificado.data
            asistencia.observaciones = form.observaciones.data or None
            
            db.session.commit()
            
            flash('Asistencia actualizada exitosamente', 'success')
            return redirect(url_for('asistencias.detalle', asistencia_id=asistencia.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al actualizar la asistencia. Intente de nuevo.', 'danger')
    
    return render_template('asistencias/editar.html', form=form, asistencia=asistencia)

@asistencias_bp.route('/<int:asistencia_id>/eliminar', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def eliminar(asistencia_id):
    """Eliminar asistencia"""
    try:
        asistencia = Asistencia.query.get_or_404(asistencia_id)
        
        db.session.delete(asistencia)
        db.session.commit()
        
        flash('Asistencia eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al eliminar la asistencia. Intente de nuevo.', 'danger')
    
    return redirect(url_for('asistencias.index'))

@asistencias_bp.route('/estadisticas')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def estadisticas():
    """Estadísticas de asistencias"""
    # Obtener parámetros de filtro
    curso_id = request.args.get('curso_id', type=int)
    estudiante_id = request.args.get('estudiante_id', type=int)
    semestre = request.args.get('semestre', '')
    
    # Query base para estadísticas
    query = db.session.query(
        Inscripcion.curso_id,
        Curso.nombre_curso,
        Inscripcion.estudiante_id,
        Estudiante.nombres,
        Estudiante.apellidos,
        db.func.count(Asistencia.id).label('total_clases'),
        db.func.sum(db.cast(Asistencia.presente, db.Integer)).label('asistencias'),
        db.func.sum(db.cast(Asistencia.justificado, db.Integer)).label('justificadas')
    ).join(Curso).join(Estudiante).join(Asistencia, isouter=True)
    
    # Filtro por rol: docentes y coordinadores solo ven estadísticas de sus cursos
    if current_user.rol in ('docente', 'coordinador'):
        query = query.filter(Curso.docente_id == current_user.id)
    
    # Aplicar filtros
    if curso_id:
        query = query.filter(Inscripcion.curso_id == curso_id)
    if estudiante_id:
        query = query.filter(Inscripcion.estudiante_id == estudiante_id)
    if semestre:
        query = query.filter(Curso.semestre == semestre)
    
    estadisticas = query.group_by(
        Inscripcion.curso_id, Curso.nombre_curso, 
        Inscripcion.estudiante_id, Estudiante.nombres, Estudiante.apellidos
    ).all()
    
    # Calcular porcentajes
    estadisticas_con_porcentajes = []
    for stat in estadisticas:
        total_clases = stat.total_clases or 0
        asistencias = stat.asistencias or 0
        justificadas = stat.justificadas or 0
        
        if total_clases > 0:
            porcentaje_asistencia = (asistencias / total_clases) * 100
            porcentaje_efectiva = ((asistencias - justificadas) / total_clases) * 100
        else:
            porcentaje_asistencia = 0
            porcentaje_efectiva = 0
        
        estadisticas_con_porcentajes.append({
            'curso': stat.nombre_curso,
            'estudiante': f"{stat.nombres} {stat.apellidos}",
            'total_clases': total_clases,
            'asistencias': asistencias,
            'justificadas': justificadas,
            'porcentaje_asistencia': porcentaje_asistencia,
            'porcentaje_efectiva': porcentaje_efectiva
        })
    
    # Para los filtros: cursos del ciclo activo
    from app.services.config_service import cargar_configuracion
    from app.models import Ciclo
    config = cargar_configuracion()
    ciclo = Ciclo.query.filter_by(codigo_ciclo=config.get('semestre_actual')).first()
    if ciclo:
        if current_user.rol in ('docente', 'coordinador'):
            cursos = Curso.query.filter_by(activo=True, docente_id=current_user.id, ciclo_id=ciclo.id).order_by('semestre', 'nombre_curso').all()
        else:
            cursos = Curso.query.filter_by(activo=True, ciclo_id=ciclo.id).order_by('semestre', 'nombre_curso').all()
    else:
        cursos = []
    
    estudiantes = Estudiante.query.filter_by(activo=True).order_by('nombres', 'apellidos').all()
    semestres = db.session.query(Curso.semestre).distinct().order_by(Curso.semestre.desc()).all()
    
    return render_template('asistencias/estadisticas.html',
                         estadisticas=estadisticas_con_porcentajes,
                         cursos=cursos,
                         estudiantes=estudiantes,
                         semestres=semestres,
                         curso_id=curso_id,
                         estudiante_id=estudiante_id,
                         semestre=semestre)