# app/modules/asistencias/routes.py
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import asistencias_bp
from app.models import Asistencia, Inscripcion, Estudiante, Curso, DiaNoLectivo, Ciclo
from app.extensions import db
from app.decorators import roles_required, curso_pertenece_al_usuario
from .forms import AsistenciaForm, AsistenciaMasivaForm
from datetime import datetime

@asistencias_bp.route('/')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def index():
    """Lista de sesiones de asistencias (agrupadas por curso y fecha)"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Query base agrupada
    asistencias_query = db.session.query(
        Curso.id.label('curso_id'),
        Curso.nombre_curso,
        Curso.semestre,
        Asistencia.fecha,
        db.func.count(Asistencia.id).label('total_estudiantes'),
        db.func.max(db.case((Asistencia.es_institucional == True, 1), else_=0)).label('es_institucional'),
        db.func.max(Asistencia.motivo_institucional).label('motivo_institucional')
    ).join(Inscripcion, Asistencia.inscripcion_id == Inscripcion.id)\
     .join(Curso, Inscripcion.curso_id == Curso.id)

    # Filtro por rol: docentes y coordinadores solo ven asistencias de sus cursos
    if current_user.rol in ('docente', 'coordinador'):
        asistencias_query = asistencias_query.filter(Curso.docente_id == current_user.id)

    # Filtros
    curso_id = request.args.get('curso_id', type=int)
    fecha = request.args.get('fecha', '')
    
    from app.services.config_service import get_ciclo_activo
    from app.models import Ciclo
    
    ciclo_activo = get_ciclo_activo()
    filtro_ciclo_id = request.args.get('filtro_ciclo_id', type=int)
    
    # Filtrado por ciclo
    if current_user.rol == 'administrador' and filtro_ciclo_id:
        if filtro_ciclo_id != -1:
            asistencias_query = asistencias_query.filter(Curso.ciclo_id == filtro_ciclo_id)
    else:
        if ciclo_activo:
            asistencias_query = asistencias_query.filter(Curso.ciclo_id == ciclo_activo.id)
        else:
            asistencias_query = asistencias_query.filter(db.false())
    
    # Comportamiento por defecto: Si no hay filtros activos (fecha o curso), 
    # y si estamos viendo el ciclo activo, mostrar solo el día actual.
    # Si estamos viendo histórico (filtro_ciclo_id y es != ciclo_activo.id), no forzar fecha de hoy.
    is_historico = current_user.rol == 'administrador' and filtro_ciclo_id and (not ciclo_activo or filtro_ciclo_id != ciclo_activo.id)
    if not fecha and not curso_id and not is_historico:
        from datetime import date
        fecha = date.today().strftime('%Y-%m-%d')
    
    if curso_id:
        asistencias_query = asistencias_query.filter(Inscripcion.curso_id == curso_id)
    if fecha:
        asistencias_query = asistencias_query.filter(Asistencia.fecha == fecha)

    sesiones = asistencias_query.group_by(
        Curso.id, Curso.nombre_curso, Curso.semestre, Asistencia.fecha
    ).order_by(
        Asistencia.fecha.desc(), Curso.nombre_curso
    ).paginate(page=page, per_page=per_page, error_out=False)

    target_ciclo_id = filtro_ciclo_id if (current_user.rol == 'administrador' and filtro_ciclo_id and filtro_ciclo_id != -1) else (ciclo_activo.id if ciclo_activo else None)

    if target_ciclo_id:
        if current_user.rol in ('docente', 'coordinador'):
            cursos = Curso.query.filter_by(activo=True, docente_id=current_user.id, ciclo_id=target_ciclo_id).order_by('semestre', 'nombre_curso').all()
        else:
            cursos = Curso.query.filter_by(activo=True, ciclo_id=target_ciclo_id).order_by('semestre', 'nombre_curso').all()
    else:
        if current_user.rol in ('docente', 'coordinador'):
            cursos = Curso.query.filter_by(activo=True, docente_id=current_user.id).order_by('semestre', 'nombre_curso').all()
        else:
            cursos = Curso.query.filter_by(activo=True).order_by('semestre', 'nombre_curso').all()

    ciclos = Ciclo.query.order_by(Ciclo.fecha_inicio.desc()).all() if current_user.rol == 'administrador' else []

    return render_template('asistencias/index.html',
                         sesiones=sesiones,
                         cursos=cursos,
                         ciclos=ciclos,
                         filtro_ciclo_id=filtro_ciclo_id or (ciclo_activo.id if ciclo_activo else -1),
                         curso_id=curso_id,
                         fecha=fecha)

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
    from app.services.config_service import get_ciclo_activo
    ciclo = get_ciclo_activo()
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
            
            # Notificar si ya existe asistencia para este curso en esta fecha
            asistencia_previa = Asistencia.query.join(Inscripcion).filter(
                Inscripcion.curso_id == form.curso_id.data,
                Asistencia.fecha == form.fecha.data
            ).first()
            
            if asistencia_previa:
                fecha_str = form.fecha.data.strftime('%d/%m/%Y') if hasattr(form.fecha.data, 'strftime') else form.fecha.data
                flash(f'Aviso: Ya se ha registrado asistencia para este curso en la fecha {fecha_str}. Si continúa, actualizará los registros existentes.', 'info')
            
            # Obtener todas las inscripciones activas del curso
            inscripciones = Inscripcion.query.join(Estudiante).filter(
                Inscripcion.curso_id == form.curso_id.data,
                Inscripcion.estado == 'ACTIVO',
                Estudiante.activo == True
            ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
            
            if not inscripciones:
                flash('No hay estudiantes inscritos en este curso', 'warning')
                return render_template('asistencias/crear_masiva.html', form=form)
            
            # Verificar si existe día no lectivo o asistencias previas
            dia_no_lectivo = DiaNoLectivo.query.filter(
                DiaNoLectivo.ciclo_id == curso.ciclo_id,
                DiaNoLectivo.fecha == form.fecha.data,
                (DiaNoLectivo.curso_id == None) | (DiaNoLectivo.curso_id == curso.id)
            ).first()

            asistencias_existentes = Asistencia.query.join(Inscripcion).filter(
                Inscripcion.curso_id == form.curso_id.data,
                Asistencia.fecha == form.fecha.data
            ).all()
            asistencias_dict = {a.inscripcion_id: a for a in asistencias_existentes}
            es_sesion_institucional = any(getattr(a, 'es_institucional', False) for a in asistencias_existentes)
            motivo_institucional_sesion = next((a.motivo_institucional for a in asistencias_existentes if getattr(a, 'es_institucional', False) and a.motivo_institucional), None)
            if not motivo_institucional_sesion and dia_no_lectivo:
                motivo_institucional_sesion = f"{dia_no_lectivo.tipo}: {dia_no_lectivo.motivo}"

            return render_template('asistencias/formulario_masivo.html',
                                 curso_id=form.curso_id.data,
                                 fecha=form.fecha.data,
                                 inscripciones=inscripciones,
                                 asistencias_dict=asistencias_dict,
                                 dia_no_lectivo=dia_no_lectivo,
                                 es_sesion_institucional=es_sesion_institucional,
                                 motivo_institucional_sesion=motivo_institucional_sesion)
            
        except Exception as e:
            flash('Ocurrió un error al generar el formulario masivo. Intente de nuevo.', 'danger')
    
    return render_template('asistencias/crear_masiva.html', form=form)

@asistencias_bp.route('/masiva/editar_sesion/<int:curso_id>/<fecha>', methods=['GET'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def editar_masiva_sesion(curso_id, fecha):
    """Editar una sesión de asistencia completa (curso y fecha)"""
    curso = Curso.query.get_or_404(curso_id)
    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    
    if current_user.rol in ('docente', 'coordinador'):
        if not curso_pertenece_al_usuario(curso):
            flash('No tiene permisos para editar asistencias en este curso', 'danger')
            return redirect(url_for('asistencias.index'))
            
    inscripciones = Inscripcion.query.join(Estudiante).filter(
        Inscripcion.curso_id == curso_id,
        Inscripcion.estado == 'ACTIVO',
        Estudiante.activo == True
    ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
    
    asistencias_existentes = Asistencia.query.join(Inscripcion).filter(
        Inscripcion.curso_id == curso_id,
        Asistencia.fecha == fecha_obj
    ).all()
    
    asistencias_dict = {a.inscripcion_id: a for a in asistencias_existentes}
    
    dia_no_lectivo = DiaNoLectivo.query.filter(
        DiaNoLectivo.ciclo_id == curso.ciclo_id,
        DiaNoLectivo.fecha == fecha_obj,
        (DiaNoLectivo.curso_id == None) | (DiaNoLectivo.curso_id == curso.id)
    ).first()

    es_sesion_institucional = any(getattr(a, 'es_institucional', False) for a in asistencias_existentes)
    motivo_institucional_sesion = next((a.motivo_institucional for a in asistencias_existentes if getattr(a, 'es_institucional', False) and a.motivo_institucional), None)
    if not motivo_institucional_sesion and dia_no_lectivo:
        motivo_institucional_sesion = f"{dia_no_lectivo.tipo}: {dia_no_lectivo.motivo}"

    return render_template('asistencias/formulario_masivo.html',
                         curso_id=curso_id,
                         fecha=fecha_obj,
                         inscripciones=inscripciones,
                         asistencias_dict=asistencias_dict,
                         dia_no_lectivo=dia_no_lectivo,
                         es_sesion_institucional=es_sesion_institucional,
                         motivo_institucional_sesion=motivo_institucional_sesion)

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
        ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
        
        registros_procesados = 0
        
        for inscripcion in inscripciones:
            # Verificar si ya existe registro para esta fecha
            asistencia_existente = Asistencia.query.filter_by(
                inscripcion_id=inscripcion.id,
                fecha=fecha
            ).first()
            
            presente = request.form.get(f'presente_{inscripcion.id}') == 'on'
            justificado = request.form.get(f'justificado_{inscripcion.id}') == 'on'
            observaciones = request.form.get(f'observaciones_{inscripcion.id}', '')
            
            if asistencia_existente:
                # Actualizar registro existente
                asistencia_existente.presente = presente
                asistencia_existente.justificado = justificado
                asistencia_existente.observaciones = observaciones or None
                asistencia_existente.es_institucional = False
                asistencia_existente.motivo_institucional = None
                registros_procesados += 1
            else:
                # Crear nuevo registro
                nueva_asistencia = Asistencia(
                    inscripcion_id=inscripcion.id,
                    fecha=fecha,
                    presente=presente,
                    justificado=justificado,
                    es_institucional=False,
                    motivo_institucional=None,
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

@asistencias_bp.route('/masiva/suspender_sesion', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def suspender_sesion_masiva():
    """Declara una sesión como suspendida institucionalmente (Feriado, Asueto, Emergencia, Actividad)"""
    try:
        curso_id = request.form.get('curso_id', type=int)
        fecha_str = request.form.get('fecha')
        tipo_suspension = request.form.get('tipo_suspension', 'FERIADO')
        motivo_detalle = request.form.get('motivo_detalle', '').strip()
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        curso = Curso.query.get_or_404(curso_id)
        if current_user.rol in ('docente', 'coordinador'):
            if not curso_pertenece_al_usuario(curso):
                flash('No tiene permisos para modificar asistencias en este curso', 'danger')
                return redirect(url_for('asistencias.index'))
                
        motivo_completo = f"{tipo_suspension}: {motivo_detalle}".strip() if motivo_detalle else tipo_suspension
        
        inscripciones = Inscripcion.query.join(Estudiante).filter(
            Inscripcion.curso_id == curso_id,
            Inscripcion.estado == 'ACTIVO'
        ).all()
        
        for ins in inscripciones:
            asist = Asistencia.query.filter_by(inscripcion_id=ins.id, fecha=fecha).first()
            if not asist:
                asist = Asistencia(
                    inscripcion_id=ins.id,
                    fecha=fecha
                )
                db.session.add(asist)
            
            asist.presente = False
            asist.justificado = True
            asist.es_institucional = True
            asist.motivo_institucional = motivo_completo
            asist.observaciones = f"Suspensión Institucional ({motivo_completo})"
            
        db.session.commit()
        
        # Recalcular riesgo de los estudiantes
        from app.services.seguimiento_service import SeguimientoService
        for ins in inscripciones:
            SeguimientoService.recalcular_estudiante(ins.estudiante_id)
            
        flash(f'Sesión del {fecha.strftime("%d/%m/%Y")} declarada exitosamente como suspensión institucional ({motivo_completo}). Los estudiantes quedan exonerados de inasistencia.', 'success')
        return redirect(url_for('asistencias.editar_masiva_sesion', curso_id=curso_id, fecha=fecha_str))
    except Exception as e:
        db.session.rollback()
        flash('Error al suspender la sesión institucional. Intente nuevamente.', 'danger')
        return redirect(url_for('asistencias.index'))

@asistencias_bp.route('/masiva/restaurar_sesion', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def restaurar_sesion_normal():
    """Restaura una sesión suspendida institucionalmente a sesión lectiva regular"""
    try:
        curso_id = request.form.get('curso_id', type=int)
        fecha_str = request.form.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        curso = Curso.query.get_or_404(curso_id)
        if current_user.rol in ('docente', 'coordinador'):
            if not curso_pertenece_al_usuario(curso):
                flash('No tiene permisos para modificar asistencias en este curso', 'danger')
                return redirect(url_for('asistencias.index'))
                
        inscripciones = Inscripcion.query.filter_by(curso_id=curso_id, estado='ACTIVO').all()
        for ins in inscripciones:
            asist = Asistencia.query.filter_by(inscripcion_id=ins.id, fecha=fecha).first()
            if asist:
                asist.es_institucional = False
                asist.motivo_institucional = None
                asist.observaciones = None
                
        db.session.commit()
        
        from app.services.seguimiento_service import SeguimientoService
        for ins in inscripciones:
            SeguimientoService.recalcular_estudiante(ins.estudiante_id)
            
        flash('La sesión ha sido restaurada a sesión lectiva regular. Ahora puede registrar asistencias con normalidad.', 'info')
        return redirect(url_for('asistencias.editar_masiva_sesion', curso_id=curso_id, fecha=fecha_str))
    except Exception as e:
        db.session.rollback()
        flash('Error al restaurar la sesión.', 'danger')
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
        db.func.sum(db.case(((Asistencia.presente == True) & (Asistencia.es_institucional != True), 1), else_=0)).label('asistencias'),
        db.func.sum(db.case(((Asistencia.justificado == True) & (Asistencia.es_institucional != True), 1), else_=0)).label('justificadas'),
        db.func.sum(db.case((Asistencia.es_institucional == True, 1), else_=0)).label('institucionales')
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
        institucionales = stat.institucionales or 0
        clases_efectivas = max(total_clases - institucionales, 0)
        
        if clases_efectivas > 0:
            porcentaje_asistencia = ((asistencias + justificadas) / clases_efectivas) * 100
            porcentaje_efectiva = (asistencias / clases_efectivas) * 100
        else:
            porcentaje_asistencia = 100.0
            porcentaje_efectiva = 100.0
        
        estadisticas_con_porcentajes.append({
            'curso': stat.nombre_curso,
            'estudiante': f"{stat.apellidos} {stat.nombres}",
            'total_clases': total_clases,
            'clases_efectivas': clases_efectivas,
            'institucionales': institucionales,
            'asistencias': asistencias,
            'justificadas': justificadas,
            'porcentaje_asistencia': porcentaje_asistencia,
            'porcentaje_efectiva': porcentaje_efectiva
        })
    
    # Para los filtros: cursos del ciclo activo
    from app.services.config_service import get_ciclo_activo
    ciclo = get_ciclo_activo()
    if ciclo:
        if current_user.rol in ('docente', 'coordinador'):
            cursos = Curso.query.filter_by(activo=True, docente_id=current_user.id, ciclo_id=ciclo.id).order_by('semestre', 'nombre_curso').all()
        else:
            cursos = Curso.query.filter_by(activo=True, ciclo_id=ciclo.id).order_by('semestre', 'nombre_curso').all()
    else:
        cursos = []
    
    estudiantes = Estudiante.query.filter_by(activo=True).order_by('apellidos', 'nombres').all()
    semestres = db.session.query(Curso.semestre).distinct().order_by(Curso.semestre.desc()).all()
    
    return render_template('asistencias/estadisticas.html',
                         estadisticas=estadisticas_con_porcentajes,
                         cursos=cursos,
                         estudiantes=estudiantes,
                         semestres=semestres,
                         curso_id=curso_id,
                         estudiante_id=estudiante_id,
                         semestre=semestre)

@asistencias_bp.route('/dias-no-lectivos', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def dias_no_lectivos():
    """Gestión de días no lectivos, feriados y asuetos del ciclo académico"""
    from app.services.config_service import get_ciclo_activo
    ciclo_activo = get_ciclo_activo()
    
    filtro_ciclo_id = request.args.get('ciclo_id', type=int)
    ciclo_id = filtro_ciclo_id or (ciclo_activo.id if ciclo_activo else None)
    
    if request.method == 'POST':
        if current_user.rol not in ('administrador', 'coordinador'):
            flash('Solo administradores y coordinadores pueden programar días no lectivos', 'danger')
            return redirect(url_for('asistencias.dias_no_lectivos'))
            
        try:
            fecha_str = request.form.get('fecha')
            tipo = request.form.get('tipo', 'FERIADO')
            motivo = request.form.get('motivo', '').strip()
            curso_id_form = request.form.get('curso_id', type=int) or None
            aplicar_a_todos = request.form.get('aplicar_todos') == 'on'
            observaciones = request.form.get('observaciones', '').strip()
            es_recuperable = request.form.get('es_recuperable') == 'on'
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            target_ciclo_id = request.form.get('ciclo_id', type=int) or ciclo_id
            
            # Crear registro DiaNoLectivo
            nuevo_dia = DiaNoLectivo(
                ciclo_id=target_ciclo_id,
                curso_id=None if aplicar_a_todos else curso_id_form,
                fecha=fecha,
                tipo=tipo,
                motivo=motivo,
                es_recuperable=es_recuperable,
                observaciones=observaciones or None
            )
            db.session.add(nuevo_dia)
            db.session.flush()
            
            # Aplicar a las asistencias de los cursos
            cursos_afectados = []
            if aplicar_a_todos:
                cursos_afectados = Curso.query.filter_by(ciclo_id=target_ciclo_id, activo=True).all()
            elif curso_id_form:
                c = Curso.query.get(curso_id_form)
                if c:
                    cursos_afectados = [c]
                    
            estudiantes_afectados = set()
            for c in cursos_afectados:
                for ins in c.inscripciones:
                    if ins.estado == 'ACTIVO':
                        asist = Asistencia.query.filter_by(inscripcion_id=ins.id, fecha=fecha).first()
                        if not asist:
                            asist = Asistencia(inscripcion_id=ins.id, fecha=fecha)
                            db.session.add(asist)
                        asist.presente = False
                        asist.justificado = True
                        asist.es_institucional = True
                        asist.motivo_institucional = f"{tipo}: {motivo}"
                        asist.observaciones = f"Día No Lectivo ({tipo}): {motivo}"
                        estudiantes_afectados.add(ins.estudiante_id)
                        
            db.session.commit()
            
            # Recalcular riesgo para los estudiantes afectados
            from app.services.seguimiento_service import SeguimientoService
            for est_id in estudiantes_afectados:
                SeguimientoService.recalcular_estudiante(est_id)
                
            flash(f'Día no lectivo registrado con éxito ({tipo}: {motivo}). Se aplicó a {len(cursos_afectados)} cursos.', 'success')
            return redirect(url_for('asistencias.dias_no_lectivos', ciclo_id=target_ciclo_id))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el día no lectivo.', 'danger')
            
    # Listar días no lectivos
    query = DiaNoLectivo.query
    if ciclo_id:
        query = query.filter_by(ciclo_id=ciclo_id)
    dias = query.order_by(DiaNoLectivo.fecha.desc()).all()
    
    ciclos = Ciclo.query.order_by(Ciclo.fecha_inicio.desc()).all() if current_user.rol == 'administrador' else []
    cursos = Curso.query.filter_by(ciclo_id=ciclo_id, activo=True).order_by(Curso.nombre_curso).all() if ciclo_id else []
    
    return render_template('asistencias/dias_no_lectivos.html',
                         dias=dias,
                         ciclo_id=ciclo_id,
                         ciclos=ciclos,
                         cursos=cursos,
                         ciclo_activo=ciclo_activo)

@asistencias_bp.route('/dias-no-lectivos/<int:id>/eliminar', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def eliminar_dia_no_lectivo(id):
    """Eliminar un día no lectivo programado"""
    try:
        dia = DiaNoLectivo.query.get_or_404(id)
        ciclo_id = dia.ciclo_id
        fecha = dia.fecha
        curso_id = dia.curso_id
        
        # Eliminar las asistencias institucionales asociadas
        if curso_id:
            asists = Asistencia.query.join(Inscripcion).filter(
                Inscripcion.curso_id == curso_id,
                Asistencia.fecha == fecha,
                Asistencia.es_institucional == True
            ).all()
        else:
            asists = Asistencia.query.join(Inscripcion).join(Curso).filter(
                Curso.ciclo_id == ciclo_id,
                Asistencia.fecha == fecha,
                Asistencia.es_institucional == True
            ).all()
            
        estudiantes_afectados = set()
        for a in asists:
            estudiantes_afectados.add(a.inscripcion.estudiante_id)
            db.session.delete(a)
            
        db.session.delete(dia)
        db.session.commit()
        
        from app.services.seguimiento_service import SeguimientoService
        for est_id in estudiantes_afectados:
            SeguimientoService.recalcular_estudiante(est_id)
            
        flash('Día no lectivo eliminado correctamente y registros de sesión restablecidos.', 'success')
        return redirect(url_for('asistencias.dias_no_lectivos', ciclo_id=ciclo_id))
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el día no lectivo.', 'danger')
        return redirect(url_for('asistencias.dias_no_lectivos'))