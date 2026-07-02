from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import seguimiento_bp
from app.extensions import db
from app.models import SeguimientoRiesgo, Estudiante
from app.services.seguimiento_service import SeguimientoService
from app.services.config_service import cargar_configuracion
from app.services.riesgo_calculator_v2 import CalculatorRiesgoIntrasemestral

@seguimiento_bp.route('/')
@login_required
def index():
    """Panel de control del módulo de seguimiento"""
    return render_template('seguimiento/index.html')

@seguimiento_bp.route('/calcular-riesgo', methods=['POST'])
@login_required
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
    # Estadísticas de riesgo
    stats_query = db.session.query(
        SeguimientoRiesgo.categoria_riesgo,
        db.func.count(SeguimientoRiesgo.id)
    ).group_by(SeguimientoRiesgo.categoria_riesgo).all()
    
    estadisticas = {categoria: cantidad for categoria, cantidad in stats_query}
    
    # Últimos cálculos
    ultimos_seguimientos = SeguimientoRiesgo.query.order_by(
        SeguimientoRiesgo.fecha_evaluacion.desc()
    ).limit(10).all()
    
    return render_template('seguimiento/resultados.html',
                         estadisticas=estadisticas,
                         ultimos_seguimientos=ultimos_seguimientos)

@seguimiento_bp.route('/api/calcular-estudiante/<int:estudiante_id>')
@login_required
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
                'nombre': f"{estudiante.nombres} {estudiante.apellidos}"
            },
            'resultado': resultado
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500