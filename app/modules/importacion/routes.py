# app/modules/importacion/routes.py
import re
from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from app.decorators import roles_required
import pandas as pd
import io
from datetime import datetime, timezone
from . import importacion_bp
from app.models import Estudiante, Curso, Inscripcion, Evaluacion, Nota, SeguimientoRiesgo, Ciclo
from app.extensions import db
from app.services.seguimiento_service import SeguimientoService
from app.services.config_service import cargar_configuracion

@importacion_bp.route('/')
@login_required
@roles_required('administrador', 'coordinador')
def index():
    """Panel de importación de datos"""
    return render_template('importacion/index.html')

@importacion_bp.route('/importar-estudiantes', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def importar_estudiantes():
    """Importar estudiantes desde archivo Excel/CSV con mejor manejo de errores"""
    try:
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('importacion.index'))
        
        archivo = request.files['archivo']
        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('importacion.index'))
        
        # Validar extensión
        if not (archivo.filename.endswith('.csv') or archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls')):
            flash('Formato de archivo no soportado. Use .csv, .xlsx o .xls', 'danger')
            return redirect(url_for('importacion.index'))
        
        # Leer archivo
        try:
            if archivo.filename.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
        except Exception as e:
            flash(f'Error al leer el archivo: {str(e)}. Verifique que el formato sea correcto.', 'danger')
            return redirect(url_for('importacion.index'))
        
        # Validar columnas requeridas
        columnas_requeridas = ['codigo_estudiante', 'nombres', 'apellidos', 'email']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            flash(f'Columnas requeridas faltantes: {", ".join(columnas_faltantes)}', 'danger')
            return redirect(url_for('importacion.index'))
        
        # Validar que el archivo no esté vacío
        if df.empty:
            flash('El archivo está vacío', 'danger')
            return redirect(url_for('importacion.index'))
        
        estudiantes_importados = 0
        estudiantes_actualizados = 0
        errores = []
        fila = 2  # Para mensajes de error (fila 1 es encabezado)
        
        for index, fila_df in df.iterrows():
            fila_actual = fila + index
            try:
                # Validar datos requeridos
                codigo = _sanitize(str(fila_df['codigo_estudiante']).strip() if not pd.isna(fila_df['codigo_estudiante']) else '')
                nombres = _sanitize(str(fila_df['nombres']).strip() if not pd.isna(fila_df['nombres']) else '')
                apellidos = _sanitize(str(fila_df['apellidos']).strip() if not pd.isna(fila_df['apellidos']) else '')
                email = _sanitize(str(fila_df['email']).strip() if not pd.isna(fila_df['email']) else '')
                
                if not codigo or not nombres or not apellidos or not email:
                    errores.append(f"Fila {fila_actual}: Datos requeridos incompletos")
                    continue
                
                # Validar formato de email
                if '@' not in email or '.' not in email:
                    errores.append(f"Fila {fila_actual}: Email inválido '{email}'")
                    continue
                
                # Buscar si el estudiante ya existe
                estudiante = Estudiante.query.filter_by(
                    codigo_estudiante=codigo
                ).first()
                
                if estudiante:
                    # Actualizar estudiante existente
                    estudiante.nombres = nombres
                    estudiante.apellidos = apellidos
                    estudiante.email = email
                    telefono = str(fila_df.get('telefono', '')).strip() if not pd.isna(fila_df.get('telefono', '')) else ''
                    estudiante.telefono = telefono
                    estudiantes_actualizados += 1
                else:
                    # Crear nuevo estudiante
                    telefono = str(fila_df.get('telefono', '')).strip() if not pd.isna(fila_df.get('telefono', '')) else ''
                    estudiante = Estudiante(
                        codigo_estudiante=codigo,
                        nombres=nombres,
                        apellidos=apellidos,
                        email=email,
                        telefono=telefono,
                        activo=True
                    )
                    db.session.add(estudiante)
                    estudiantes_importados += 1
                
            except Exception as e:
                errores.append(f"Fila {fila_actual}: Error inesperado - {str(e)}")
                continue
        
        # Guardar cambios
        if estudiantes_importados > 0 or estudiantes_actualizados > 0:
            try:
                db.session.commit()
                mensaje = f'✅ Importación completada: {estudiantes_importados} nuevos, {estudiantes_actualizados} actualizados.'
                if errores:
                    mensaje += f' Se omitieron {len(errores)} filas con errores.'
                    flash(mensaje, 'warning')
                    for error in errores[:5]:  # Mostrar solo primeros 5 errores
                        flash(f'  • {error}', 'warning')
                    if len(errores) > 5:
                        flash(f'  ... y {len(errores)-5} errores más', 'warning')
                else:
                    flash(mensaje, 'success')
                
                # RECALCULO AUTOMÁTICO - NUEVO
                SeguimientoService.recalcular_riesgo_semestre()
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Error al guardar en base de datos: {str(e)}', 'danger')
        else:
            if errores:
                flash('❌ No se pudo importar ningún registro. Errores encontrados:', 'danger')
                for error in errores[:5]:
                    flash(f'  • {error}', 'danger')
            else:
                flash('⚠️ No se encontraron datos para importar', 'warning')
        
        return redirect(url_for('importacion.resultados'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error general en importación: {str(e)}', 'danger')
        return redirect(url_for('importacion.index'))

@importacion_bp.route('/importar-cursos', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def importar_cursos():
    """Importar cursos desde archivo Excel/CSV"""
    try:
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('importacion.index'))
        
        archivo = request.files['archivo']
        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('importacion.index'))
        
        # Leer archivo
        if archivo.filename.endswith('.csv'):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)
        
        # Validar columnas requeridas
        columnas_requeridas = ['codigo_curso', 'nombre_curso', 'semestre']
        for columna in columnas_requeridas:
            if columna not in df.columns:
                flash(f'Columna requerida faltante: {columna}', 'danger')
                return redirect(url_for('importacion.index'))
        
        cursos_importados = 0
        cursos_actualizados = 0
        
        config = cargar_configuracion()
        periodo_actual = config.get('semestre_actual', '2024-1')
        
        # Buscar o crear el ciclo del periodo actual
        ciclo = Ciclo.query.filter_by(codigo_ciclo=periodo_actual).first()
        if not ciclo:
            ciclo = Ciclo(
                nombre=f"Ciclo {periodo_actual}",
                codigo_ciclo=periodo_actual,
                fecha_inicio=datetime.now(timezone.utc).date(),
                fecha_fin=datetime.now(timezone.utc).date(),
                activo=True
            )
            db.session.add(ciclo)
            db.session.flush()

        for _, fila in df.iterrows():
            semestre_val = str(fila['semestre']).strip()
            
            # Buscar si el curso ya existe en este ciclo específico
            curso = Curso.query.filter_by(
                codigo_curso=fila['codigo_curso'],
                ciclo_id=ciclo.id
            ).first()
            
            if curso:
                # Actualizar curso existente
                curso.nombre_curso = fila['nombre_curso']
                curso.creditos = fila.get('creditos', 3)
                curso.ciclo_id = ciclo.id
                cursos_actualizados += 1
            else:
                # Crear nuevo curso
                curso = Curso(
                    codigo_curso=fila['codigo_curso'],
                    nombre_curso=fila['nombre_curso'],
                    creditos=fila.get('creditos', 3),
                    semestre=semestre_val,
                    ciclo_id=ciclo.id,
                    activo=True
                )
                db.session.add(curso)
                cursos_importados += 1
        
        db.session.commit()
        
        flash(f'✅ Cursos importados: {cursos_importados} nuevos, {cursos_actualizados} actualizados', 'success')
        
        # RECALCULO AUTOMÁTICO - NUEVO
        SeguimientoService.recalcular_riesgo_semestre()
        return redirect(url_for('importacion.resultados'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error en importación: {str(e)}', 'danger')
        return redirect(url_for('importacion.index'))

@importacion_bp.route('/importar-notas', methods=['POST'])
@login_required
@roles_required('administrador', 'coordinador')
def importar_notas():
    """Importar notas desde archivo Excel/CSV"""
    try:
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('importacion.index'))
        
        archivo = request.files['archivo']
        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('importacion.index'))
        
        # Leer archivo
        if archivo.filename.endswith('.csv'):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)
        
        # Validar columnas requeridas
        columnas_requeridas = ['codigo_estudiante', 'codigo_curso', 'nombre_evaluacion', 'nota']
        for columna in columnas_requeridas:
            if columna not in df.columns:
                flash(f'Columna requerida faltante: {columna}', 'danger')
                return redirect(url_for('importacion.index'))
        
        config = cargar_configuracion()
        semestre_actual = config.get('semestre_actual', '2024-1')
        
        ciclo = Ciclo.query.filter_by(codigo_ciclo=semestre_actual).first()
        if not ciclo:
            flash(f'Error: El ciclo actual ({semestre_actual}) no existe. Configure el ciclo o importe los cursos primero.', 'danger')
            return redirect(url_for('importacion.index'))

        notas_importadas = 0
        
        for _, fila in df.iterrows():
            estudiante = Estudiante.query.filter_by(
                codigo_estudiante=fila['codigo_estudiante']
            ).first()
            
            curso = Curso.query.filter_by(
                codigo_curso=fila['codigo_curso'],
                ciclo_id=ciclo.id
            ).first()
            
            if not estudiante or not curso:
                continue  # Saltar si no encuentra estudiante o curso
            
            # Buscar o crear inscripción
            inscripcion = Inscripcion.query.filter_by(
                estudiante_id=estudiante.id,
                curso_id=curso.id
            ).first()
            
            if not inscripcion:
                inscripcion = Inscripcion(
                    estudiante_id=estudiante.id,
                    curso_id=curso.id,
                    estado='ACTIVO'
                )
                db.session.add(inscripcion)
                db.session.flush()  # Para obtener el ID
            
            # Buscar o crear evaluación
            evaluacion = Evaluacion.query.filter_by(
                curso_id=curso.id,
                nombre_evaluacion=fila['nombre_evaluacion']
            ).first()
            
            if not evaluacion:
                evaluacion = Evaluacion(
                    curso_id=curso.id,
                    nombre_evaluacion=fila['nombre_evaluacion'],
                    tipo_evaluacion='PARCIAL',
                    peso=100.0
                )
                db.session.add(evaluacion)
                db.session.flush()
            
            # Buscar o crear nota
            nota = Nota.query.filter_by(
                inscripcion_id=inscripcion.id,
                evaluacion_id=evaluacion.id
            ).first()
            
            if nota:
                # Actualizar nota existente
                nota.nota = float(fila['nota'])
            else:
                # Crear nueva nota
                nota = Nota(
                    inscripcion_id=inscripcion.id,
                    evaluacion_id=evaluacion.id,
                    nota=float(fila['nota']),
                    fecha_registro=pd.to_datetime(fila.get('fecha', datetime.now(timezone.utc)))
                )
                db.session.add(nota)
            
            notas_importadas += 1
        
        db.session.commit()
        
        flash(f'✅ Notas importadas: {notas_importadas} registros procesados', 'success')
        
        # RECALCULO AUTOMÁTICO - NUEVO
        SeguimientoService.recalcular_riesgo_semestre()
        return redirect(url_for('importacion.resultados'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error en importación: {str(e)}', 'danger')
        return redirect(url_for('importacion.index'))

@importacion_bp.route('/resultados')
@login_required
@roles_required('administrador', 'coordinador')
def resultados():
    """Mostrar resultados de importaciones"""
    # Obtener estadísticas actuales
    estadisticas = {
        'estudiantes': Estudiante.query.filter_by(activo=True).count(),
        'cursos': Curso.query.filter_by(activo=True).count(),
        'notas': Nota.query.count(),
        'riesgo': SeguimientoRiesgo.query.filter(
            SeguimientoRiesgo.categoria_riesgo != 'SIN_RIESGO'
        ).count()
    }
    
    return render_template('importacion/resultados.html', estadisticas=estadisticas)

def _sanitize(value):
    value = re.sub(r'[<>\'";]', '', value)
    return value

@importacion_bp.route('/descargar-plantilla/<tipo>')
@login_required
@roles_required('administrador', 'coordinador')
def descargar_plantilla(tipo):
    """Descargar plantillas para importación"""
    if tipo == 'estudiantes':
        # Crear DataFrame de ejemplo para estudiantes
        df = pd.DataFrame({
            'codigo_estudiante': ['2024EST001', '2024EST002'],
            'nombres': ['Juan Carlos', 'María Elena'],
            'apellidos': ['García López', 'Rodríguez Martínez'],
            'email': ['juan.garcia@ejemplo.com', 'maria.rodriguez@ejemplo.com'],
            'telefono': ['123456789', '987654321']
        })
    elif tipo == 'cursos':
        df = pd.DataFrame({
            'codigo_curso': ['MAT101', 'PROG102'],
            'nombre_curso': ['Matemáticas Básicas', 'Programación Python'],
            'creditos': [4, 3],
            'semestre': ['I', 'II']
        })
    elif tipo == 'notas':
        df = pd.DataFrame({
            'codigo_estudiante': ['2024EST001', '2024EST001'],
            'codigo_curso': ['MAT101', 'MAT101'],
            'nombre_evaluacion': ['Parcial 1', 'Parcial 2'],
            'nota': [15.5, 14.0],
            'fecha': ['2024-03-15', '2024-04-20']
        })
    else:
        flash('Tipo de plantilla no válido', 'danger')
        return redirect(url_for('importacion.index'))
    
    # Crear archivo en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Plantilla', index=False)
    output.seek(0)
    
    return send_file(
        output,
        download_name=f'plantilla_{tipo}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )