# app/modules/evaluaciones/routes.py
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import evaluaciones_bp
from app.models import Evaluacion, Curso, Nota, Inscripcion, Estudiante, IndicadorLogro
from app.extensions import db
from app.decorators import roles_required, curso_pertenece_al_usuario
from .forms import EvaluacionForm, NotaForm, IndicadorForm
from datetime import datetime, timezone

# ===== RUTAS PARA EVALUACIONES =====

@evaluaciones_bp.route('/')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def index():
    """Lista de todas las evaluaciones"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Query base con join para curso
    evaluaciones_query = Evaluacion.query.join(Curso)

    from app.services.config_service import get_ciclo_activo
    from app.models import Ciclo
    
    ciclo_activo = get_ciclo_activo()
    filtro_ciclo_id = request.args.get('filtro_ciclo_id', type=int)
    
    if current_user.rol == 'administrador' and filtro_ciclo_id:
        if filtro_ciclo_id != -1:
            evaluaciones_query = evaluaciones_query.filter(Curso.ciclo_id == filtro_ciclo_id)
    else:
        if ciclo_activo:
            evaluaciones_query = evaluaciones_query.filter(Curso.ciclo_id == ciclo_activo.id)
        else:
            evaluaciones_query = evaluaciones_query.filter(db.false())

    # Filtro por rol: docentes y coordinadores solo ven evaluaciones de sus cursos
    if current_user.rol in ('docente', 'coordinador'):
        evaluaciones_query = evaluaciones_query.filter(Curso.docente_id == current_user.id)

    # Búsqueda
    search = request.args.get('search', '')
    if search:
        evaluaciones_query = evaluaciones_query.filter(
            db.or_(
                Evaluacion.nombre_evaluacion.ilike(f'%{search}%'),
                Curso.nombre_curso.ilike(f'%{search}%'),
                Curso.codigo_curso.ilike(f'%{search}%')
            )
        )

    # Filtros
    curso_id = request.args.get('curso_id', type=int)
    tipo_evaluacion = request.args.get('tipo_evaluacion', '')
    
    if curso_id:
        evaluaciones_query = evaluaciones_query.filter(Evaluacion.curso_id == curso_id)
    if tipo_evaluacion:
        evaluaciones_query = evaluaciones_query.filter(Evaluacion.tipo_evaluacion == tipo_evaluacion)

    evaluaciones = evaluaciones_query.order_by(
        Curso.semestre.desc(), Curso.nombre_curso, Evaluacion.nombre_evaluacion
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Para los filtros: docentes y coordinadores solo ven sus cursos
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
    
    tipos_evaluacion = [
        'PARCIAL', 'QUIZ', 'TRABAJO', 'PROYECTO', 'LABORATORIO', 'EXAMEN_FINAL', 'OTRO'
    ]
    
    ciclos = Ciclo.query.order_by(Ciclo.fecha_inicio.desc()).all() if current_user.rol == 'administrador' else []

    return render_template('evaluaciones/index.html',
                         evaluaciones=evaluaciones,
                         cursos=cursos,
                         ciclos=ciclos,
                         filtro_ciclo_id=filtro_ciclo_id or (ciclo_activo.id if ciclo_activo else -1),
                         tipos_evaluacion=tipos_evaluacion,
                         search=search,
                         curso_id=curso_id,
                         tipo_evaluacion=tipo_evaluacion)

@evaluaciones_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def crear_evaluacion():
    """Crear nueva evaluación con validación estricta de 100% por Indicador de Logro"""
    curso_id_param = request.form.get('curso_id', type=int) or request.args.get('curso_id', type=int)
    form = EvaluacionForm(curso_id=curso_id_param)
    
    # Si viene curso_id, asegurar indicadores y actualizar choices
    if curso_id_param:
        form.curso_id.data = curso_id_param
        indicadores = IndicadorLogro.query.filter_by(curso_id=curso_id_param).order_by(IndicadorLogro.orden).all()
        if not indicadores:
            il1 = IndicadorLogro(curso_id=curso_id_param, codigo='IL-01', nombre='Indicador de Logro 01', peso=33.33, orden=1)
            il2 = IndicadorLogro(curso_id=curso_id_param, codigo='IL-02', nombre='Indicador de Logro 02', peso=33.33, orden=2)
            il3 = IndicadorLogro(curso_id=curso_id_param, codigo='IL-03', nombre='Indicador de Logro 03', peso=33.34, orden=3)
            db.session.add_all([il1, il2, il3])
            db.session.commit()
            indicadores = [il1, il2, il3]
            
        form.indicador_id.choices = [
            (il.id, f"{il.codigo}: {il.nombre} ({il.peso_disponible:.1f}% disponible)")
            for il in indicadores
        ]
    
    # Para GET request, establecer fecha actual y sugerir peso disponible
    if request.method == 'GET':
        form.fecha_creacion.data = datetime.now(timezone.utc).date()
        if form.indicador_id.choices:
            primer_il = IndicadorLogro.query.get(form.indicador_id.choices[0][0])
            if primer_il and primer_il.peso_disponible > 0:
                form.peso.data = min(primer_il.peso_disponible, 20.0)
            else:
                form.peso.data = 20.0
        else:
            form.peso.data = 20.0
    
    if form.validate_on_submit():
        try:
            # Verificar que el curso pertenece al usuario (docentes y coordinadores)
            if current_user.rol in ('docente', 'coordinador'):
                curso = Curso.query.get(form.curso_id.data)
                if not curso or not curso_pertenece_al_usuario(curso):
                    flash('No tiene permisos para crear evaluaciones en este curso', 'danger')
                    return redirect(url_for('evaluaciones.index'))
            
            # Validar que el indicador pertenece al curso
            indicador = IndicadorLogro.query.get(form.indicador_id.data)
            if not indicador or indicador.curso_id != form.curso_id.data:
                flash('El Indicador de Logro no es válido para este curso', 'danger')
                return render_template('evaluaciones/crear_evaluacion.html', form=form, curso_id=curso_id_param, curso_preselected=bool(curso_id_param))

            # REGLA FUNDAMENTAL: Las evaluaciones de un indicador no deben sobrepasar el 100%
            peso_nuevo = float(form.peso.data)
            peso_actual = indicador.suma_pesos_evaluaciones
            if (peso_actual + peso_nuevo) > 100.001:
                disp = max(100.0 - peso_actual, 0.0)
                flash(f'¡No permitido! La suma de evaluaciones en el indicador {indicador.codigo} no puede sobrepasar el 100%. Actualmente tiene acumulado {peso_actual:.1f}%, por lo que el peso máximo disponible es {disp:.1f}%.', 'danger')
                return render_template('evaluaciones/crear_evaluacion.html', form=form, curso_id=curso_id_param, curso_preselected=bool(curso_id_param))
            
            # Verificar si ya existe la evaluación en el mismo curso
            evaluacion_existente = Evaluacion.query.filter_by(
                nombre_evaluacion=form.nombre_evaluacion.data,
                curso_id=form.curso_id.data
            ).first()
            
            if evaluacion_existente:
                flash('Ya existe una evaluación con este nombre en el mismo curso', 'danger')
                return render_template('evaluaciones/crear_evaluacion.html', form=form, curso_id=curso_id_param, curso_preselected=bool(curso_id_param))
            
            # Crear nueva evaluación vinculada a su Indicador de Logro
            nueva_evaluacion = Evaluacion(
                curso_id=form.curso_id.data,
                indicador_id=form.indicador_id.data,
                nombre_evaluacion=form.nombre_evaluacion.data,
                tipo_evaluacion=form.tipo_evaluacion.data,
                peso=form.peso.data,
                fecha_creacion=form.fecha_creacion.data
            )
            
            db.session.add(nueva_evaluacion)
            db.session.commit()
            
            flash(f'Evaluación asignada exitosamente al {indicador.codigo} con peso de {form.peso.data}%. (Total acumulado en indicador: {indicador.suma_pesos_evaluaciones:.1f}%)', 'success')
            return redirect(url_for('evaluaciones.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al crear la evaluación: {str(e)}', 'danger')
    
    # Mantener curso_id disponible para el template (para el botón "Volver al curso")
    return render_template('evaluaciones/crear_evaluacion.html', form=form, curso_id=curso_id_param, curso_preselected=bool(curso_id_param))

@evaluaciones_bp.route('/<int:evaluacion_id>')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def detalle_evaluacion(evaluacion_id):
    """Detalle de una evaluación específica"""
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    
    # Verificar pertenencia del curso (docentes y coordinadores)
    if current_user.rol in ('docente', 'coordinador'):
        if not curso_pertenece_al_usuario(evaluacion.curso):
            flash('No tiene permisos para ver esta evaluación', 'danger')
            return redirect(url_for('evaluaciones.index'))
    
    # Obtener notas de esta evaluación
    notas = Nota.query.filter_by(
        evaluacion_id=evaluacion_id
    ).join(Inscripcion).join(Estudiante).order_by(Estudiante.apellidos, Estudiante.nombres).all()
    
    # Estadísticas
    total_notas = len(notas)
    promedio = db.session.query(db.func.avg(Nota.nota)).filter_by(
        evaluacion_id=evaluacion_id
    ).scalar() or 0
    nota_maxima = db.session.query(db.func.max(Nota.nota)).filter_by(
        evaluacion_id=evaluacion_id
    ).scalar() or 0
    nota_minima = db.session.query(db.func.min(Nota.nota)).filter_by(
        evaluacion_id=evaluacion_id
    ).scalar() or 0

    return render_template('evaluaciones/detalle_evaluacion.html',
                         evaluacion=evaluacion,
                         notas=notas,
                         total_notas=total_notas,
                         promedio=promedio,
                         nota_maxima=nota_maxima,
                         nota_minima=nota_minima)

@evaluaciones_bp.route('/<int:evaluacion_id>/editar', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def editar_evaluacion(evaluacion_id):
    """Editar evaluación existente con validación estricta de 100% por Indicador de Logro"""
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    
    # Verificar pertenencia del curso (docentes y coordinadores)
    if current_user.rol in ('docente', 'coordinador'):
        if not curso_pertenece_al_usuario(evaluacion.curso):
            flash('No tiene permisos para editar esta evaluación', 'danger')
            return redirect(url_for('evaluaciones.index'))
    
    form = EvaluacionForm(obj=evaluacion)
    
    # Cargar indicadores del curso
    indicadores = IndicadorLogro.query.filter_by(curso_id=evaluacion.curso_id).order_by(IndicadorLogro.orden).all()
    form.indicador_id.choices = [
        (il.id, f"{il.codigo}: {il.nombre} ({il.peso_disponible + (float(evaluacion.peso) if evaluacion.indicador_id == il.id else 0.0):.1f}% disponible)")
        for il in indicadores
    ]
    if request.method == 'GET' and evaluacion.indicador_id:
        form.indicador_id.data = evaluacion.indicador_id
    
    if form.validate_on_submit():
        try:
            # Validar indicador
            indicador = IndicadorLogro.query.get(form.indicador_id.data)
            if not indicador or indicador.curso_id != form.curso_id.data:
                flash('El Indicador de Logro seleccionado no pertenece al curso seleccionado', 'danger')
                return render_template('evaluaciones/editar_evaluacion.html', form=form, evaluacion=evaluacion)
                
            # REGLA: Suma de pesos en el indicador no puede sobrepasar el 100% (excluyendo la evaluación actual)
            peso_nuevo = float(form.peso.data)
            peso_actual_otros = sum(float(e.peso or 0) for e in indicador.evaluaciones if e.id != evaluacion.id)
            if (peso_actual_otros + peso_nuevo) > 100.001:
                disp = max(100.0 - peso_actual_otros, 0.0)
                flash(f'¡No permitido! La suma de evaluaciones en el indicador {indicador.codigo} no debe sobrepasar el 100%. Actualmente tiene acumulado {peso_actual_otros:.1f}%, por lo que el peso máximo disponible es {disp:.1f}%.', 'danger')
                return render_template('evaluaciones/editar_evaluacion.html', form=form, evaluacion=evaluacion)

            # Verificar si ya existe la evaluación (excluyendo la actual)
            evaluacion_existente = Evaluacion.query.filter(
                Evaluacion.nombre_evaluacion == form.nombre_evaluacion.data,
                Evaluacion.curso_id == form.curso_id.data,
                Evaluacion.id != evaluacion_id
            ).first()
            
            if evaluacion_existente:
                flash('Ya existe una evaluación con este nombre en el mismo curso', 'danger')
                return render_template('evaluaciones/editar_evaluacion.html', form=form, evaluacion=evaluacion)
            
            # Actualizar evaluación
            evaluacion.curso_id = form.curso_id.data
            evaluacion.indicador_id = form.indicador_id.data
            evaluacion.nombre_evaluacion = form.nombre_evaluacion.data
            evaluacion.tipo_evaluacion = form.tipo_evaluacion.data
            evaluacion.peso = form.peso.data
            evaluacion.fecha_creacion = form.fecha_creacion.data
            
            db.session.commit()
            
            flash('Evaluación actualizada exitosamente', 'success')
            return redirect(url_for('evaluaciones.detalle_evaluacion', evaluacion_id=evaluacion.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al actualizar la evaluación. Intente de nuevo.', 'danger')
    
    return render_template('evaluaciones/editar_evaluacion.html', form=form, evaluacion=evaluacion)

@evaluaciones_bp.route('/<int:evaluacion_id>/eliminar', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def eliminar_evaluacion(evaluacion_id):
    """Eliminar evaluación"""
    try:
        evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
        
        # Verificar si tiene registros relacionados
        if evaluacion.notas:
            flash('No se puede eliminar la evaluación porque tiene notas relacionadas', 'danger')
            return redirect(url_for('evaluaciones.detalle_evaluacion', evaluacion_id=evaluacion_id))
        
        db.session.delete(evaluacion)
        db.session.commit()
        
        flash('Evaluación eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al eliminar la evaluación. Intente de nuevo.', 'danger')
    
    return redirect(url_for('evaluaciones.index'))

@evaluaciones_bp.route('/buscar')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def buscar():
    """Endpoint AJAX para búsqueda en tiempo real de evaluaciones"""
    q = request.args.get('q', '').strip()
    
    if not q:
        return jsonify({'evaluaciones': [], 'total': 0})
        
    evaluaciones_query = Evaluacion.query.join(Curso)
    
    # Filtro por rol: docentes y coordinadores solo ven evaluaciones de sus cursos
    if current_user.rol in ('docente', 'coordinador'):
        evaluaciones_query = evaluaciones_query.filter(Curso.docente_id == current_user.id)
    
    resultados = evaluaciones_query.filter(
        db.or_(
            Evaluacion.nombre_evaluacion.ilike(f'%{q}%'),
            Curso.nombre_curso.ilike(f'%{q}%'),
            Curso.codigo_curso.ilike(f'%{q}%')
        )
    ).order_by(Curso.semestre.desc(), Curso.nombre_curso, Evaluacion.nombre_evaluacion).limit(20).all()
    
    data = []
    for e in resultados:
        data.append({
            'id': e.id,
            'nombre_evaluacion': e.nombre_evaluacion,
            'curso_nombre': e.curso.nombre_curso,
            'curso_codigo': e.curso.codigo_curso,
            'curso_semestre': e.curso.semestre,
            'tipo_evaluacion': e.tipo_evaluacion,
            'peso': e.peso,
            'fecha': e.fecha_creacion.strftime('%d/%m/%Y'),
            'notas_count': len(e.notas),
            'url_detalle': url_for('evaluaciones.detalle_evaluacion', evaluacion_id=e.id),
            'url_editar': url_for('evaluaciones.editar_evaluacion', evaluacion_id=e.id),
            'url_eliminar': url_for('evaluaciones.eliminar_evaluacion', evaluacion_id=e.id),
            'url_calificar': url_for('evaluaciones.calificar_masiva', evaluacion_id=e.id)
        })
        
    return jsonify({'evaluaciones': data, 'total': len(data)})

@evaluaciones_bp.route('/api/estudiantes-por-curso/<int:curso_id>')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def estudiantes_por_curso(curso_id):
    """API: Obtener estudiantes inscritos en un curso"""
    inscripciones = Inscripcion.query.join(Estudiante).filter(
        Inscripcion.curso_id == curso_id,
        Inscripcion.estado == 'ACTIVO',
        Estudiante.activo == True
    ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
    
    data = [{
        'id': ins.estudiante.id,
        'texto': f"{ins.estudiante.codigo_estudiante} - {ins.estudiante.apellidos} {ins.estudiante.nombres}"
    } for ins in inscripciones]
    
    return jsonify({'estudiantes': data})

@evaluaciones_bp.route('/api/evaluaciones-por-curso/<int:curso_id>')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def evaluaciones_por_curso(curso_id):
    """API: Obtener evaluaciones de un curso"""
    evaluaciones = Evaluacion.query.filter_by(curso_id=curso_id).order_by(Evaluacion.nombre_evaluacion).all()
    
    data = [{
        'id': e.id,
        'texto': f"{e.nombre_evaluacion} ({e.tipo_evaluacion})"
    } for e in evaluaciones]
    
    return jsonify({'evaluaciones': data})

# ===== RUTAS PARA NOTAS =====

@evaluaciones_bp.route('/notas')
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def notas_index():
    """Lista de todas las notas"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Query base con joins y carga anticipada (eager loading)
    from sqlalchemy.orm import joinedload
    notas_query = Nota.query.options(
        joinedload(Nota.evaluacion),
        joinedload(Nota.inscripcion).joinedload(Inscripcion.estudiante),
        joinedload(Nota.inscripcion).joinedload(Inscripcion.curso)
    ).join(Inscripcion).join(Estudiante).join(Evaluacion).join(Curso)

    from app.services.config_service import get_ciclo_activo
    from app.models import Ciclo
    
    ciclo_activo = get_ciclo_activo()
    filtro_ciclo_id = request.args.get('filtro_ciclo_id', type=int)
    
    if current_user.rol == 'administrador' and filtro_ciclo_id:
        if filtro_ciclo_id != -1:
            notas_query = notas_query.filter(Curso.ciclo_id == filtro_ciclo_id)
    else:
        if ciclo_activo:
            notas_query = notas_query.filter(Curso.ciclo_id == ciclo_activo.id)
        else:
            notas_query = notas_query.filter(db.false())

    # Filtro por rol: docentes y coordinadores solo ven notas de sus cursos
    if current_user.rol in ('docente', 'coordinador'):
        notas_query = notas_query.filter(Curso.docente_id == current_user.id)

    # Filtros
    estudiante_id = request.args.get('estudiante_id', type=int)
    curso_id = request.args.get('curso_id', type=int)
    evaluacion_id = request.args.get('evaluacion_id', type=int)
    
    if estudiante_id:
        notas_query = notas_query.filter(Inscripcion.estudiante_id == estudiante_id)
    if curso_id:
        notas_query = notas_query.filter(Inscripcion.curso_id == curso_id)
    if evaluacion_id:
        notas_query = notas_query.filter(Nota.evaluacion_id == evaluacion_id)

    notas = notas_query.order_by(
        Nota.fecha_registro.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Para los filtros: docentes y coordinadores solo ven sus cursos
    estudiantes = Estudiante.query.filter_by(activo=True).order_by('apellidos', 'nombres').all()
    
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
    
    evaluaciones = Evaluacion.query.join(Curso).filter(
        Curso.activo == True
    )
    if target_ciclo_id:
        evaluaciones = evaluaciones.filter(Curso.ciclo_id == target_ciclo_id)
    evaluaciones = evaluaciones.order_by(Curso.nombre_curso, Evaluacion.nombre_evaluacion).all()

    estudiante_actual = next((e for e in estudiantes if e.id == estudiante_id), None) if estudiante_id else None
    estudiante_nombre_actual = f"{estudiante_actual.codigo_estudiante} - {estudiante_actual.apellidos} {estudiante_actual.nombres}" if estudiante_actual else ''

    ciclos = Ciclo.query.order_by(Ciclo.fecha_inicio.desc()).all() if current_user.rol == 'administrador' else []

    return render_template('evaluaciones/notas_index.html',
                         notas=notas,
                         estudiantes=estudiantes,
                         cursos=cursos,
                         evaluaciones=evaluaciones,
                         ciclos=ciclos,
                         filtro_ciclo_id=filtro_ciclo_id or (ciclo_activo.id if ciclo_activo else -1),
                         estudiante_id=estudiante_id,
                         curso_id=curso_id,
                         evaluacion_id=evaluacion_id,
                         estudiante_nombre_actual=estudiante_nombre_actual)

@evaluaciones_bp.route('/notas/crear', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def crear_nota():
    """Crear nueva nota"""
    form = NotaForm()
    
    # Para GET request, establecer fecha actual como default
    if request.method == 'GET':
        form.fecha_registro.data = datetime.now(timezone.utc).date()
    
    # Si hay curso_id en el POST, cargar las choices dinámicas
    if request.method == 'POST' and form.curso_id.data:
        curso_id = form.curso_id.data
        
        # Cargar estudiantes del curso seleccionado
        inscripciones = Inscripcion.query.join(Estudiante).filter(
            Inscripcion.curso_id == curso_id,
            Inscripcion.estado == 'ACTIVO',
            Estudiante.activo == True
        ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
        form.estudiante_id.choices = [
            (ins.estudiante_id, f"{ins.estudiante.codigo_estudiante} - {ins.estudiante.apellidos} {ins.estudiante.nombres}")
            for ins in inscripciones
        ]
        
        # Cargar evaluaciones del curso seleccionado
        evaluaciones = Evaluacion.query.filter_by(curso_id=curso_id).order_by(Evaluacion.nombre_evaluacion).all()
        form.evaluacion_id.choices = [
            (e.id, f"{e.nombre_evaluacion} ({e.tipo_evaluacion})")
            for e in evaluaciones
        ]
    
    if form.validate_on_submit():
        try:
            # Resolver inscripcion_id desde curso_id + estudiante_id
            inscripcion = Inscripcion.query.filter_by(
                curso_id=form.curso_id.data,
                estudiante_id=form.estudiante_id.data,
                estado='ACTIVO'
            ).first()
            
            if not inscripcion:
                flash('No se encontró una inscripción activa para este estudiante en el curso seleccionado', 'danger')
                return render_template('evaluaciones/crear_nota.html', form=form)
            
            # Verificar pertenencia del curso (docentes y coordinadores)
            if current_user.rol in ('docente', 'coordinador'):
                evaluacion = Evaluacion.query.get(form.evaluacion_id.data)
                if not evaluacion or not curso_pertenece_al_usuario(evaluacion.curso):
                    flash('No tiene permisos para crear notas en este curso', 'danger')
                    return redirect(url_for('evaluaciones.notas_index'))
            
            # Verificar si ya existe la nota para esta inscripción y evaluación
            nota_existente = Nota.query.filter_by(
                inscripcion_id=inscripcion.id,
                evaluacion_id=form.evaluacion_id.data
            ).first()
            
            if nota_existente:
                flash('Ya existe una nota para este estudiante en esta evaluación', 'danger')
                return render_template('evaluaciones/crear_nota.html', form=form)
            
            # Crear nueva nota
            nueva_nota = Nota(
                inscripcion_id=inscripcion.id,
                evaluacion_id=form.evaluacion_id.data,
                nota=form.nota.data,
                fecha_registro=form.fecha_registro.data,
                observaciones=form.observaciones.data or None
            )
            
            db.session.add(nueva_nota)
            db.session.commit()
            
            flash('Nota creada exitosamente', 'success')
            return redirect(url_for('evaluaciones.notas_index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al crear la nota. Intente de nuevo.', 'danger')
    
    return render_template('evaluaciones/crear_nota.html', form=form)

@evaluaciones_bp.route('/notas/<int:nota_id>/editar', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def editar_nota(nota_id):
    """Editar nota existente"""
    nota = Nota.query.get_or_404(nota_id)
    
    # Verificar pertenencia del curso (docentes y coordinadores)
    if current_user.rol in ('docente', 'coordinador'):
        evaluacion_check = Evaluacion.query.get(nota.evaluacion_id)
        if not evaluacion_check or not curso_pertenece_al_usuario(evaluacion_check.curso):
            flash('No tiene permisos para editar esta nota', 'danger')
            return redirect(url_for('evaluaciones.notas_index'))
    
    # Pre-cargar el formulario con los datos actuales en GET
    if request.method == 'GET':
        inscripcion = Inscripcion.query.get(nota.inscripcion_id)
        form = NotaForm()
        form.curso_id.data = inscripcion.curso_id
        form.estudiante_id.data = inscripcion.estudiante_id
        form.evaluacion_id.data = nota.evaluacion_id
        form.nota.data = nota.nota
        form.fecha_registro.data = nota.fecha_registro
        form.observaciones.data = nota.observaciones
        
        # Cargar choices con los datos actuales
        form.estudiante_id.choices = [
            (inscripcion.estudiante_id, f"{inscripcion.estudiante.codigo_estudiante} - {inscripcion.estudiante.apellidos} {inscripcion.estudiante.nombres}")
        ]
        form.evaluacion_id.choices = [
            (nota.evaluacion_id, f"{nota.evaluacion.nombre_evaluacion} ({nota.evaluacion.tipo_evaluacion})")
        ]
        
        return render_template('evaluaciones/editar_nota.html', form=form, nota=nota)
    
    # POST: reconstruir form y cargar choices dinámicamente
    form = NotaForm()
    
    if form.curso_id.data:
        curso_id = form.curso_id.data
        
        inscripciones = Inscripcion.query.join(Estudiante).filter(
            Inscripcion.curso_id == curso_id,
            Inscripcion.estado == 'ACTIVO',
            Estudiante.activo == True
        ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
        form.estudiante_id.choices = [
            (ins.estudiante_id, f"{ins.estudiante.codigo_estudiante} - {ins.estudiante.apellidos} {ins.estudiante.nombres}")
            for ins in inscripciones
        ]
        
        evaluaciones = Evaluacion.query.filter_by(curso_id=curso_id).order_by(Evaluacion.nombre_evaluacion).all()
        form.evaluacion_id.choices = [
            (e.id, f"{e.nombre_evaluacion} ({e.tipo_evaluacion})")
            for e in evaluaciones
        ]
    
    if form.validate_on_submit():
        try:
            inscripcion = Inscripcion.query.filter_by(
                curso_id=form.curso_id.data,
                estudiante_id=form.estudiante_id.data,
                estado='ACTIVO'
            ).first()
            
            if not inscripcion:
                flash('No se encontró una inscripción activa para este estudiante en el curso seleccionado', 'danger')
                return render_template('evaluaciones/editar_nota.html', form=form, nota=nota)
            
            nota_existente = Nota.query.filter(
                Nota.inscripcion_id == inscripcion.id,
                Nota.evaluacion_id == form.evaluacion_id.data,
                Nota.id != nota_id
            ).first()
            
            if nota_existente:
                flash('Ya existe una nota para este estudiante en esta evaluación', 'danger')
                return render_template('evaluaciones/editar_nota.html', form=form, nota=nota)
            
            nota.inscripcion_id = inscripcion.id
            nota.evaluacion_id = form.evaluacion_id.data
            nota.nota = form.nota.data
            nota.fecha_registro = form.fecha_registro.data
            nota.observaciones = form.observaciones.data or None
            
            db.session.commit()
            
            flash('Nota actualizada exitosamente', 'success')
            return redirect(url_for('evaluaciones.notas_index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al actualizar la nota. Intente de nuevo.', 'danger')
    
    return render_template('evaluaciones/editar_nota.html', form=form, nota=nota)

@evaluaciones_bp.route('/notas/<int:nota_id>/eliminar', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def eliminar_nota(nota_id):
    """Eliminar nota"""
    try:
        nota = Nota.query.get_or_404(nota_id)
        
        db.session.delete(nota)
        db.session.commit()
        
        flash('Nota eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al eliminar la nota. Intente de nuevo.', 'danger')
    
        return redirect(url_for('evaluaciones.notas_index'))

# ===== RUTAS PARA REGISTRO MASIVO =====

@evaluaciones_bp.route('/notas/masiva', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def registro_masivo():
    """Formulario inicial para registro masivo de notas"""
    # Docentes y coordinadores solo ven sus cursos
    if current_user.rol in ('docente', 'coordinador'):
        cursos = Curso.query.filter_by(activo=True, docente_id=current_user.id).all()
    else:
        cursos = Curso.query.filter_by(activo=True).all()
    
    evaluaciones = []
    
    curso_id = request.args.get('curso_id', type=int)
    if curso_id:
        evaluaciones = Evaluacion.query.filter_by(curso_id=curso_id).all()
        
    return render_template('evaluaciones/registro_masivo_init.html', 
                         cursos=cursos, 
                         evaluaciones=evaluaciones,
                         curso_id=curso_id)

@evaluaciones_bp.route('/notas/masiva/formulario', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def formulario_masivo():
    """Formulario para ingresar las notas de todos los estudiantes"""
    evaluacion_id = request.form.get('evaluacion_id', type=int)
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    
    # Verificar pertenencia del curso (docentes y coordinadores)
    if current_user.rol in ('docente', 'coordinador'):
        if not curso_pertenece_al_usuario(evaluacion.curso):
            flash('No tiene permisos para registrar notas en este curso', 'danger')
            return redirect(url_for('evaluaciones.registro_masivo'))
    
    # Estudiantes inscritos
    inscripciones = Inscripcion.query.filter_by(
        curso_id=evaluacion.curso_id, 
        estado='ACTIVO'
    ).join(Estudiante).order_by(Estudiante.apellidos, Estudiante.nombres).all()
    
    # Obtener notas existentes si las hay
    notas_existentes = {n.inscripcion_id: n for n in Nota.query.filter_by(evaluacion_id=evaluacion_id).all()}
    
    return render_template('evaluaciones/formulario_masivo.html',
                         evaluacion=evaluacion,
                         inscripciones=inscripciones,
                         notas_existentes=notas_existentes)

@evaluaciones_bp.route('/evaluacion/<int:evaluacion_id>/calificar_masiva', methods=['GET'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def calificar_masiva(evaluacion_id):
    """Acceso directo al formulario de calificación masiva de una evaluación"""
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    
    # Verificar pertenencia del curso (docentes y coordinadores)
    if current_user.rol in ('docente', 'coordinador'):
        if not curso_pertenece_al_usuario(evaluacion.curso):
            flash('No tiene permisos para registrar notas en este curso', 'danger')
            return redirect(url_for('evaluaciones.index'))
    
    # Estudiantes inscritos
    inscripciones = Inscripcion.query.filter_by(
        curso_id=evaluacion.curso_id, 
        estado='ACTIVO'
    ).join(Estudiante).order_by(Estudiante.apellidos, Estudiante.nombres).all()
    
    # Obtener notas existentes si las hay
    notas_existentes = {n.inscripcion_id: n for n in Nota.query.filter_by(evaluacion_id=evaluacion_id).all()}
    
    return render_template('evaluaciones/formulario_masivo.html',
                         evaluacion=evaluacion,
                         inscripciones=inscripciones,
                         notas_existentes=notas_existentes)

@evaluaciones_bp.route('/notas/masiva/procesar', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def procesar_masiva():
    """Procesar el registro masivo de notas"""
    try:
        evaluacion_id = request.form.get('evaluacion_id', type=int)
        evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
        
        # Verificar pertenencia del curso (docentes y coordinadores)
        if current_user.rol in ('docente', 'coordinador'):
            if not curso_pertenece_al_usuario(evaluacion.curso):
                flash('No tiene permisos para registrar notas en este curso', 'danger')
                return redirect(url_for('evaluaciones.registro_masivo'))
        
        # Obtener todas las inscripciones del curso
        inscripciones = Inscripcion.query.join(Estudiante).filter(
            Inscripcion.curso_id == evaluacion.curso_id
        ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
        
        for inscripcion in inscripciones:
            nota_valor = request.form.get(f'nota_{inscripcion.id}')
            if nota_valor:
                # Convertir a float, manejar vacío
                try:
                    nota_float = float(nota_valor)
                except ValueError:
                    continue
                
                # Buscar si ya existe
                nota_obj = Nota.query.filter_by(
                    inscripcion_id=inscripcion.id,
                    evaluacion_id=evaluacion_id
                ).first()
                
                if nota_obj:
                    nota_obj.nota = nota_float
                    nota_obj.fecha_registro = datetime.now(timezone.utc).date()
                else:
                    nueva_nota = Nota(
                        inscripcion_id=inscripcion.id,
                        evaluacion_id=evaluacion_id,
                        nota=nota_float,
                        fecha_registro=datetime.now(timezone.utc).date()
                    )
                    db.session.add(nueva_nota)
        
        db.session.commit()
        
        # INTEGRACIÓN: Recalcular riesgo para todos los estudiantes del curso
        from app.services.seguimiento_service import SeguimientoService
        for inscripcion in inscripciones:
            SeguimientoService.recalcular_estudiante(inscripcion.estudiante_id)
            
        flash('Calificaciones registradas y riesgo actualizado exitosamente', 'success')
        return redirect(url_for('evaluaciones.detalle_evaluacion', evaluacion_id=evaluacion_id))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al procesar las calificaciones. Intente de nuevo.', 'danger')
        return redirect(url_for('evaluaciones.index'))

@evaluaciones_bp.route('/curso/<int:curso_id>/consolidado', methods=['GET'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def consolidado_curso(curso_id):
    """Consolidado de notas organizado por Indicadores de Logro con promedios parciales y final"""
    from app.models import Curso, Evaluacion, Inscripcion, Nota, Estudiante, IndicadorLogro
    
    curso = Curso.query.get_or_404(curso_id)
    
    # Verificar pertenencia del curso
    if current_user.rol in ('docente', 'coordinador'):
        from app.decorators import curso_pertenece_al_usuario
        if not curso_pertenece_al_usuario(curso):
            flash('No tiene permisos para ver el consolidado de este curso', 'danger')
            return redirect(url_for('evaluaciones.index'))
            
    # Obtener Indicadores de Logro del curso
    indicadores = IndicadorLogro.query.filter_by(curso_id=curso_id).order_by(IndicadorLogro.orden, IndicadorLogro.id).all()
    
    # Si el curso no tiene indicadores, auto-crear IL-01
    if not indicadores:
        il1 = IndicadorLogro(curso_id=curso_id, codigo='IL-01', nombre='Indicador de Logro 01', peso=100.0, orden=1)
        db.session.add(il1)
        db.session.commit()
        indicadores = [il1]
    
    inscripciones = Inscripcion.query.join(Estudiante).filter(
        Inscripcion.curso_id == curso_id,
        Inscripcion.estado == 'ACTIVO'
    ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
    
    notas_raw = Nota.query.join(Inscripcion).filter(
        Inscripcion.curso_id == curso_id
    ).all()
    
    # Mapeo: {inscripcion_id: {evaluacion_id: nota_float}}
    notas_dict = {}
    for n in notas_raw:
        if n.inscripcion_id not in notas_dict:
            notas_dict[n.inscripcion_id] = {}
        notas_dict[n.inscripcion_id][n.evaluacion_id] = float(n.nota) if n.nota is not None else None
        
    consolidado = []
    
    for ins in inscripciones:
        notas_alumno = notas_dict.get(ins.id, {})
        bloques_il = []
        promedios_para_final = []
        
        for il in indicadores:
            notas_il = []
            suma_pond_il = 0.0
            suma_pesos_il = 0.0
            
            for ev in il.evaluaciones:
                nota_val = notas_alumno.get(ev.id)
                notas_il.append({'evaluacion': ev, 'nota': nota_val})
                if nota_val is not None and ev.peso:
                    suma_pond_il += nota_val * float(ev.peso)
                    suma_pesos_il += float(ev.peso)
                    
            if suma_pesos_il > 0:
                promedio_il = round(suma_pond_il / suma_pesos_il, 1)
            else:
                notas_validas = [n['nota'] for n in notas_il if n['nota'] is not None]
                promedio_il = round(sum(notas_validas) / len(notas_validas), 1) if notas_validas else None
                
            bloques_il.append({
                'indicador': il,
                'notas': notas_il,
                'promedio_il': promedio_il
            })
            
            if promedio_il is not None:
                peso_il = float(il.peso or 0)
                promedios_para_final.append((promedio_il, peso_il))
                
        # Promedio final ponderado de los indicadores de logro
        if promedios_para_final:
            suma_pesos_final = sum(peso for _, peso in promedios_para_final)
            if suma_pesos_final > 0:
                promedio_final = round(sum(p * w for p, w in promedios_para_final) / suma_pesos_final, 1)
            else:
                promedio_final = round(sum(p for p, _ in promedios_para_final) / len(promedios_para_final), 1)
        else:
            promedio_final = 0.0
            
        consolidado.append({
            'estudiante': f"{ins.estudiante.apellidos} {ins.estudiante.nombres}",
            'codigo': ins.estudiante.codigo_estudiante,
            'bloques_il': bloques_il,
            'promedio': promedio_final
        })
        
    return render_template('evaluaciones/consolidado_curso.html',
                         curso=curso,
                         indicadores=indicadores,
                         consolidado=consolidado)

@evaluaciones_bp.route('/api/cursos/<int:curso_id>/indicadores')
@login_required
def api_curso_indicadores(curso_id):
    """API para obtener los indicadores de un curso con sus pesos y disponibilidad"""
    indicadores = IndicadorLogro.query.filter_by(curso_id=curso_id).order_by(IndicadorLogro.orden).all()
    if not indicadores:
        il1 = IndicadorLogro(curso_id=curso_id, codigo='IL-01', nombre='Indicador de Logro 01', peso=33.33, orden=1)
        il2 = IndicadorLogro(curso_id=curso_id, codigo='IL-02', nombre='Indicador de Logro 02', peso=33.33, orden=2)
        il3 = IndicadorLogro(curso_id=curso_id, codigo='IL-03', nombre='Indicador de Logro 03', peso=33.34, orden=3)
        db.session.add_all([il1, il2, il3])
        db.session.commit()
        indicadores = [il1, il2, il3]
        
    return jsonify([{
        'id': il.id,
        'codigo': il.codigo,
        'nombre': il.nombre,
        'peso_il': float(il.peso),
        'peso_acumulado': il.suma_pesos_evaluaciones,
        'peso_disponible': il.peso_disponible,
        'evaluaciones_count': len(il.evaluaciones)
    } for il in indicadores])

@evaluaciones_bp.route('/curso/<int:curso_id>/indicadores', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def gestionar_indicadores(curso_id):
    """Panel de gestión de Indicadores de Logro de una Unidad Didáctica"""
    curso = Curso.query.get_or_404(curso_id)
    if current_user.rol in ('docente', 'coordinador'):
        if not curso_pertenece_al_usuario(curso):
            flash('No tiene permisos para modificar este curso', 'danger')
            return redirect(url_for('evaluaciones.index'))
            
    form = IndicadorForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        codigo_clean = form.codigo.data.strip().upper()
        existente = IndicadorLogro.query.filter_by(curso_id=curso_id, codigo=codigo_clean).first()
        if existente:
            flash(f'Ya existe un indicador con el código {codigo_clean} en este curso', 'danger')
        else:
            indicadores_act = IndicadorLogro.query.filter_by(curso_id=curso_id).all()
            nuevo = IndicadorLogro(
                curso_id=curso_id,
                codigo=codigo_clean,
                nombre=form.nombre.data.strip(),
                peso=form.peso.data,
                orden=int(form.orden.data or len(indicadores_act) + 1)
            )
            db.session.add(nuevo)
            db.session.commit()
            flash(f'Indicador {nuevo.codigo} agregado correctamente.', 'success')
            return redirect(url_for('evaluaciones.gestionar_indicadores', curso_id=curso_id))
            
    indicadores = IndicadorLogro.query.filter_by(curso_id=curso_id).order_by(IndicadorLogro.orden).all()
    suma_pesos_il = sum(float(il.peso) for il in indicadores)
    
    return render_template('evaluaciones/gestionar_indicadores.html',
                         curso=curso,
                         indicadores=indicadores,
                         suma_pesos_il=suma_pesos_il,
                         form=form)