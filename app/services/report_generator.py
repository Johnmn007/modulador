import os
import json
from datetime import datetime
from flask import render_template
from app.models import Estudiante, SeguimientoRiesgo, Curso, Inscripcion, Nota, Asistencia, Evaluacion, IndicadorLogro
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
        """Genera acta oficial consolidada de calificaciones para un curso organizada por Indicadores de Logro"""
        curso = Curso.query.get_or_404(curso_id)
        config = cargar_configuracion()
        nota_minima = float(config.get('nota_minima_aprobatoria', 12.5))
        
        # Obtener Indicadores de Logro del curso ordenados
        indicadores = IndicadorLogro.query.filter_by(curso_id=curso_id).order_by(
            IndicadorLogro.orden.asc(),
            IndicadorLogro.id.asc()
        ).all()
        
        if not indicadores:
            il1 = IndicadorLogro(curso_id=curso_id, codigo='IL-01', nombre='Indicador de Logro 01', peso=100.0, orden=1)
            db.session.add(il1)
            db.session.commit()
            indicadores = [il1]
            
        # Lista plana de todas las evaluaciones agrupadas por indicador
        evaluaciones = []
        for il in indicadores:
            evaluaciones.extend(il.evaluaciones)
            
        # Si hubiera evaluaciones huérfanas sin indicador, asignarlas al primer indicador
        evals_huerfanas = Evaluacion.query.filter_by(curso_id=curso_id, indicador_id=None).all()
        for ev in evals_huerfanas:
            ev.indicador_id = indicadores[0].id
            evaluaciones.append(ev)
        if evals_huerfanas:
            db.session.commit()
            
        # Estudiantes inscritos activos
        inscripciones = Inscripcion.query.filter_by(curso_id=curso_id, estado='ACTIVO').join(
            Estudiante
        ).order_by(Estudiante.apellidos, Estudiante.nombres).all()
        
        # Mapeo de notas {inscripcion_id: {evaluacion_id: nota_float}}
        notas_raw = Nota.query.join(Inscripcion).filter(
            Inscripcion.curso_id == curso_id
        ).all()
        
        notas_dict = {}
        evaluaciones_con_nota = set()
        for n in notas_raw:
            if n.nota is not None:
                evaluaciones_con_nota.add(n.evaluacion_id)
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
            bloques_il = []
            promedios_para_final = []
            
            for il in indicadores:
                notas_il = []
                suma_pond_il = 0.0
                suma_pesos_il = 0.0
                
                for ev in il.evaluaciones:
                    val = notas_alumno.get(ev.id)
                    # Si la evaluación ya tiene notas registradas en el curso y este alumno no tiene nota, asignar 0.0
                    if val is None and ev.id in evaluaciones_con_nota:
                        val = 0.0
                        
                    notas_list.append(val)
                    notas_il.append(val)
                    if val is not None and ev.peso:
                        suma_pond_il += val * float(ev.peso)
                        suma_pesos_il += float(ev.peso)
                        
                if suma_pesos_il > 0:
                    promedio_il = round(suma_pond_il / suma_pesos_il, 1)
                else:
                    notas_validas = [n for n in notas_il if n is not None]
                    promedio_il = round(sum(notas_validas) / len(notas_validas), 1) if notas_validas else None
                    
                bloques_il.append({
                    'indicador': il,
                    'notas': notas_il,
                    'promedio_il': promedio_il
                })
                
                if promedio_il is not None:
                    promedios_para_final.append((promedio_il, float(il.peso or 0)))
                    
            # Promedio ponderado final de los Indicadores de Logro
            if promedios_para_final:
                suma_pesos_final = sum(peso for _, peso in promedios_para_final)
                if suma_pesos_final > 0:
                    promedio_final = round(sum(p * w for p, w in promedios_para_final) / suma_pesos_final, 1)
                else:
                    promedio_final = round(sum(p for p, _ in promedios_para_final) / len(promedios_para_final), 1)
            else:
                promedio_final = 0.0
            
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
                'bloques_il': bloques_il,
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
            indicadores=indicadores,
            evaluaciones=evaluaciones,
            consolidado=consolidado,
            estadisticas=estadisticas,
            config=config,
            fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        return {
            'html': html_content,
            'curso': curso,
            'indicadores': indicadores,
            'evaluaciones': evaluaciones,
            'consolidado': consolidado,
            'estadisticas': estadisticas
        }

    def generar_excel_notas_curso(self, resultado_o_curso_id):
        """
        Genera el libro Excel (.xlsx) con el acta consolidada oficial de calificaciones.
        Estructurada con encabezados institucionales, desglose por Indicador de Logro,
        evaluaciones ponderadas, promedios parciales y finales, faltas, condición y
        resumen estadístico institucional.
        """
        import io
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        if isinstance(resultado_o_curso_id, (int, str)):
            resultado = self.generar_reporte_notas_curso(int(resultado_o_curso_id))
        else:
            resultado = resultado_o_curso_id

        curso = resultado['curso']
        indicadores = resultado['indicadores']
        evaluaciones = resultado['evaluaciones']
        consolidado = resultado['consolidado']
        estadisticas = resultado['estadisticas']
        nota_minima = float(estadisticas.get('nota_minima_aprobatoria', 12.5))

        wb = openpyxl.Workbook()
        ws = wb.active
        codigo_limpio = (curso.codigo_curso or 'CURSO')[:20]
        ws.title = f"Acta {codigo_limpio}"
        ws.views.sheetView[0].showGridLines = True

        # Paleta de Colores Institucional
        c_navy = "0F172A"       # Encabezado principal
        c_slate = "1E293B"      # Subencabezado / evaluacion
        c_ocean = "0369A1"      # Indicador de logro
        c_sky = "0284C7"        # Subtotal promedio IL
        c_subtotal_bg = "F0F9FF"# Fondo celda promedio IL
        c_final_bg = "F1F5F9"   # Fondo celda promedio final
        c_border = "CBD5E1"     # Bordes suaves
        c_zebra = "F8FAFC"      # Fondo fila par

        # Fuentes
        f_title1 = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        f_title2 = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
        f_th = Font(name="Calibri", size=8.5, bold=True, color="FFFFFF")
        f_th_small = Font(name="Calibri", size=7.5, bold=True, color="FFFFFF")
        f_cell_normal = Font(name="Calibri", size=9.5, color="1E293B")
        f_cell_bold = Font(name="Calibri", size=9.5, bold=True, color="1E293B")
        f_aprobado = Font(name="Calibri", size=9.5, bold=True, color="15803D")
        f_desaprobado = Font(name="Calibri", size=9.5, bold=True, color="B91C1C")
        f_final_aprobado = Font(name="Calibri", size=10.5, bold=True, color="15803D")
        f_final_desaprobado = Font(name="Calibri", size=10.5, bold=True, color="B91C1C")
        f_null = Font(name="Calibri", size=9.5, color="94A3B8")

        # Rellenos
        fill_navy = PatternFill(start_color=c_navy, end_color=c_navy, fill_type="solid")
        fill_slate = PatternFill(start_color=c_slate, end_color=c_slate, fill_type="solid")
        fill_ocean = PatternFill(start_color=c_ocean, end_color=c_ocean, fill_type="solid")
        fill_sky = PatternFill(start_color=c_sky, end_color=c_sky, fill_type="solid")
        fill_subtotal = PatternFill(start_color=c_subtotal_bg, end_color=c_subtotal_bg, fill_type="solid")
        fill_final = PatternFill(start_color=c_final_bg, end_color=c_final_bg, fill_type="solid")
        fill_info = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_even = PatternFill(start_color=c_zebra, end_color=c_zebra, fill_type="solid")
        fill_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

        # Badges condición
        fill_badge_aprobado = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        font_badge_aprobado = Font(name="Calibri", size=9, bold=True, color="15803D")

        fill_badge_desaprobado = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        font_badge_desaprobado = Font(name="Calibri", size=9, bold=True, color="B91C1C")

        fill_badge_dpi = PatternFill(start_color="7F1D1D", end_color="7F1D1D", fill_type="solid")
        font_badge_dpi = Font(name="Calibri", size=9, bold=True, color="FFFFFF")

        # Bordes
        border_thin = Border(
            left=Side(style='thin', color=c_border),
            right=Side(style='thin', color=c_border),
            top=Side(style='thin', color=c_border),
            bottom=Side(style='thin', color=c_border)
        )
        border_info = Border(
            left=Side(style='thin', color="E2E8F0"),
            right=Side(style='thin', color="E2E8F0"),
            top=Side(style='thin', color="E2E8F0"),
            bottom=Side(style='thin', color="E2E8F0")
        )

        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")
        align_th = Alignment(horizontal="center", vertical="center", wrap_text=True)

        def style_cells(min_col, min_row, max_col, max_row, font=None, fill=None, border=None, alignment=None, number_format=None):
            for r in range(min_row, max_row + 1):
                for c in range(min_col, max_col + 1):
                    cell = ws.cell(row=r, column=c)
                    if font: cell.font = font
                    if fill: cell.fill = fill
                    if border: cell.border = border
                    if alignment: cell.alignment = alignment
                    if number_format: cell.number_format = number_format

        # Calcular número total de columnas
        total_eval_cols = sum(len(il.evaluaciones) + 1 for il in indicadores)
        total_cols = 3 + total_eval_cols + 3  # N°, Código, Nombre, [ILs...], Prom. Final, Faltas, Condición
        total_cols = max(total_cols, 8)       # Al menos 8 columnas para la cabecera

        # Fila 1: Banner institucional
        ws.row_dimensions[1].height = 20
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
        ws.cell(1, 1, "SADES — SISTEMA DE GESTIÓN Y SEGUIMIENTO ESTUDIANTIL")
        style_cells(1, 1, total_cols, 1, font=f_title1, fill=fill_navy, alignment=align_center)

        # Fila 2: Título del documento
        ws.row_dimensions[2].height = 26
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_cols)
        ws.cell(2, 1, "ACTA CONSOLIDADA DE EVALUACIÓN ACADÉMICA")
        style_cells(1, 2, total_cols, 2, font=f_title2, fill=fill_slate, alignment=align_center)

        # Fila 3: Separador
        ws.row_dimensions[3].height = 8

        # Fila 4 a 6: Ficha informativa del curso
        ws.row_dimensions[4].height = 20
        ws.row_dimensions[5].height = 20
        ws.row_dimensions[6].height = 20

        # Rellenar cuadro de información
        style_cells(1, 4, total_cols, 6, fill=fill_info, border=border_info)

        col_mid = max(3, total_cols // 2)

        # Fila 4:
        ws.cell(4, 1, "ASIGNATURA:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(4, 1).alignment = align_left
        ws.merge_cells(start_row=4, start_column=2, end_row=4, end_column=col_mid)
        ws.cell(4, 2, f"{curso.nombre_curso} ({curso.codigo_curso})").font = Font(name="Calibri", size=9.5, bold=True, color=c_navy)
        ws.cell(4, 2).alignment = align_left

        col_doc_lbl = col_mid + 1
        ws.cell(4, col_doc_lbl, "DOCENTE:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(4, col_doc_lbl).alignment = align_left
        col_doc_val = col_doc_lbl + 1
        ws.merge_cells(start_row=4, start_column=col_doc_val, end_row=4, end_column=total_cols - 2)
        if curso.docente:
            docente_nombre = getattr(curso.docente, 'nombre_completo', None) or getattr(curso.docente, 'username', 'Docente')
        else:
            docente_nombre = "No asignado"
        ws.cell(4, col_doc_val, docente_nombre).font = Font(name="Calibri", size=9.5, bold=True, color=c_navy)
        ws.cell(4, col_doc_val).alignment = align_left

        ws.cell(4, total_cols - 1, "CRÉDITOS:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(4, total_cols, str(curso.creditos or 0)).font = Font(name="Calibri", size=9.5, bold=True, color=c_navy)
        ws.cell(4, total_cols).alignment = align_center

        # Fila 5:
        ws.cell(5, 1, "PERIODO / CICLO:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(5, 1).alignment = align_left
        ws.merge_cells(start_row=5, start_column=2, end_row=5, end_column=col_mid)
        ciclo_codigo = curso.ciclo.codigo_ciclo if curso.ciclo else "N/A"
        ws.cell(5, 2, ciclo_codigo).font = Font(name="Calibri", size=9.5, color=c_navy)
        ws.cell(5, 2).alignment = align_left

        ws.cell(5, col_doc_lbl, "SEMESTRE:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(5, col_doc_lbl).alignment = align_left
        ws.merge_cells(start_row=5, start_column=col_doc_val, end_row=5, end_column=total_cols - 2)
        ws.cell(5, col_doc_val, f"Semestre {curso.semestre}").font = Font(name="Calibri", size=9.5, color=c_navy)
        ws.cell(5, col_doc_val).alignment = align_left

        ws.cell(5, total_cols - 1, "SESIONES:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(5, total_cols, f"{curso.total_sesiones_programadas}").font = Font(name="Calibri", size=9.5, color=c_navy)
        ws.cell(5, total_cols).alignment = align_center

        # Fila 6:
        ws.cell(6, 1, "LÍMITE FALTAS:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(6, 1).alignment = align_left
        ws.merge_cells(start_row=6, start_column=2, end_row=6, end_column=col_mid)
        ws.cell(6, 2, f"{curso.max_faltas_permitidas} (30% DPI)").font = Font(name="Calibri", size=9.5, color=c_navy)
        ws.cell(6, 2).alignment = align_left

        ws.cell(6, col_doc_lbl, "NOTA MÍNIMA:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(6, col_doc_lbl).alignment = align_left
        ws.merge_cells(start_row=6, start_column=col_doc_val, end_row=6, end_column=total_cols - 2)
        ws.cell(6, col_doc_val, f"{nota_minima:.1f}").font = Font(name="Calibri", size=9.5, bold=True, color=c_navy)
        ws.cell(6, col_doc_val).alignment = align_left

        ws.cell(6, total_cols - 1, "EMISIÓN:").font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws.cell(6, total_cols, datetime.now().strftime('%d/%m/%Y')).font = Font(name="Calibri", size=8.5, color="64748B")
        ws.cell(6, total_cols).alignment = align_center

        # Fila 7: Separador
        ws.row_dimensions[7].height = 10

        # Filas 8 y 9: Encabezados de la Tabla Principal
        ws.row_dimensions[8].height = 24
        ws.row_dimensions[9].height = 28

        # N° (Col 1)
        ws.merge_cells(start_row=8, start_column=1, end_row=9, end_column=1)
        ws.cell(8, 1, "N°")
        style_cells(1, 8, 1, 9, font=f_th, fill=fill_navy, border=border_thin, alignment=align_center)

        # Código (Col 2)
        ws.merge_cells(start_row=8, start_column=2, end_row=9, end_column=2)
        ws.cell(8, 2, "CÓDIGO")
        style_cells(2, 8, 2, 9, font=f_th, fill=fill_navy, border=border_thin, alignment=align_center)

        # Apellidos y Nombres (Col 3)
        ws.merge_cells(start_row=8, start_column=3, end_row=9, end_column=3)
        ws.cell(8, 3, "APELLIDOS Y NOMBRES")
        style_cells(3, 8, 3, 9, font=f_th, fill=fill_navy, border=border_thin, alignment=align_center)

        current_col = 4
        subtotal_cols = []

        for il in indicadores:
            il_evals_count = len(il.evaluaciones)
            il_total_cols = il_evals_count + 1  # Evaluaciones + Subtotal
            start_col = current_col
            end_col = current_col + il_total_cols - 1

            # Nivel 1: Indicador de Logro
            ws.merge_cells(start_row=8, start_column=start_col, end_row=8, end_column=end_col)
            il_title = f"{il.codigo}{' - ' + il.nombre[:20] if il.nombre else ''} ({il.peso:.0f}%)"
            ws.cell(8, start_col, il_title)
            style_cells(start_col, 8, end_col, 8, font=f_th, fill=fill_ocean, border=border_thin, alignment=align_center)

            # Nivel 2: Evaluaciones
            for ev in il.evaluaciones:
                ws.cell(9, current_col, f"{ev.nombre_evaluacion[:14]}\n({ev.peso:.0f}%)")
                style_cells(current_col, 9, current_col, 9, font=f_th_small, fill=fill_slate, border=border_thin, alignment=align_th)
                current_col += 1

            # Nivel 2: Subtotal Promedio del Indicador
            ws.cell(9, current_col, f"Prom.\n{il.codigo}")
            style_cells(current_col, 9, current_col, 9, font=f_th_small, fill=fill_sky, border=border_thin, alignment=align_th)
            subtotal_cols.append(current_col)
            current_col += 1

        # Promedio Final
        col_prom_final = current_col
        ws.merge_cells(start_row=8, start_column=col_prom_final, end_row=9, end_column=col_prom_final)
        ws.cell(8, col_prom_final, "PROM.\nFINAL")
        style_cells(col_prom_final, 8, col_prom_final, 9, font=f_th, fill=fill_navy, border=border_thin, alignment=align_th)
        current_col += 1

        # Faltas
        col_faltas = current_col
        ws.merge_cells(start_row=8, start_column=col_faltas, end_row=9, end_column=col_faltas)
        ws.cell(8, col_faltas, "FALTAS")
        style_cells(col_faltas, 8, col_faltas, 9, font=f_th, fill=fill_slate, border=border_thin, alignment=align_th)
        current_col += 1

        # Condición
        col_condicion = current_col
        ws.merge_cells(start_row=8, start_column=col_condicion, end_row=9, end_column=col_condicion)
        ws.cell(8, col_condicion, "CONDICIÓN")
        style_cells(col_condicion, 8, col_condicion, 9, font=f_th, fill=fill_navy, border=border_thin, alignment=align_center)

        # Filas de Datos (Estudiantes)
        start_data_row = 10
        current_row = start_data_row

        if not consolidado:
            ws.row_dimensions[current_row].height = 24
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=total_cols)
            ws.cell(current_row, 1, "No existen estudiantes inscritos activos en este curso.")
            style_cells(1, current_row, total_cols, current_row, font=f_null, border=border_thin, alignment=align_center)
            current_row += 1
        else:
            for item in consolidado:
                ws.row_dimensions[current_row].height = 20
                row_fill = fill_even if (item['num'] % 2 == 0) else fill_odd

                # N°
                ws.cell(current_row, 1, item['num'])
                style_cells(1, current_row, 1, current_row, font=f_cell_normal, fill=row_fill, border=border_thin, alignment=align_center)

                # Código
                ws.cell(current_row, 2, item['codigo'])
                style_cells(2, current_row, 2, current_row, font=f_cell_bold, fill=row_fill, border=border_thin, alignment=align_center)

                # Nombre
                ws.cell(current_row, 3, item['nombre_completo'])
                style_cells(3, current_row, 3, current_row, font=f_cell_normal, fill=row_fill, border=border_thin, alignment=align_left)

                # Notas por Indicador
                c_idx = 4
                for bloque in item['bloques_il']:
                    for nota in bloque['notas']:
                        cell = ws.cell(current_row, c_idx)
                        if nota is not None:
                            cell.value = float(nota)
                            cell.number_format = '0.0'
                            cell.font = f_aprobado if float(nota) >= nota_minima else f_desaprobado
                        else:
                            cell.value = "-"
                            cell.font = f_null
                        cell.fill = row_fill
                        cell.border = border_thin
                        cell.alignment = align_center
                        c_idx += 1

                    # Promedio IL
                    cell_il = ws.cell(current_row, c_idx)
                    prom_il = bloque['promedio_il']
                    if prom_il is not None:
                        cell_il.value = float(prom_il)
                        cell_il.number_format = '0.0'
                        cell_il.font = f_aprobado if float(prom_il) >= nota_minima else f_desaprobado
                    else:
                        cell_il.value = "-"
                        cell_il.font = f_null
                    cell_il.fill = fill_subtotal
                    cell_il.border = border_thin
                    cell_il.alignment = align_center
                    c_idx += 1

                # Promedio Final
                cell_pf = ws.cell(current_row, col_prom_final)
                pf_val = item['promedio']
                cell_pf.value = float(pf_val)
                cell_pf.number_format = '0.0'
                if float(pf_val) >= nota_minima and item['condicion'] != 'DPI':
                    cell_pf.font = f_final_aprobado
                else:
                    cell_pf.font = f_final_desaprobado
                cell_pf.fill = fill_final
                cell_pf.border = border_thin
                cell_pf.alignment = align_center

                # Faltas
                cell_f = ws.cell(current_row, col_faltas)
                cell_f.value = int(item['faltas'])
                cell_f.fill = row_fill
                cell_f.border = border_thin
                cell_f.alignment = align_center
                if item.get('max_faltas') is not None and item['faltas'] > item['max_faltas']:
                    cell_f.font = f_desaprobado
                else:
                    cell_f.font = f_cell_normal

                # Condición con Badge
                cell_cond = ws.cell(current_row, col_condicion)
                cond_text = item['condicion']
                if cond_text == 'APROBADO':
                    cell_cond.value = "Aprobado"
                    cell_cond.fill = fill_badge_aprobado
                    cell_cond.font = font_badge_aprobado
                elif cond_text == 'DPI':
                    cell_cond.value = "DPI (>30%)"
                    cell_cond.fill = fill_badge_dpi
                    cell_cond.font = font_badge_dpi
                else:
                    cell_cond.value = "Desaprobado"
                    cell_cond.fill = fill_badge_desaprobado
                    cell_cond.font = font_badge_desaprobado
                cell_cond.border = border_thin
                cell_cond.alignment = align_center

                current_row += 1

        # Bloque de Resumen Estadístico
        current_row += 1
        ws.row_dimensions[current_row].height = 8  # Espacio

        current_row += 1
        ws.row_dimensions[current_row].height = 22
        stats_header_end = min(total_cols, 7)
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=stats_header_end)
        ws.cell(current_row, 2, "RESUMEN ESTADÍSTICO DEL RENDIMIENTO ACADÉMICO")
        style_cells(2, current_row, stats_header_end, current_row, font=Font(name="Calibri", size=9.5, bold=True, color=c_navy),
                    fill=PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid"),
                    border=border_thin, alignment=align_center)

        # Fila 1 de Estadísticas
        current_row += 1
        ws.row_dimensions[current_row].height = 20
        # Total Inscritos
        ws.cell(current_row, 2, "Total Inscritos:").font = f_cell_bold
        ws.cell(current_row, 2).alignment = align_left
        ws.cell(current_row, 2).fill = fill_odd
        ws.cell(current_row, 2).border = border_thin

        ws.cell(current_row, 3, estadisticas.get('total_estudiantes', 0)).font = f_cell_bold
        ws.cell(current_row, 3).alignment = align_center
        ws.cell(current_row, 3).fill = fill_odd
        ws.cell(current_row, 3).border = border_thin

        # Promedio del Aula
        ws.cell(current_row, 4, "Promedio Aula:").font = f_cell_bold
        ws.cell(current_row, 4).alignment = align_left
        ws.cell(current_row, 4).fill = fill_odd
        ws.cell(current_row, 4).border = border_thin

        cell_pa = ws.cell(current_row, 5, float(estadisticas.get('promedio_aula', 0.0)))
        cell_pa.font = f_cell_bold
        cell_pa.number_format = '0.00'
        cell_pa.alignment = align_center
        cell_pa.fill = fill_odd
        cell_pa.border = border_thin

        # Nota Máx / Mín
        ws.cell(current_row, 6, "Nota Máx / Mín:").font = f_cell_bold
        ws.cell(current_row, 6).alignment = align_left
        ws.cell(current_row, 6).fill = fill_odd
        ws.cell(current_row, 6).border = border_thin

        ws.cell(current_row, 7, f"{estadisticas.get('nota_maxima', 0):.1f} / {estadisticas.get('nota_minima', 0):.1f}").font = f_cell_bold
        ws.cell(current_row, 7).alignment = align_center
        ws.cell(current_row, 7).fill = fill_odd
        ws.cell(current_row, 7).border = border_thin

        # Fila 2 de Estadísticas
        current_row += 1
        ws.row_dimensions[current_row].height = 20
        # Aprobados
        ws.cell(current_row, 2, "Aprobados:").font = f_cell_bold
        ws.cell(current_row, 2).alignment = align_left
        ws.cell(current_row, 2).fill = fill_even
        ws.cell(current_row, 2).border = border_thin

        ws.cell(current_row, 3, f"{estadisticas.get('aprobados', 0)} ({estadisticas.get('porcentaje_aprobados', 0):.1f}%)").font = f_aprobado
        ws.cell(current_row, 3).alignment = align_center
        ws.cell(current_row, 3).fill = fill_even
        ws.cell(current_row, 3).border = border_thin

        # Desaprobados
        ws.cell(current_row, 4, "Desaprobados:").font = f_cell_bold
        ws.cell(current_row, 4).alignment = align_left
        ws.cell(current_row, 4).fill = fill_even
        ws.cell(current_row, 4).border = border_thin

        ws.cell(current_row, 5, f"{estadisticas.get('desaprobados', 0)} ({estadisticas.get('porcentaje_desaprobados', 0):.1f}%)").font = f_desaprobado
        ws.cell(current_row, 5).alignment = align_center
        ws.cell(current_row, 5).fill = fill_even
        ws.cell(current_row, 5).border = border_thin

        # Retirados por DPI
        ws.cell(current_row, 6, "Retirados DPI:").font = f_cell_bold
        ws.cell(current_row, 6).alignment = align_left
        ws.cell(current_row, 6).fill = fill_even
        ws.cell(current_row, 6).border = border_thin

        ws.cell(current_row, 7, str(estadisticas.get('dpi', 0))).font = f_desaprobado
        ws.cell(current_row, 7).alignment = align_center
        ws.cell(current_row, 7).fill = fill_even
        ws.cell(current_row, 7).border = border_thin

        # Ajuste de Ancho de Columnas
        col_widths = {
            1: 6,   # N°
            2: 14,  # Código
            3: 32,  # Apellidos y Nombres
        }
        for c in range(4, current_col):
            if c in subtotal_cols:
                col_widths[c] = 12
            elif c == col_prom_final:
                col_widths[c] = 12
            elif c == col_faltas:
                col_widths[c] = 9
            elif c == col_condicion:
                col_widths[c] = 15
            else:
                col_widths[c] = 11

        for c, w in col_widths.items():
            col_letter = get_column_letter(c)
            ws.column_dimensions[col_letter].width = w

        # Congelar Paneles en Celda D10 (Fija filas 1-9 y columnas A-C)
        ws.freeze_panes = "D10"

        # Exportar a BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

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
            
            indicadores = IndicadorLogro.query.filter_by(curso_id=curso.id).order_by(IndicadorLogro.orden, IndicadorLogro.id).all()
            if not indicadores:
                il1 = IndicadorLogro(curso_id=curso.id, codigo='IL-01', nombre='Indicador de Logro 01', peso=100.0, orden=1)
                db.session.add(il1)
                db.session.commit()
                indicadores = [il1]
                
            notas_alumno = {n.evaluacion_id: float(n.nota) for n in ins.notas if n.nota is not None}
            evaluaciones_con_nota_curso = set(
                n[0] for n in db.session.query(Nota.evaluacion_id).join(Inscripcion).filter(
                    Inscripcion.curso_id == curso.id,
                    Nota.nota.isnot(None)
                ).distinct().all()
            )
            
            desglose_indicadores = []
            desglose_notas_plano = []
            promedios_para_final = []
            
            for il in indicadores:
                desglose_evs = []
                suma_pond_il = 0.0
                suma_pesos_il = 0.0
                
                for ev in il.evaluaciones:
                    nota_val = notas_alumno.get(ev.id)
                    if nota_val is None and ev.id in evaluaciones_con_nota_curso:
                        nota_val = 0.0
                        
                    ev_dict = {
                        'evaluacion': ev.nombre_evaluacion,
                        'peso': ev.peso,
                        'nota': nota_val
                    }
                    desglose_evs.append(ev_dict)
                    desglose_notas_plano.append(ev_dict)
                    if nota_val is not None and ev.peso:
                        suma_pond_il += nota_val * float(ev.peso)
                        suma_pesos_il += float(ev.peso)
                        
                if suma_pesos_il > 0:
                    promedio_il = round(suma_pond_il / suma_pesos_il, 1)
                else:
                    valid_notes = [e['nota'] for e in desglose_evs if e['nota'] is not None]
                    promedio_il = round(sum(valid_notes) / len(valid_notes), 1) if valid_notes else None
                    
                desglose_indicadores.append({
                    'indicador': il,
                    'evaluaciones': desglose_evs,
                    'promedio_il': promedio_il
                })
                
                if promedio_il is not None:
                    promedios_para_final.append((promedio_il, float(il.peso or 0)))
                    
            if promedios_para_final:
                s_pesos_f = sum(w for _, w in promedios_para_final)
                if s_pesos_f > 0:
                    promedio_curso = round(sum(p * w for p, w in promedios_para_final) / s_pesos_f, 1)
                else:
                    promedio_curso = round(sum(p for p, _ in promedios_para_final) / len(promedios_para_final), 1)
            else:
                promedio_curso = 0.0
            
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
                'indicadores': desglose_indicadores,
                'evaluaciones': desglose_notas_plano,
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