from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import seguimiento_bp
from app.extensions import db
from app.models import SeguimientoRiesgo, Estudiante, Ciclo
from app.services.seguimiento_service import SeguimientoService
from app.services.config_service import cargar_configuracion, get_ciclo_activo
from app.services.riesgo_calculator_v2 import CalculatorRiesgoIntrasemestral
from app.decorators import roles_required

@seguimiento_bp.route('/')
@login_required
def index():
    """Panel de control del módulo de seguimiento"""
    ciclos = Ciclo.query.order_by(Ciclo.fecha_inicio.desc()).all()
    ciclo_activo = get_ciclo_activo()
    return render_template('seguimiento/index.html', ciclos=ciclos, ciclo_activo=ciclo_activo)

@seguimiento_bp.route('/calcular-riesgo', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def calcular_riesgo():
    """Ejecutar cálculo de riesgo para todos los estudiantes"""
    # OBTENER SEMESTRE DE CONFIGURACIÓN
    config = cargar_configuracion()
    semestre_defecto = config.get('semestre_actual', '2025-1')
    semestre = request.form.get('semestre', semestre_defecto)
    
    success, message = SeguimientoService.recalcular_riesgo_semestre(semestre)
    
    if success:
        flash(f'✅ Cálculo de riesgo completado! {message}', 'success')
        return redirect(url_for('seguimiento.resultados'))
    else:
        flash(f'❌ Error ejecutando cálculo: {message}', 'danger')
        return redirect(url_for('seguimiento.index'))

@seguimiento_bp.route('/resultados')
@login_required
def resultados():
    """Mostrar resultados del cálculo de riesgo"""
    config = cargar_configuracion()
    ciclo = get_ciclo_activo()
    semestre_actual = ciclo.codigo_ciclo if ciclo else config.get('semestre_actual', '2025-1')

    # Estadísticas de riesgo del semestre actual
    stats_query = db.session.query(
        SeguimientoRiesgo.categoria_riesgo,
        db.func.count(SeguimientoRiesgo.id)
    ).filter(SeguimientoRiesgo.semestre == semestre_actual).group_by(SeguimientoRiesgo.categoria_riesgo).all()
    
    estadisticas = {categoria: cantidad for categoria, cantidad in stats_query}
    
    # Todos los seguimientos del semestre actual ordenados por mayor riesgo
    query = SeguimientoRiesgo.query.filter_by(semestre=semestre_actual)
    
    categoria_filter = request.args.get('categoria')
    ciclo_filter = request.args.get('ciclo')
    
    if categoria_filter:
        query = query.filter_by(categoria_riesgo=categoria_filter.replace(' ', '_'))
        
    ultimos_seguimientos = query.order_by(SeguimientoRiesgo.puntaje_riesgo.desc()).all()
    
    # Calcular el ciclo predominante para cada estudiante
    seguimientos_filtrados = []
    for seguimiento in ultimos_seguimientos:
        # Buscar el ciclo curricular más repetido entre los cursos en los que el estudiante está inscrito
        ciclo_query = db.session.execute(db.text("""
            SELECT c.semestre, COUNT(c.id) as cantidad
            FROM inscripciones i
            JOIN cursos c ON i.curso_id = c.id
            JOIN ciclos ci ON c.ciclo_id = ci.id
            WHERE i.estudiante_id = :estudiante_id AND ci.codigo_ciclo = :semestre_actual
            GROUP BY c.semestre
            ORDER BY cantidad DESC
            LIMIT 1
        """), {'estudiante_id': seguimiento.estudiante_id, 'semestre_actual': semestre_actual}).fetchone()
        
        seguimiento.ciclo_predominante = ciclo_query[0] if ciclo_query else "N/A"
        
        # Si hay filtro de ciclo, solo conservamos los que coincidan
        if ciclo_filter and ciclo_filter != "":
            if seguimiento.ciclo_predominante == ciclo_filter:
                seguimientos_filtrados.append(seguimiento)
        else:
            seguimientos_filtrados.append(seguimiento)
            
    ultimos_seguimientos = seguimientos_filtrados
    
    return render_template('seguimiento/resultados.html',
                         estadisticas=estadisticas,
                         ultimos_seguimientos=ultimos_seguimientos,
                         semestre_actual=semestre_actual,
                         categoria_filter=categoria_filter,
                         ciclo_filter=ciclo_filter)

@seguimiento_bp.route('/api/calcular-estudiante/<int:estudiante_id>')
@login_required
@roles_required('administrador', 'coordinador')
def calcular_estudiante(estudiante_id):
    """API para calcular riesgo de un estudiante específico"""
    try:
        # OBTENER SEMESTRE DE CONFIGURACIÓN
        config = cargar_configuracion()
        semestre_defecto = config.get('semestre_actual', '2025-1')
        semestre = request.args.get('semestre', semestre_defecto)
        estudiante = Estudiante.query.get_or_404(estudiante_id)
        
        calculador = CalculatorRiesgoIntrasemestral(config)
        
        resultado = calculador.calcular_riesgo_estudiante(estudiante_id, semestre, db)
        
        return jsonify({
            'estudiante': {
                'id': estudiante.id,
                'codigo': estudiante.codigo_estudiante,
                'nombre': f"{estudiante.apellidos} {estudiante.nombres}"
            },
            'resultado': resultado
        })
        
    except Exception as e:
        return jsonify({'error': 'Error al calcular el riesgo del estudiante'}), 500