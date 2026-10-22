import random
import sys
import os
from datetime import date
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Estudiante, SeguimientoRiesgo

app = create_app()

def generate_mock_data():
    with app.app_context():
        # Limpiar registros existentes de 2026-1 si los hay para evitar duplicados
        SeguimientoRiesgo.query.filter_by(semestre='2026-1').delete()
        
        estudiantes = Estudiante.query.all()
        print(f"Generando datos para {len(estudiantes)} estudiantes...")
        
        count_roja = 0
        count_amarilla = 0
        count_verde = 0
        
        for est in estudiantes:
            # Distribución de riesgo realista
            # 60% Sin Riesgo, 25% Alerta Amarilla, 15% Alerta Roja
            rand = random.random()
            
            if rand < 0.15:
                categoria = 'ALERTA_ROJA'
                puntaje = random.uniform(0.71, 0.95)
                tendencia = random.choice(['SUBE', 'ESTABLE'])
                obs = "Estudiante presenta múltiples cursos desaprobados e inasistencias reiteradas. Requiere intervención tutorial urgente."
                factores = [
                    {"nombre": "Riesgo Histórico", "valor": random.uniform(0.6, 0.9), "peso": 0.3, "descripcion": "Promedio general deficiente históricamente"},
                    {"nombre": "Asistencia Actual", "valor": random.uniform(0.7, 1.0), "peso": 0.3, "descripcion": "Asistencia crítica en múltiples cursos"},
                    {"nombre": "Rendimiento Actual", "valor": random.uniform(0.75, 1.0), "peso": 0.4, "descripcion": "Desempeño bajo sostenido en el ciclo actual"}
                ]
                count_roja += 1
            elif rand < 0.40:
                categoria = 'ALERTA_AMARILLA'
                puntaje = random.uniform(0.41, 0.69)
                tendencia = random.choice(['SUBE', 'BAJA', 'ESTABLE'])
                obs = "Estudiante presenta algunas deficiencias en cursos clave. Monitorear desempeño en próximas evaluaciones."
                factores = [
                    {"nombre": "Riesgo Histórico", "valor": random.uniform(0.3, 0.6), "peso": 0.3, "descripcion": "Promedio general aceptable a regular"},
                    {"nombre": "Asistencia Actual", "valor": random.uniform(0.3, 0.6), "peso": 0.3, "descripcion": "Asistencia irregular puntual"},
                    {"nombre": "Rendimiento Actual", "valor": random.uniform(0.4, 0.7), "peso": 0.4, "descripcion": "Desempeño con altibajos en el ciclo actual"}
                ]
                count_amarilla += 1
            else:
                categoria = 'SIN_RIESGO'
                puntaje = random.uniform(0.1, 0.39)
                tendencia = random.choice(['BAJA', 'ESTABLE'])
                obs = "Estudiante con desempeño académico óptimo. Sin alertas identificadas."
                factores = [
                    {"nombre": "Riesgo Histórico", "valor": random.uniform(0.0, 0.3), "peso": 0.3, "descripcion": "Promedio general bueno a excelente"},
                    {"nombre": "Asistencia Actual", "valor": random.uniform(0.0, 0.2), "peso": 0.3, "descripcion": "Asistencia regular y constante"},
                    {"nombre": "Rendimiento Actual", "valor": random.uniform(0.1, 0.3), "peso": 0.4, "descripcion": "Desempeño satisfactorio en el ciclo actual"}
                ]
                count_verde += 1
            
            seguimiento = SeguimientoRiesgo(
                estudiante_id=est.id,
                semestre='2026-1',
                categoria_riesgo=categoria,
                puntaje_riesgo=puntaje,
                puntaje_anterior=max(0, puntaje + random.uniform(-0.15, 0.15)),
                tendencia=tendencia,
                fecha_evaluacion=date(2026, 7, 15), # Fecha final de 2026-1
                factores_riesgo=factores,
                observaciones=obs
            )
            db.session.add(seguimiento)
            
        db.session.commit()
        print("¡Datos generados exitosamente!")
        print(f"Resumen: {count_roja} Roja | {count_amarilla} Amarilla | {count_verde} Sin Riesgo")

if __name__ == '__main__':
    generate_mock_data()
