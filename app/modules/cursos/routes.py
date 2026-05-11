# app/modules/cursos/routes.py
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import cursos_bp
from datetime import datetime
from app.models import Curso, Inscripcion, Evaluacion, Estudiante, Usuario, Ciclo
from app.extensions import db
from app.services.config_service import cargar_configuracion
from app.decorators import roles_required
from .forms import CursoForm

@cursos_bp.route('/')
@login_required
def index():
    """Lista de todos los cursos"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Query base
    cursos_query = Curso.query
    
    # Filtro por rol
    if current_user.rol == 'docente':
        cursos_query = cursos_query.filter_by(docente_id=current_user.id)

    # Búsqueda
    search = request.args.get('search', '')
    if search:
        cursos_query = cursos_query.filter(
            db.or_(
                Curso.nombre_curso.ilike(f'%{search}%'),
                Curso.codigo_curso.ilike(f'%{search}%'),
                Curso.semestre.ilike(f'%{search}%')
            )
        )

    cursos = cursos_query.order_by(Curso.semestre.desc(), Curso.nombre_curso).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('cursos/index.html',
                         cursos=cursos,
                         search=search)

@cursos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador')
def crear():
    """Crear nuevo curso"""
    form = CursoForm()
    
    docentes = Usuario.query.filter_by(rol='docente', activo=True).all()
    form.docente_id.choices = [(0, '--- Seleccionar Docente ---')] + [(d.id, f"{d.username}") for d in docentes]
    
    if form.validate_on_submit():
        try:
            semestre_val = form.semestre.data
            
            config = cargar_configuracion()
            periodo_actual = config.get('semestre_actual', '2024-1')
            
            # Buscar o crear el ciclo del periodo actual
            ciclo = Ciclo.query.filter_by(codigo_ciclo=periodo_actual).first()
            if not ciclo:
                ciclo = Ciclo(
                    nombre=f"Ciclo {periodo_actual}",
                    codigo_ciclo=periodo_actual,
                    fecha_inicio=datetime.utcnow().date(),
                    fecha_fin=datetime.utcnow().date(),
                    activo=True
                )
                db.session.add(ciclo)
                db.session.flush()

            # Verificar si el código de curso ya existe en este ciclo
            curso_existente = Curso.query.filter_by(
                codigo_curso=form.codigo_curso.data,
                ciclo_id=ciclo.id
            ).first()
            
            if curso_existente:
                flash('Ya existe un curso con este código en el periodo actual', 'danger')
                return render_template('cursos/crear.html', form=form)

            # Crear nuevo curso
            nuevo_curso = Curso(
                codigo_curso=form.codigo_curso.data,
                nombre_curso=form.nombre_curso.data,
                creditos=form.creditos.data,
                semestre=semestre_val,
                ciclo_id=ciclo.id,
                docente_id=form.docente_id.data if form.docente_id.data != 0 else None,
                activo=form.activo.data
            )
            
            db.session.add(nuevo_curso)
            db.session.commit()
            
            flash('Curso creado exitosamente', 'success')
            return redirect(url_for('cursos.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear curso: {str(e)}', 'danger')
    
    return render_template('cursos/crear.html', form=form)


@cursos_bp.route('/<int:curso_id>')
@login_required
def detalle(curso_id):
    """Detalle de un curso específico"""
    curso = Curso.query.get_or_404(curso_id)
    
    if current_user.rol == 'docente' and curso.docente_id != current_user.id:
        flash('No tiene permisos para ver este curso', 'danger')
        return redirect(url_for('cursos.index'))
    
    # Obtener inscripciones del curso
    inscripciones = (
        Inscripcion.query
        .filter_by(curso_id=curso_id)
        .join(Inscripcion.estudiante)               
        .order_by(Estudiante.apellidos)           
        .all()
    )
    
    # Obtener evaluaciones del curso
    evaluaciones = (
        Evaluacion.query
        .filter_by(curso_id=curso_id)
        .order_by(Evaluacion.fecha_creacion)
        .all()
    )
    
    return render_template(
        'cursos/detalle.html',
        curso=curso,
        inscripciones=inscripciones,
        evaluaciones=evaluaciones
    )



@cursos_bp.route('/<int:curso_id>/editar', methods=['GET', 'POST'])
@login_required
@roles_required('administrador', 'coordinador')
def editar(curso_id):
    """Editar curso existente"""
    curso = Curso.query.get_or_404(curso_id)
    form = CursoForm(obj=curso)
    
    docentes = Usuario.query.filter_by(rol='docente', activo=True).all()
    form.docente_id.choices = [(0, '--- Seleccionar Docente ---')] + [(d.id, f"{d.username}") for d in docentes]
    
    # Preseleccionar el docente actual (form obj=curso ya hace esto si es None)
    if curso.docente_id is None and request.method == 'GET':
        form.docente_id.data = 0
    
    if form.validate_on_submit():
        try:
            semestre_val = form.semestre.data
            
            config = cargar_configuracion()
            periodo_actual = config.get('semestre_actual', '2024-1')
            
            # Buscar o crear el ciclo del periodo actual
            ciclo = Ciclo.query.filter_by(codigo_ciclo=periodo_actual).first()
            if not ciclo:
                ciclo = Ciclo(
                    nombre=f"Ciclo {periodo_actual}",
                    codigo_ciclo=periodo_actual,
                    fecha_inicio=datetime.utcnow().date(),
                    fecha_fin=datetime.utcnow().date(),
                    activo=True
                )
                db.session.add(ciclo)
                db.session.flush()

            # Verificar si el código de curso ya existe en este ciclo (excluyendo el actual)
            curso_existente = Curso.query.filter(
                Curso.codigo_curso == form.codigo_curso.data,
                Curso.ciclo_id == ciclo.id,
                Curso.id != curso_id
            ).first()
            
            if curso_existente:
                flash('Ya existe un curso con este código en el periodo actual', 'danger')
                return render_template('cursos/editar.html', form=form, curso=curso)

            # Actualizar curso
            curso.codigo_curso = form.codigo_curso.data
            curso.nombre_curso = form.nombre_curso.data
            curso.creditos = form.creditos.data
            curso.semestre = semestre_val
            curso.ciclo_id = ciclo.id
            curso.docente_id = form.docente_id.data if form.docente_id.data != 0 else None
            curso.activo = form.activo.data
            
            db.session.commit()
            
            flash('Curso actualizado exitosamente', 'success')
            return redirect(url_for('cursos.detalle', curso_id=curso.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar curso: {str(e)}', 'danger')
    
    return render_template('cursos/editar.html', form=form, curso=curso)

@cursos_bp.route('/<int:curso_id>/eliminar', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def eliminar(curso_id):
    """Eliminar curso"""
    try:
        curso = Curso.query.get_or_404(curso_id)
        
        # Verificar si tiene registros relacionados
        if curso.inscripciones:
            flash('No se puede eliminar el curso porque tiene inscripciones relacionadas', 'danger')
            return redirect(url_for('cursos.detalle', curso_id=curso_id))
        
        if curso.evaluaciones:
            flash('No se puede eliminar el curso porque tiene evaluaciones relacionadas', 'danger')
            return redirect(url_for('cursos.detalle', curso_id=curso_id))
        
        db.session.delete(curso)
        db.session.commit()
        
        flash('Curso eliminado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar curso: {str(e)}', 'danger')
    
    return redirect(url_for('cursos.index'))