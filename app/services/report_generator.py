import os
import json
from datetime import datetime
from flask import render_template
from app.models import Estudiante, SeguimientoRiesgo, Curso, Inscripcion, Nota, Asistencia, Evaluacion
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
            from app.services.config_service import get_ciclo_activo
            ciclo = get_ciclo_activo()
            semestre = ciclo.codigo_ciclo if ciclo else None
        
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
            
            # Asistencia del curso con métricas académicas (16 semanas y límite 30% DPI)
            asistencia_query = db.session.query(
                db.func.count(Asistencia.id),
                db.func.sum(db.case(((Asistencia.presente == True) & (Asistencia.es_institucional != True), 1), else_=0)),
                db.func.sum(db.case(((Asistencia.justificado == True) & (Asistencia.es_institucional != True), 1), else_=0)),
                db.func.sum(db.case(((Asistencia.presente == False) & (Asistencia.justificado == False) & (Asistencia.es_institucional != True), 1), else_=0)),
                db.func.sum(db.case((Asistencia.es_institucional == True, 1), else_=0))
            ).join(Inscripcion).filter(
                Inscripcion.estudiante_id == estudiante_id,
                Inscripcion.curso_id == curso.id
            ).first()
            
            total_clases = asistencia_query[0] or 0
            presentes = asistencia_query[1] or 0
            justificadas = asistencia_query[2] or 0
            inasistencias = asistencia_query[3] or 0
            institucionales = asistencia_query[4] or 0
            
            total_clases_efectivas = max(total_clases - institucionales, 0)
            total_programadas = curso.total_sesiones_efectivas_programadas
            max_faltas = curso.max_faltas_permitidas
            faltas_restantes = max_faltas - inasistencias
            
            porcentaje_asistencia = ((presentes + justificadas) / total_clases_efectivas * 100) if total_clases_efectivas > 0 else 100.0
            porcentaje_inasistencia_sem = (inasistencias / total_programadas * 100) if total_programadas > 0 else 0.0
            
            if faltas_restantes < 0:
                estado_asist = 'DPI'
            elif faltas_restantes <= 1:
                estado_asist = 'ALERTA_CRITICA'
            elif faltas_restantes <= 3 and inasistencias > 0:
                estado_asist = 'PREVENTIVO'
            else:
                estado_asist = 'NORMAL'
            
            datos_cursos.append({
                'curso': curso,
                'promedio': round(promedio_query, 2) if promedio_query else 'Sin notas',
                'asistencia': round(porcentaje_asistencia, 1),
                'total_clases': total_clases,
                'total_clases_efectivas': total_clases_efectivas,
                'institucionales': institucionales,
                'inasistencias': inasistencias,
                'total_programadas': total_programadas,
                'max_faltas': max_faltas,
                'faltas_restantes': faltas_restantes,
                'porcentaje_inasistencia_sem': round(porcentaje_inasistencia_sem, 1),
                'estado_asistencia': estado_asist
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
            from app.services.config_service import get_ciclo_activo
            ciclo = get_ciclo_activo()
            semestre = ciclo.codigo_ciclo if ciclo else None
        
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
        inscripciones = Inscripcion.query.filter_by(curso_id=curso_id, estado='ACTIVO').join(Estudiante).order_by(Estudiante.apellidos, Estudiante.nombres).all()
        
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
            
            clases_efectivas = [a for a in asist_est if not getattr(a, 'es_institucional', False)]
            total_pres = sum(1 for a in clases_efectivas if a.presente or a.justificado)
            porcentaje = (total_pres / len(clases_efectivas) * 100) if clases_efectivas else 100.0
            
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
                        if getattr(estado, 'es_institucional', False):
                            simbolo = 'S'
                        elif estado.presente: 
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

    def generar_reporte_notas_curso(self, curso_id):
        """Genera acta oficial consolidada de calificaciones para un curso"""
        curso = Curso.query.get_or_404(curso_id)
        config = cargar_configuracion()
        nota_minima = float(config.get('nota_minima_aprobatoria', 12.5))
        
        # Evaluaciones del curso ordenadas por fecha/creación
        evaluaciones = Evaluacion.query.filter_by(curso_id=curso_id).order_by(
            Evaluacion.fecha_creacion.asc(),
            Evaluacion.id.asc()
        ).all()
        
        # Estudiantes inscritos activos
        inscripciones = Inscripcion.query.filter_by(curso_id=curso_id, estado='ACTIVO').join(
            Estudiante
        ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
        
        # Mapeo de notas {inscripcion_id: {evaluacion_id: nota_float}}
        notas_raw = Nota.query.join(Inscripcion).filter(
            Inscripcion.curso_id == curso_id
        ).all()
        
        notas_dict = {}
        for n in notas_raw:
            if n.inscripcion_id not in notas_dict:
                notas_dict[n.inscripcion_id] = {}
            notas_dict[n.inscripcion_id][n.evaluacion_id] = float(n.nota) if n.nota is not None else None
            
        # Conteo de inasistencias por inscripción para verificar condición DPI (>30% inasistencias)
        asistencias_raw = db.session.query(
            Inscripcion.id,
            db.func.sum(db.case(((Asistencia.presente == False) & (Asistencia.justificado == False) & (Asistencia.es_institucional != True), 1), else_=0))
        ).join(Asistencia, Asistencia.inscripcion_id == Inscripcion.id).filter(
            Inscripcion.curso_id == curso_id
        ).group_by(Inscripcion.id).all()
        
        inasistencias_dict = {a[0]: (a[1] or 0) for a in asistencias_raw}
        max_faltas = curso.max_faltas_permitidas
        
        consolidado = []
        promedios_validos = []
        aprobados_count = 0
        desaprobados_count = 0
        dpi_count = 0
        
        for idx, ins in enumerate(inscripciones, 1):
            notas_alumno = notas_dict.get(ins.id, {})
            notas_list = []
            suma_ponderada = 0.0
            
            for ev in evaluaciones:
                val = notas_alumno.get(ev.id)
                notas_list.append(val)
                if val is not None:
                    peso_frac = float(ev.peso) / 100.0 if ev.peso else 0.0
                    suma_ponderada += val * peso_frac
            
            # Promedio ponderado final
            promedio_final = round(suma_ponderada, 1) if evaluaciones else 0.0
            
            faltas = inasistencias_dict.get(ins.id, 0)
            es_dpi = (faltas > max_faltas) if (max_faltas is not None and curso.total_sesiones_programadas > 0) else False
            
            if es_dpi:
                condicion = 'DPI'
                dpi_count += 1
                desaprobados_count += 1
            elif promedio_final >= nota_minima:
                condicion = 'APROBADO'
                aprobados_count += 1
            else:
                condicion = 'DESAPROBADO'
                desaprobados_count += 1
                
            promedios_validos.append(promedio_final)
            
            consolidado.append({
                'num': idx,
                'estudiante': ins.estudiante,
                'codigo': ins.estudiante.codigo_estudiante,
                'nombre_completo': f"{ins.estudiante.apellidos}, {ins.estudiante.nombres}",
                'notas': notas_list,
                'promedio': promedio_final,
                'faltas': faltas,
                'max_faltas': max_faltas,
                'condicion': condicion
            })
            
        total_estudiantes = len(inscripciones)
        promedio_aula = round(sum(promedios_validos) / total_estudiantes, 2) if total_estudiantes > 0 else 0.0
        nota_maxima = max(promedios_validos) if promedios_validos else 0.0
        nota_minima_aula = min(promedios_validos) if promedios_validos else 0.0
        porcentaje_aprobados = round((aprobados_count / total_estudiantes * 100), 1) if total_estudiantes > 0 else 0.0
        porcentaje_desaprobados = round((desaprobados_count / total_estudiantes * 100), 1) if total_estudiantes > 0 else 0.0
        
        estadisticas = {
            'total_estudiantes': total_estudiantes,
            'aprobados': aprobados_count,
            'desaprobados': desaprobados_count,
            'dpi': dpi_count,
            'porcentaje_aprobados': porcentaje_aprobados,
            'porcentaje_desaprobados': porcentaje_desaprobados,
            'promedio_aula': promedio_aula,
            'nota_maxima': nota_maxima,
            'nota_minima': nota_minima_aula,
            'nota_minima_aprobatoria': nota_minima
        }
        
        html_content = render_template(
            'reportes/notas_curso_pdf.html',
            curso=curso,
            evaluaciones=evaluaciones,
            consolidado=consolidado,
            estadisticas=estadisticas,
            config=config,
            fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        return {
            'html': html_content,
            'curso': curso,
            'evaluaciones': evaluaciones,
            'consolidado': consolidado,
            'estadisticas': estadisticas
        }

    def generar_reporte_boleta_estudiante(self, estudiante_id, semestre=None):
        """Genera boleta oficial de calificaciones de un estudiante para un semestre"""
        estudiante = Estudiante.query.get_or_404(estudiante_id)
        config = cargar_configuracion()
        nota_minima = float(config.get('nota_minima_aprobatoria', 12.5))
        
        from app.services.config_service import get_ciclo_activo
        from app.models import Ciclo
        
        if not semestre:
            ciclo = get_ciclo_activo()
            semestre = ciclo.codigo_ciclo if ciclo else None
        else:
            ciclo = Ciclo.query.filter_by(codigo_ciclo=semestre).first()
            if not ciclo:
                ciclo = get_ciclo_activo()
                
        # Inscripciones del estudiante en este ciclo / semestre
        inscripciones_query = Inscripcion.query.join(Curso).filter(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.estado == 'ACTIVO'
        )
        if ciclo:
            inscripciones_query = inscripciones_query.filter(Curso.ciclo_id == ciclo.id)
        elif semestre:
            inscripciones_query = inscripciones_query.filter(Curso.semestre == semestre)
            
        inscripciones = inscripciones_query.order_by(Curso.nombre_curso).all()
        
        boleta_cursos = []
        suma_creditos = 0
        suma_puntos_ponderados = 0.0
        cursos_aprobados = 0
        cursos_desaprobados = 0
        
        for ins in inscripciones:
            curso = ins.curso
            creditos = curso.creditos or 3
            
            evaluaciones = Evaluacion.query.filter_by(curso_id=curso.id).order_by(
                Evaluacion.fecha_creacion.asc(),
                Evaluacion.id.asc()
            ).all()
            
            notas_alumno = {n.evaluacion_id: float(n.nota) for n in ins.notas if n.nota is not None}
            
            desglose_notas = []
            suma_ponderada = 0.0
            
            for ev in evaluaciones:
                nota_val = notas_alumno.get(ev.id)
                desglose_notas.append({
                    'evaluacion': ev.nombre_evaluacion,
                    'peso': ev.peso,
                    'nota': nota_val
                })
                if nota_val is not None:
                    suma_ponderada += nota_val * (float(ev.peso) / 100.0 if ev.peso else 0.0)
                    
            promedio_curso = round(suma_ponderada, 1) if evaluaciones else 0.0
            
            inasistencias = sum(1 for a in ins.asistencias if not a.presente and not a.justificado)
            max_faltas = curso.max_faltas_permitidas
            es_dpi = (inasistencias > max_faltas) if (max_faltas is not None and curso.total_sesiones_programadas > 0) else False
            
            if es_dpi:
                condicion = 'DPI'
                cursos_desaprobados += 1
            elif promedio_curso >= nota_minima:
                condicion = 'APROBADO'
                cursos_aprobados += 1
            else:
                condicion = 'DESAPROBADO'
                cursos_desaprobados += 1
                
            suma_creditos += creditos
            suma_puntos_ponderados += promedio_curso * creditos
            
            boleta_cursos.append({
                'curso': curso,
                'creditos': creditos,
                'evaluaciones': desglose_notas,
                'promedio': promedio_curso,
                'inasistencias': inasistencias,
                'condicion': condicion
            })
            
        promedio_ponderado_semestral = round(suma_puntos_ponderados / suma_creditos, 2) if suma_creditos > 0 else 0.0
        
        estadisticas = {
            'total_cursos': len(inscripciones),
            'cursos_aprobados': cursos_aprobados,
            'cursos_desaprobados': cursos_desaprobados,
            'creditos_totales': suma_creditos,
            'promedio_ponderado': promedio_ponderado_semestral,
            'nota_minima_aprobatoria': nota_minima
        }
        
        html_content = render_template(
            'reportes/boleta_estudiante_pdf.html',
            estudiante=estudiante,
            semestre=semestre,
            ciclo=ciclo,
            boleta_cursos=boleta_cursos,
            estadisticas=estadisticas,
            config=config,
            fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        return {
            'html': html_content,
            'estudiante': estudiante,
            'semestre': semestre,
            'boleta_cursos': boleta_cursos,
            'estadisticas': estadisticas
        }