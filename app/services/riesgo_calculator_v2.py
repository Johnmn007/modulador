# app/services/riesgo_calculator_v2.py - VERSIÓN CORREGIDA
from app.services.logger import riesgo_logger, log_exception
import logging
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from sqlalchemy import text  # IMPORTANTE: Agregar esta importación

@dataclass
class FactorRiesgo:
    nombre: str
    valor: float
    peso: float  
    descripcion: str

class CalculatorRiesgoIntrasemestral:
    """
    NUEVA VERSIÓN - Especializada en evaluación intrasemestral
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.umbral_amarillo = self.config.get('umbral_amarillo', 0.4)
        self.umbral_rojo = self.config.get('umbral_rojo', 0.7)
        
        # Pesos balanceados (pueden ser ajustados desde config)
        self.peso_rendimiento = self.config.get('peso_rendimiento', 0.35)
        self.peso_asistencia = self.config.get('peso_asistencia', 0.25)
        self.peso_distribucion = self.config.get('peso_distribucion', 0.20)
        self.peso_historial = self.config.get('peso_historial', 0.20)

    def calcular_riesgo_estudiante(self, estudiante_id: int, semestre: str, db) -> Dict:
        """Calcula riesgo usando solo factores del semestre actual"""
        try:
            factores = self._evaluar_factores_intrasemestrales(estudiante_id, semestre, db)
            puntaje_total = self._calcular_puntaje_total(factores)
            categoria = self._determinar_categoria(puntaje_total)
            
            return {
                'puntaje_riesgo': round(puntaje_total, 3),
                'categoria': categoria,
                'factores': [
                    {
                        'nombre': f.nombre,
                        'valor': round(f.valor, 3),
                        'peso': f.peso,
                        'descripcion': f.descripcion,
                        'contribucion': round(f.valor * f.peso, 3)
                    }
                    for f in factores
                ],
                'recomendaciones': self._generar_recomendaciones(factores, categoria)
            }
        except Exception as e:
            riesgo_logger.error(f"Error calculando riesgo para estudiante {estudiante_id}: {e}")
            return {
                'puntaje_riesgo': 0.0,
                'categoria': 'SIN_RIESGO',
                'factores': [],
                'recomendaciones': ['Error en cálculo - Revisar datos']
            }

    def _evaluar_factores_intrasemestrales(self, estudiante_id: int, semestre: str, db) -> List[FactorRiesgo]:
        """Evalúa ÚNICAMENTE factores del semestre actual"""
        factores = []

        # Factor 1: Rendimiento académico ACTUAL
        factor_notas = self._evaluar_rendimiento_actual(estudiante_id, semestre, db)
        factores.append(factor_notas)

        # Factor 2: Asistencia ACTUAL  
        factor_asistencia = self._evaluar_asistencia_actual(estudiante_id, semestre, db)
        factores.append(factor_asistencia)

        # Factor 3: Distribución de riesgo entre cursos
        factor_distribucion = self._evaluar_distribucion_riesgo(estudiante_id, semestre, db)
        factores.append(factor_distribucion)

        # Factor 4: Historial académico (NUEVO)
        factor_historial = self._evaluar_historial_academico(estudiante_id, semestre, db)
        factores.append(factor_historial)

        return factores

    def _evaluar_rendimiento_actual(self, estudiante_id: int, semestre: str, db) -> FactorRiesgo:
        """Evalúa rendimiento BASADO EN DATOS ACTUALES del semestre"""
        # CONSULTA CORREGIDA: Usar text() y parámetros nombrados
        query = text("""
        SELECT c.nombre_curso, AVG(n.nota) as promedio_curso, COUNT(n.id) as evaluaciones
        FROM cursos c
        JOIN ciclos ci ON c.ciclo_id = ci.id
        JOIN inscripciones i ON c.id = i.curso_id
        LEFT JOIN notas n ON i.id = n.inscripcion_id
        WHERE i.estudiante_id = :estudiante_id AND ci.codigo_ciclo = :semestre
        GROUP BY c.id, c.nombre_curso
        """)
        
        try:
            # EJECUCIÓN CORREGIDA: Usar parámetros nombrados
            cursos = db.session.execute(query, {
                'estudiante_id': estudiante_id, 
                'semestre': semestre
            }).fetchall()
            
            if not cursos:
                return FactorRiesgo("Rendimiento Actual", 0.5, self.peso_rendimiento, 
                                  "Sin cursos inscritos")

            # Calcular métricas
            total_notas = 0
            total_evaluaciones = 0
            cursos_con_datos = 0
            
            for curso in cursos:
                if curso.promedio_curso is not None:  # CORREGIDO: usar punto en lugar de corchetes
                    total_notas += curso.promedio_curso * curso.evaluaciones
                    total_evaluaciones += curso.evaluaciones
                    cursos_con_datos += 1

            if total_evaluaciones == 0:
                return FactorRiesgo("Rendimiento Actual", 0.5, self.peso_rendimiento,
                                  f"Inscrito en {len(cursos)} cursos pero sin evaluaciones")

            promedio_general = total_notas / total_evaluaciones
            
            # FACTOR ADAPTATIVO: Considerar completitud
            evaluaciones_esperadas = len(cursos) * 3  # Asumiendo 3 eval por curso
            factor_completitud = min(total_evaluaciones / evaluaciones_esperadas, 1.0)
            
            # Escala de riesgo con ajuste por completitud
            if promedio_general >= 14.5:
                valor_base = 0.1
            elif promedio_general >= 12.5:
                valor_base = 0.3
            elif promedio_general >= 10.5:
                valor_base = 0.6
            else:
                valor_base = 0.9
                
            # Eliminada la reducción de riesgo por completitud (ocultaba estudiantes reprobando tempranamente)
            valor_ajustado = valor_base

            descripcion = (f"Promedio: {promedio_general:.1f} | "
                         f"{total_evaluaciones} evaluaciones | "
                         f"Completitud: {factor_completitud:.0%}")
            return FactorRiesgo("Rendimiento Actual", valor_ajustado, self.peso_rendimiento, descripcion)
            
        except Exception as e:
            riesgo_logger.error(f"Error en evaluación de rendimiento: {e}")
            return FactorRiesgo("Rendimiento Actual", 0.5, self.peso_rendimiento, "Error en cálculo")

    def _evaluar_asistencia_actual(self, estudiante_id: int, semestre: str, db) -> FactorRiesgo:
        """Evalúa asistencia del semestre actual basada en la regla institucional del 30% de inasistencias sobre el total programado (16 semanas)"""
        import math
        query = text("""
        SELECT 
            c.id as curso_id,
            c.nombre_curso,
            COALESCE(c.total_sesiones, COALESCE(c.sesiones_por_semana, 2) * 16) as total_programadas,
            COALESCE(c.limite_inasistencia_porcentaje, 30.0) as limite_pct,
            COUNT(a.id) as total_clases_tomadas,
            SUM(CASE WHEN a.presente = TRUE THEN 1 ELSE 0 END) as asistencias,
            SUM(CASE WHEN a.justificado = TRUE THEN 1 ELSE 0 END) as justificadas,
            SUM(CASE WHEN a.presente = FALSE AND a.justificado = FALSE THEN 1 ELSE 0 END) as inasistencias
        FROM inscripciones i
        JOIN cursos c ON i.curso_id = c.id
        JOIN ciclos ci ON c.ciclo_id = ci.id
        LEFT JOIN asistencias a ON a.inscripcion_id = i.id
        WHERE i.estudiante_id = :estudiante_id AND ci.codigo_ciclo = :semestre
        GROUP BY c.id, c.nombre_curso, c.total_sesiones, c.sesiones_por_semana, c.limite_inasistencia_porcentaje
        """)
        
        try:
            cursos_asistencia = db.session.execute(query, {
                'estudiante_id': estudiante_id, 
                'semestre': semestre
            }).fetchall()
            
            if not cursos_asistencia:
                return FactorRiesgo("Asistencia Actual", 0.1, self.peso_asistencia, 
                                  "Sin cursos inscritos en el ciclo")

            cursos_dpi = []
            cursos_alerta_critica = []
            cursos_preventivo = []
            total_inasistencias_general = 0
            total_programadas_general = 0
            total_tomadas_general = 0
            total_presentes_general = 0
            
            for row in cursos_asistencia:
                total_prog = int(row.total_programadas) if row.total_programadas else 32
                limite_pct = float(row.limite_pct) if row.limite_pct else 30.0
                max_faltas = math.floor(total_prog * (limite_pct / 100.0))
                inasistencias = int(row.inasistencias or 0)
                tomadas = int(row.total_clases_tomadas or 0)
                presentes = int(row.asistencias or 0)
                
                faltas_disp = max_faltas - inasistencias
                total_inasistencias_general += inasistencias
                total_programadas_general += total_prog
                total_tomadas_general += tomadas
                total_presentes_general += presentes
                
                if faltas_disp < 0:
                    cursos_dpi.append(f"{row.nombre_curso} ({inasistencias}/{max_faltas} máx.)")
                elif faltas_disp <= 1:
                    cursos_alerta_critica.append(f"{row.nombre_curso} (resta {faltas_disp} falta)")
                elif faltas_disp <= 3 and inasistencias > 0:
                    cursos_preventivo.append(f"{row.nombre_curso} (restan {faltas_disp})")
            
            # Determinación de riesgo según proximidad al límite reglamentario de 30%
            if cursos_dpi:
                valor = 0.95
                descripcion = f"🚨 LÍMITE SUPERADO (DPI >30%) en: {', '.join(cursos_dpi)}"
            elif cursos_alerta_critica:
                valor = 0.75
                descripcion = f"⚠️ ALERTA CRÍTICA: Próximo al 30% de faltas en: {', '.join(cursos_alerta_critica)}"
            elif cursos_preventivo:
                valor = 0.45
                descripcion = f"Inasistencias en seguimiento: {', '.join(cursos_preventivo)}"
            else:
                valor = 0.1
                descripcion = f"Asistencia regular ({total_inasistencias_general} faltas acumuladas en el ciclo)"

            return FactorRiesgo("Asistencia Actual", valor, self.peso_asistencia, descripcion)
            
        except Exception as e:
            riesgo_logger.error(f"Error en evaluación de asistencia: {e}")
            return FactorRiesgo("Asistencia Actual", 0.5, self.peso_asistencia, "Error en cálculo")

    def _evaluar_distribucion_riesgo(self, estudiante_id: int, semestre: str, db) -> FactorRiesgo:
        """Evalúa distribución de riesgo entre cursos"""
        # CONSULTA CORREGIDA
        query = text("""
        SELECT c.nombre_curso, AVG(n.nota) as promedio_curso, COUNT(n.id) as evaluaciones
        FROM cursos c
        JOIN ciclos ci ON c.ciclo_id = ci.id
        JOIN inscripciones i ON c.id = i.curso_id
        LEFT JOIN notas n ON i.id = n.inscripcion_id
        WHERE i.estudiante_id = :estudiante_id AND ci.codigo_ciclo = :semestre
        GROUP BY c.id, c.nombre_curso
        """)
        
        try:
            # EJECUCIÓN CORREGIDA
            cursos = db.session.execute(query, {
                'estudiante_id': estudiante_id, 
                'semestre': semestre
            }).fetchall()
            
            if not cursos:
                return FactorRiesgo("Distribución de Riesgo", 0.5, self.peso_distribucion, 
                                  "Sin cursos inscritos")

            cursos_en_riesgo = 0
            total_cursos = len(cursos)
            
            for curso in cursos:
                # Curso en riesgo si:
                if curso.promedio_curso is None:  # CORREGIDO: usar punto
                    cursos_en_riesgo += 0.5  # Riesgo potencial (sin eval)
                elif curso.promedio_curso < 12.5:
                    if curso.evaluaciones >= 2:  # Si tiene al menos 2 eval, confirmado
                        cursos_en_riesgo += 1
                    else:  # Pocas eval, riesgo moderado
                        cursos_en_riesgo += 0.7

            proporcion_riesgo = cursos_en_riesgo / total_cursos
            
            # Escala de riesgo por distribución
            if proporcion_riesgo == 0:
                valor = 0.1
            elif proporcion_riesgo <= 0.3:
                valor = 0.3
            elif proporcion_riesgo <= 0.6:
                valor = 0.6
            else:
                valor = 0.9

            descripcion = f"{cursos_en_riesgo:.1f} de {total_cursos} cursos requieren atención"
            return FactorRiesgo("Distribución de Riesgo", valor, self.peso_distribucion, descripcion)
            
        except Exception as e:
            riesgo_logger.error(f"Error en evaluación de distribución: {e}")
            return FactorRiesgo("Distribución de Riesgo", 0.5, self.peso_distribucion, "Error en cálculo")

    def _evaluar_historial_academico(self, estudiante_id: int, semestre_actual: str, db) -> FactorRiesgo:
        """Evalúa el desempeño histórico del estudiante (semestres anteriores)"""
        query = text("""
        SELECT AVG(n.nota) as promedio_historico, COUNT(DISTINCT ci.codigo_ciclo) as semestres_previos
        FROM notas n
        JOIN inscripciones i ON n.inscripcion_id = i.id
        JOIN cursos c ON i.curso_id = c.id
        JOIN ciclos ci ON c.ciclo_id = ci.id
        WHERE i.estudiante_id = :estudiante_id AND ci.codigo_ciclo < :semestre_actual
        """)
        
        try:
            result = db.session.execute(query, {
                'estudiante_id': estudiante_id,
                'semestre_actual': semestre_actual
            }).fetchone()
            
            if not result or result.promedio_historico is None:
                # Estudiante nuevo (cachimbó) - Riesgo neutral
                return FactorRiesgo("Historial Académico", 0.5, self.peso_historial, "Estudiante nuevo (Sin historial)")

            promedio = float(result.promedio_historico)
            semestres = result.semestres_previos
            
            # Escala de riesgo histórica
            if promedio >= 15:
                valor = 0.1
            elif promedio >= 12.5:
                valor = 0.3
            elif promedio >= 10.5:
                valor = 0.6
            else:
                valor = 0.9
                
            descripcion = f"Promedio histórico: {promedio:.2f} ({semestres} semestres previos)"
            return FactorRiesgo("Historial Académico", valor, self.peso_historial, descripcion)
            
        except Exception as e:
            riesgo_logger.error(f"Error en evaluación de historial: {e}")
            return FactorRiesgo("Historial Académico", 0.5, self.peso_historial, "Error en historial")

    def _calcular_puntaje_total(self, factores: List[FactorRiesgo]) -> float:
        return sum(factor.valor * factor.peso for factor in factores)

    def _determinar_categoria(self, puntaje: float) -> str:
        if puntaje < self.umbral_amarillo:
            return "SIN_RIESGO"
        elif puntaje < self.umbral_rojo:
            return "ALERTA_AMARILLA"
        else:
            return "ALERTA_ROJA"

    def _generar_recomendaciones(self, factores: List[FactorRiesgo], categoria: str) -> List[str]:
        recomendaciones = []
        
        if categoria == "SIN_RIESGO":
            recomendaciones.append("✅ Mantener el buen desempeño académico")
            return recomendaciones

        for factor in factores:
            if factor.valor > 0.5:
                if factor.nombre == "Rendimiento Actual":
                    recomendaciones.append("📚 Reforzamiento académico inmediato")
                    recomendaciones.append("⏰ Revisar técnicas de estudio y planificación")
                    
                elif factor.nombre == "Asistencia Actual":
                    if factor.valor >= 0.9:
                        recomendaciones.append("🚨 Regularización por DPI: Estudiante superó el 30% de inasistencias en una o más asignaturas")
                        recomendaciones.append("⚖️ Notificar formalmente a Coordinación Académica para resolución de inhabilitación")
                    else:
                        recomendaciones.append("📅 Plan de compromiso de asistencia y seguimiento de faltas restantes")
                        recomendaciones.append("🏫 Entrevista preventiva con Bienestar Estudiantil para evaluar causas e inasistencias justificables")
                    
                elif factor.nombre == "Distribución de Riesgo":
                    recomendaciones.append("🎯 Priorizar atención en cursos críticos")
                    recomendaciones.append("📊 Evaluar carga académica con coordinación")
                    
                elif factor.nombre == "Historial Académico":
                    recomendaciones.append("📈 Revisar antecedentes académicos y plan de nivelación")
                    recomendaciones.append("🔍 Entrevista de orientación académica")

        if categoria == "ALERTA_AMARILLA":
            recomendaciones.append("🔔 Seguimiento quincenal por coordinación académica")
            recomendaciones.append("🎯 Establecer metas de mejora específicas")
            
        elif categoria == "ALERTA_ROJA":
            recomendaciones.append("🚨 INTERVENCIÓN INMEDIATA - Reunión urgente requerida")
            recomendaciones.append("📞 Notificar a departamento estudiantil y familia")
            recomendaciones.append("⚖️ Evaluar posible ajuste de matrícula")

        return recomendaciones