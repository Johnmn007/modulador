import os
import json
from datetime import datetime
from flask import render_template
from app.models import Estudiante, SeguimientoRiesgo, Curso, Inscripcion, Nota, Asistencia
from app.extensions import db
from app.services.config_service import cargar_configuracion

class ReportGenerator:
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(__file__), '../static/reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generar_reporte_riesgo_individual(self, estudiante_id, semestre=None):
        """Genera reporte individual de riesgo para un estudiante"""
        estudiante = Estudiante.query.get_or_404(estudiante_id)
        
        if not semestre:
            config = cargar_configuracion()
            semestre = config.get('semestre_actual')
        
        # Obtener seguimiento de riesgo más reciente
        seguimiento = SeguimientoRiesgo.query.filter_by(
            estudiante_id=estudiante_id,
            semestre=semestre
        ).order_by(SeguimientoRiesgo.fecha_evaluacion.desc()).first()
        
        # Obtener cursos del semestre
        cursos = Curso.query.join(Inscripcion).filter(
            Inscripcion.estudiante_id == estudiante_id,
            Curso.semestre == semestre
        ).all()
        
        # Obtener notas y asistencias
        datos_cursos = []
        for curso in cursos:
            # Promedio de notas del curso
            promedio_query = db.session.query(db.func.avg(Nota.nota)).join(
                Inscripcion
            ).filter(
                Inscripcion.estudiante_id == estudiante_id,
                Inscripcion.curso_id == curso.id
            ).scalar()
            
            # Asistencia del curso
            asistencia_query = db.session.query(
                db.func.count(Asistencia.id),
                db.func.sum(db.cast(Asistencia.presente, db.Integer))
            ).join(Inscripcion).filter(
                Inscripcion.estudiante_id == estudiante_id,
                Inscripcion.curso_id == curso.id
            ).first()
            
            total_clases = asistencia_query[0] or 0
            asistencias = asistencia_query[1] or 0
            porcentaje_asistencia = (asistencias / total_clases * 100) if total_clases > 0 else 0
            
            datos_cursos.append({
                'curso': curso,
                'promedio': round(promedio_query, 2) if promedio_query else 'Sin notas',
                'asistencia': round(porcentaje_asistencia, 1),
                'total_clases': total_clases
            })
        
        # Renderizar template HTML
        html_content = render_template(
            'reportes/individual_riesgo.html',
            estudiante=estudiante,
            seguimiento=seguimiento,
            cursos=datos_cursos,
            semestre=semestre,
            fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        return {
            'html': html_content,
            'estudiante': estudiante,
            'seguimiento': seguimiento,
            'datos_cursos': datos_cursos
        }
    
    def generar_reporte_riesgo_general(self, semestre=None, categoria_filtro=None):
        """Genera reporte general de riesgo para todos los estudiantes"""
        if not semestre:
            config = cargar_configuracion()
            semestre = config.get('semestre_actual')
        
        # Obtener estudiantes en riesgo
        query = db.session.query(Estudiante, SeguimientoRiesgo).join(
            SeguimientoRiesgo, Estudiante.id == SeguimientoRiesgo.estudiante_id
        ).filter(
            SeguimientoRiesgo.semestre == semestre,
            Estudiante.activo == True
        )
        
        if categoria_filtro and categoria_filtro != 'TODOS':
            query = query.filter(SeguimientoRiesgo.categoria_riesgo == categoria_filtro)
        
        estudiantes_riesgo = query.order_by(
            SeguimientoRiesgo.puntaje_riesgo.desc()
        ).all()
        
        # Estadísticas
        total_estudiantes = Estudiante.query.filter_by(activo=True).count()
        total_riesgo = len(estudiantes_riesgo)
        
        # Conteo por categoría
        categorias_count = db.session.query(
            SeguimientoRiesgo.categoria_riesgo,
            db.func.count(SeguimientoRiesgo.id)
        ).filter(
            SeguimientoRiesgo.semestre == semestre
        ).group_by(SeguimientoRiesgo.categoria_riesgo).all()
        
        estadisticas = {
            'total_estudiantes': total_estudiantes,
            'total_riesgo': total_riesgo,
            'porcentaje_riesgo': (total_riesgo / total_estudiantes * 100) if total_estudiantes > 0 else 0,
            'categorias': dict(categorias_count)
        }
        
        html_content = render_template(
            'reportes/general_riesgo.html',
            estudiantes_riesgo=estudiantes_riesgo,
            estadisticas=estadisticas,
            semestre=semestre,
            categoria_filtro=categoria_filtro,
            fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        return {
            'html': html_content,
            'estadisticas': estadisticas,
            'estudiantes_riesgo': estudiantes_riesgo
        }

    def generar_reporte_asistencia_curso(self, curso_id):
        """Genera una matriz de asistencia para todo un curso (Agrupado por mes)"""
        curso = Curso.query.get_or_404(curso_id)
        
        # Estudiantes inscritos
        inscripciones = Inscripcion.query.filter_by(curso_id=curso_id, estado='ACTIVO').join(Estudiante).order_by(Estudiante.apellidos).all()
        
        # Todas las fechas de asistencia para este curso
        fechas = db.session.query(Asistencia.fecha).join(Inscripcion).filter(
            Inscripcion.curso_id == curso_id
        ).distinct().order_by(Asistencia.fecha).all()
        todas_fechas = [f[0] for f in fechas]
        
        nombres_meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        
        # Obtener meses únicos en orden
        unique_months = []
        for f in todas_fechas:
            mes_key = (f.year, f.month)
            if mes_key not in unique_months:
                unique_months.append(mes_key)
                
        # Agrupar meses en bloques de 2
        chunks = []
        for i in range(0, len(unique_months), 2):
            chunks.append(unique_months[i:i+2])
            
        # Pre-calcular el porcentaje global para cada estudiante
        global_stats = {}
        for ins in inscripciones:
            asist_est = Asistencia.query.filter(
                Asistencia.inscripcion_id == ins.id,
                Asistencia.fecha.in_(todas_fechas)
            ).all()
            
            total_pres = sum(1 for a in asist_est if a.presente or a.justificado)
            porcentaje = (total_pres / len(todas_fechas) * 100) if todas_fechas else 0
            
            # También guardamos el diccionario de asistencias para no volver a consultarlo por mes
            dict_asist = {a.fecha: a for a in asist_est}
            global_stats[ins.id] = {
                'porcentaje': porcentaje,
                'dict_asistencias': dict_asist
            }

        meses_data = []
        for chunk in chunks:
            fechas_chunk = [f for f in todas_fechas if (f.year, f.month) in chunk]
            
            nombres = [f"{nombres_meses[m]} {y}" for y, m in chunk]
            if len(nombres) > 1 and nombres[0].split()[-1] == nombres[1].split()[-1]:
                nombre_chunk = f"{nombres_meses[chunk[0][1]]} - {nombres_meses[chunk[1][1]]} {chunk[0][0]}"
            else:
                nombre_chunk = " - ".join(nombres)
                
            matriz_chunk = []
            
            for ins in inscripciones:
                dict_asistencias = global_stats[ins.id]['dict_asistencias']
                
                fila = {
                    'estudiante': ins.estudiante,
                    'asistencias': []
                }
                
                for fecha in fechas_chunk:
                    estado = dict_asistencias.get(fecha)
                    if estado:
                        if estado.presente: 
                            simbolo = 'P'
                        elif estado.justificado: 
                            simbolo = 'J'
                        else: 
                            simbolo = 'F'
                    else:
                        simbolo = '-'
                    fila['asistencias'].append(simbolo)
                
                fila['porcentaje'] = global_stats[ins.id]['porcentaje']
                matriz_chunk.append(fila)
                
            meses_data.append({
                'nombre': nombre_chunk,
                'fechas': fechas_chunk,
                'matriz': matriz_chunk
            })
            
        html_content = render_template(
            'reportes/asistencia_grupal_pdf.html',
            curso=curso,
            meses=meses_data,
            fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        return {
            'html': html_content,
            'curso': curso,
            'meses': meses_data
        }