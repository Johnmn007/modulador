# reportes/routes.py - VERSIÓN COMPLETAMENTE CORREGIDA
import os
import pdfkit
from datetime import datetime
import tempfile
import platform
from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from . import reportes_bp
from app.services.report_generator import ReportGenerator
from app.services.config_service import cargar_configuracion
from app.services.logger import app_logger
from app.models import Reporte, Estudiante, Curso
from app.extensions import db

def get_pdf_config():
    """Configuración portable para pdfkit en diferentes sistemas"""
    try:
        # Detectar sistema operativo
        if platform.system() == "Windows":
            # Rutas comunes en Windows
            possible_paths = [
                r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
                'wkhtmltopdf.exe'  # Si está en el PATH
            ]
        else:
            # Linux/Mac
            possible_paths = [
                '/usr/bin/wkhtmltopdf',
                '/usr/local/bin/wkhtmltopdf',
                'wkhtmltopdf'
            ]
        
        # Buscar wkhtmltopdf
        for path in possible_paths:
            if os.path.exists(path):
                return pdfkit.configuration(wkhtmltopdf=path)
        
        # Si no se encuentra, usar None (asume que está en PATH)
        return pdfkit.configuration()
        
    except Exception:
        return pdfkit.configuration()
    
    
@reportes_bp.route('/')
@login_required
def index():
    """Panel principal de reportes"""
    return render_template('reportes/index.html')


@reportes_bp.route('/individual')
@login_required
def individual():
    """Reporte individual de estudiantes"""
    estudiantes = Estudiante.query.filter_by(activo=True).order_by(Estudiante.apellidos).all()
    config = cargar_configuracion()
    return render_template('reportes/individual.html', estudiantes=estudiantes, config=config)

@reportes_bp.route('/general')
@login_required
def general():
    """Reporte general de riesgo"""
    config = cargar_configuracion()
    return render_template('reportes/general.html', config=config)

@reportes_bp.route('/generar-general', methods=['POST'])
@login_required
def generar_general():
    """Generar reporte general de riesgo"""
    try:
        semestre = request.form.get('semestre')
        categoria = request.form.get('categoria', 'TODOS')
        formato = request.form.get('formato', 'html')
        
        generator = ReportGenerator()
        resultado = generator.generar_reporte_riesgo_general(semestre, categoria)
        
        reporte = Reporte(
            tipo_reporte='GENERAL_RIESGO',
            titulo=f'Reporte General de Riesgo - {semestre}',
            descripcion=f'Resumen de riesgo para la categoría {categoria}',
            parametros={'semestre': semestre, 'categoria': categoria, 'formato': formato},
            contenido=resultado['html'],
            usuario_id=current_user.id
        )
        db.session.add(reporte)
        db.session.commit()
        
        if formato == 'pdf':
            try:
                config = get_pdf_config()
                options = {'page-size': 'A4', 'encoding': "UTF-8"}
                pdf = pdfkit.from_string(resultado['html'], False, configuration=config, options=options)
                filename = f"reporte_general_{datetime.now().strftime('%Y%m%d')}.pdf"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp.write(pdf)
                temp.close()
                response = send_file(temp.name, as_attachment=True, download_name=filename)
                return response
            except Exception as e:
                flash(f'Error al generar PDF: {str(e)}', 'warning')
                return resultado['html']
        
        return render_template('reportes/vista_previa.html', 
                             contenido=resultado['html'],
                             titulo=reporte.titulo,
                             reporte_id=reporte.id,
                             datetime=datetime)
    except Exception as e:
        db.session.rollback()
        flash(f'Error generando reporte: {str(e)}', 'danger')
        return redirect(url_for('reportes.general'))

@reportes_bp.route('/generar-individual', methods=['POST'])
@login_required
def generar_individual():
    """Generar reporte individual"""
    try:
        estudiante_id = request.form.get('estudiante_id')
        semestre = request.form.get('semestre')
        formato = request.form.get('formato', 'html')
        
        generator = ReportGenerator()
        resultado = generator.generar_reporte_riesgo_individual(estudiante_id, semestre)
        
        # Guardar en base de datos
        reporte = Reporte(
            tipo_reporte='INDIVIDUAL_RIESGO',
            titulo=f'Reporte de Riesgo - {resultado["estudiante"].nombres} {resultado["estudiante"].apellidos}',
            descripcion=f'Reporte individual de riesgo académico para el semestre {semestre}',
            parametros={
                'estudiante_id': estudiante_id,
                'semestre': semestre,
                'formato': formato
            },
            contenido=resultado['html'],
            usuario_id=current_user.id
        )
        db.session.add(reporte)
        db.session.commit()
        
        if formato == 'pdf':
            try:
                config = get_pdf_config()
                options = {
                    'page-size': 'A4',
                    'margin-top': '.5in',
                    'margin-right': '1.0in',
                    'margin-bottom': '1.0in',
                    'margin-left': '1.0in',
                    'encoding': "UTF-8"
                }
                pdf = pdfkit.from_string(resultado['html'], False, configuration=config, options=options)
                filename = f"reporte_riesgo_{estudiante_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp.write(pdf)
                temp.close()
                response = send_file(temp.name, as_attachment=True, download_name=filename)
                return response
            except Exception as e:
                flash(f'Error al generar PDF: {str(e)}', 'warning')
                return resultado['html']
        
        return render_template('reportes/vista_previa.html', 
                             contenido=resultado['html'],
                             titulo=reporte.titulo,
                             reporte_id=reporte.id,
                             datetime=datetime)
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error generando reporte: {str(e)}', 'danger')
        return redirect(url_for('reportes.individual'))

@reportes_bp.route('/asistencias')
@login_required
def asistencias_index():
    """Pantalla inicial de reportes de asistencia"""
    cursos = Curso.query.filter_by(activo=True).order_by(Curso.semestre, Curso.nombre_curso).all()
    estudiantes = Estudiante.query.filter_by(activo=True).order_by(Estudiante.apellidos).all()
    config = cargar_configuracion()
    return render_template('reportes/asistencias_filter.html', cursos=cursos, estudiantes=estudiantes, config=config)

@reportes_bp.route('/asistencias/grupal', methods=['POST'])
@login_required
def generar_asistencia_grupal():
    """Genera reporte de asistencia grupal (matriz)"""
    try:
        curso_id = request.form.get('curso_id', type=int)
        formato = request.form.get('formato', 'html')
        
        generator = ReportGenerator()
        resultado = generator.generar_reporte_asistencia_curso(curso_id)
        
        reporte = Reporte(
            tipo_reporte='GRUPAL_ASISTENCIA',
            titulo=f'Reporte Asistencia - {resultado["curso"].nombre_curso}',
            descripcion=f'Matriz de asistencia completa del curso',
            parametros={'curso_id': curso_id, 'formato': formato},
            contenido=resultado['html'],
            usuario_id=current_user.id
        )
        db.session.add(reporte)
        db.session.commit()
        
        if formato == 'pdf':
            try:
                config = get_pdf_config()
                options = {
                    'page-size': 'A4',
                    'orientation': 'Landscape',
                    'margin-top': '.5in',
                    'margin-right': '.5in',
                    'margin-bottom': '.5in',
                    'margin-left': '.5in',
                    'encoding': "UTF-8"
                }
                pdf = pdfkit.from_string(resultado['html'], False, configuration=config, options=options)
                filename = f"asistencia_{resultado['curso'].codigo_curso}_{datetime.now().strftime('%Y%m%d')}.pdf"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp.write(pdf)
                temp.close()
                response = send_file(temp.name, as_attachment=True, download_name=filename)
                return response
            except Exception as e:
                flash(f'Error al generar PDF: {str(e)}', 'warning')
                return resultado['html']
        
        return render_template('reportes/vista_previa.html', 
                             contenido=resultado['html'],
                             titulo=reporte.titulo,
                             reporte_id=reporte.id,
                             datetime=datetime)
    except Exception as e:
        db.session.rollback()
        flash(f'Error al generar reporte: {str(e)}', 'danger')
        return redirect(url_for('reportes.asistencias_index'))

@reportes_bp.route('/historial')
@login_required
def historial():
    """Historial de reportes generados"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    reportes = Reporte.query.filter_by(usuario_id=current_user.id).order_by(
        Reporte.fecha_generacion.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('reportes/historial.html', reportes=reportes)

@reportes_bp.route('/descargar/<int:reporte_id>')
@login_required
def descargar(reporte_id):
    """Descargar reporte generado anteriormente"""
    reporte = Reporte.query.get_or_404(reporte_id)
    if reporte.usuario_id != current_user.id and current_user.rol != 'administrador':
        app_logger.warning(f"Acceso denegado a reporte {reporte_id} por usuario {current_user.id} (rol: {current_user.rol})")
        flash('No tiene permisos para acceder a este reporte', 'danger')
        return redirect(url_for('reportes.historial'))
    
    # Si el reporte es HTML guardado en DB, podemos intentar reconvertirlo a PDF si se pide
    # Por ahora solo manejamos archivos físicos si existen
    if reporte.archivo_path and os.path.exists(reporte.archivo_path):
        filename = f"reporte_{reporte.tipo_reporte}_{reporte.id}.pdf"
        return send_file(reporte.archivo_path, as_attachment=True, download_name=filename)
    else:
        # Si no hay archivo físico, mostramos la versión HTML guardada
        return render_template('reportes/vista_previa.html', 
                             contenido=reporte.contenido,
                             titulo=reporte.titulo,
                             reporte_id=reporte.id,
                             datetime=datetime)