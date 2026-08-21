# app/modules/evaluaciones/routes.py
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import evaluaciones_bp
from app.models import Evaluacion, Curso, Nota, Inscripcion, Estudiante
from app.extensions import db
from app.decorators import roles_required, curso_pertenece_al_usuario
from .forms import EvaluacionForm, NotaForm
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
    if current_user.rol in ('docente', 'coordinador'):
        cursos = Curso.query.filter_by(activo=True, docente_id=current_user.id).order_by('semestre', 'nombre_curso').all()
    else:
        cursos = Curso.query.filter_by(activo=True).order_by('semestre', 'nombre_curso').all()
    
    tipos_evaluacion = [
        'PARCIAL', 'QUIZ', 'TRABAJO', 'PROYECTO', 'LABORATORIO', 'EXAMEN_FINAL', 'OTRO'
    ]

    return render_template('evaluaciones/index.html',
                         evaluaciones=evaluaciones,
                         cursos=cursos,
                         tipos_evaluacion=tipos_evaluacion,
                         search=search,
                         curso_id=curso_id,
                         tipo_evaluacion=tipo_evaluacion)

@evaluaciones_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador', 'docente')
def crear_evaluacion():
    """Crear nueva evaluación"""
    form = EvaluacionForm()
    
    # Para GET request, establecer fecha actual como default
    if request.method == 'GET':
        form.fecha_creacion.data = datetime.now(timezone.utc).date()
        form.peso.data = 100.0  # Valor por defecto
        # Preseleccionar el curso si viene como parámetro (desde detalle del curso)
        curso_id = request.args.get('curso_id', type=int)
        if curso_id:
            form.curso_id.data = curso_id
    
    if form.validate_on_submit():
        try:
            # Verificar que el curso pertenece al usuario (docentes y coordinadores)
            if current_user.rol in ('docente', 'coordinador'):
                curso = Curso.query.get(form.curso_id.data)
                if not curso or not curso_pertenece_al_usuario(curso):
                    flash('No tiene permisos para crear evaluaciones en este curso', 'danger')
                    return redirect(url_for('evaluaciones.index'))
            
            # Verificar si ya existe la evaluación en el mismo curso
            evaluacion_existente = Evaluacion.query.filter_by(
                nombre_evaluacion=form.nombre_evaluacion.data,
                curso_id=form.curso_id.data
            ).first()
            
            if evaluacion_existente:
                flash('Ya existe una evaluación con este nombre en el mismo curso', 'danger')
                return render_template('evaluaciones/crear_evaluacion.html', form=form)
            
            # Crear nueva evaluación
            nueva_evaluacion = Evaluacion(
                curso_id=form.curso_id.data,
                nombre_evaluacion=form.nombre_evaluacion.data,
                tipo_evaluacion=form.tipo_evaluacion.data,
                peso=form.peso.data,
                fecha_creacion=form.fecha_creacion.data
            )
            
            db.session.add(nueva_evaluacion)
            db.session.commit()
            
            flash('Evaluación creada exitosamente', 'success')
            return redirect(url_for('evaluaciones.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al crear la evaluación. Intente de nuevo.', 'danger')
    
    # Mantener curso_id disponible para el template (para el botón "Volver al curso")
    curso_id = request.args.get('curso_id', type=int)
    return render_template('evaluaciones/crear_evaluacion.html', form=form, curso_id=curso_id, curso_preselected=bool(curso_id))

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
    """Editar evaluación existente"""
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    
    # Verificar pertenencia del curso (docentes y coordinadores)
    if current_user.rol in ('docente', 'coordinador'):
        if not curso_pertenece_al_usuario(evaluacion.curso):
            flash('No tiene permisos para editar esta evaluación', 'danger')
            return redirect(url_for('evaluaciones.index'))
    
    form = EvaluacionForm(obj=evaluacion)
    
    if form.validate_on_submit():
        try:
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
            'url_eliminar': url_for('evaluaciones.eliminar_evaluacion', evaluacion_id=e.id)
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

    # Query base con joins
    notas_query = Nota.query.join(Inscripcion).join(Estudiante).join(Evaluacion).join(Curso)

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
    if current_user.rol in ('docente', 'coordinador'):
        cursos = Curso.query.filter_by(activo=True, docente_id=current_user.id).order_by('semestre', 'nombre_curso').all()
    else:
        cursos = Curso.query.filter_by(activo=True).order_by('semestre', 'nombre_curso').all()
    
    evaluaciones = Evaluacion.query.join(Curso).filter(
        Curso.activo == True
    ).order_by(Curso.nombre_curso, Evaluacion.nombre_evaluacion).all()

    estudiante_actual = next((e for e in estudiantes if e.id == estudiante_id), None) if estudiante_id else None
    estudiante_nombre_actual = f"{estudiante_actual.codigo_estudiante} - {estudiante_actual.nombres} {estudiante_actual.apellidos}" if estudiante_actual else ''

    return render_template('evaluaciones/notas_index.html',
                         notas=notas,
                         estudiantes=estudiantes,
                         cursos=cursos,
                         evaluaciones=evaluaciones,
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