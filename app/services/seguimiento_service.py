from datetime import datetime
from app.models import Estudiante, SeguimientoRiesgo
from app.extensions import db
from app.services.riesgo_calculator_v2 import CalculatorRiesgoIntrasemestral
from app.services.config_service import cargar_configuracion
from app.services.logger import riesgo_logger

class SeguimientoService:
    @staticmethod
    def _actualizar_seguimiento(estudiante_id, semestre, resultado):
        seguimiento = SeguimientoRiesgo.query.filter_by(
            estudiante_id=estudiante_id,
            semestre=semestre
        ).first()

        if seguimiento:
            puntaje_anterior = float(seguimiento.puntaje_riesgo)
            nuevo_puntaje = float(resultado['puntaje_riesgo'])

            if nuevo_puntaje > puntaje_anterior + 0.05:
                tendencia = 'SUBE'
            elif nuevo_puntaje < puntaje_anterior - 0.05:
                tendencia = 'BAJA'
            else:
                tendencia = 'ESTABLE'

            seguimiento.puntaje_anterior = puntaje_anterior
            seguimiento.tendencia = tendencia
            seguimiento.categoria_riesgo = resultado['categoria']
            seguimiento.puntaje_riesgo = nuevo_puntaje
            seguimiento.factores_riesgo = resultado['factores']
            seguimiento.fecha_evaluacion = datetime.now().date()
        else:
            seguimiento = SeguimientoRiesgo(
                estudiante_id=estudiante_id,
                semestre=semestre,
                categoria_riesgo=resultado['categoria'],
                puntaje_riesgo=resultado['puntaje_riesgo'],
                puntaje_anterior=0.0,
                tendencia='ESTABLE',
                factores_riesgo=resultado['factores']
            )
            db.session.add(seguimiento)

    @staticmethod
    def recalcular_riesgo_semestre(semestre=None):
        try:
            config = cargar_configuracion()
            if not semestre:
                semestre = config.get('semestre_actual')

            calculador = CalculatorRiesgoIntrasemestral(config)
            estudiantes = Estudiante.query.filter_by(activo=True).all()
            procesados = 0

            for estudiante in estudiantes:
                try:
                    resultado = calculador.calcular_riesgo_estudiante(estudiante.id, semestre, db)
                    SeguimientoService._actualizar_seguimiento(estudiante.id, semestre, resultado)
                    procesados += 1
                except Exception as e:
                    riesgo_logger.error(f"Error procesando estudiante {estudiante.id}: {e}")
                    continue

            db.session.commit()
            return True, f"Se procesaron {procesados} estudiantes."
        except Exception as e:
            db.session.rollback()
            riesgo_logger.error(f"Error general en SeguimientoService: {e}")
            return False, str(e)

    @staticmethod
    def recalcular_estudiante(estudiante_id, semestre=None):
        try:
            config = cargar_configuracion()
            if not semestre:
                semestre = config.get('semestre_actual')

            calculador = CalculatorRiesgoIntrasemestral(config)
            resultado = calculador.calcular_riesgo_estudiante(estudiante_id, semestre, db)

            SeguimientoService._actualizar_seguimiento(estudiante_id, semestre, resultado)

            db.session.commit()
            return True, resultado
        except Exception as e:
            db.session.rollback()
            return False, str(e)
