# tests/test_riesgo.py
from datetime import date
from tests.test_base import BaseTestCase
from app.extensions import db
from app.models import Estudiante, Curso, Inscripcion, Evaluacion, Nota, Asistencia, SeguimientoRiesgo
from app.services.riesgo_calculator_v2 import CalculatorRiesgoIntrasemestral
from app.services.seguimiento_service import SeguimientoService

class TestRiesgo(BaseTestCase):
    def test_calcular_riesgo_estudiante_excelente(self):
        """Verifica el cálculo de riesgo para un estudiante con excelentes notas y asistencia"""
        # Crear asistencia perfecta (100% asistido)
        for i in range(5):
            asistencia = Asistencia(
                inscripcion_id=self.inscripcion.id,
                fecha=date(2026, 4, i+1),
                presente=True,
                justificado=False
            )
            db.session.add(asistencia)
        
        # Agregar notas altas (promedio = 17)
        eval2 = Evaluacion(curso_id=self.curso.id, nombre_evaluacion="PC2", peso=30.0)
        db.session.add(eval2)
        db.session.commit()
        
        nota2 = Nota(inscripcion_id=self.inscripcion.id, evaluacion_id=eval2.id, nota=20.0)
        db.session.add(nota2)
        db.session.commit()

        # Instanciar calculador
        calculador = CalculatorRiesgoIntrasemestral()
        resultado = calculador.calcular_riesgo_estudiante(self.estudiante.id, "2026-1", db)
        
        # Debiera ser SIN_RIESGO
        self.assertEqual(resultado['categoria'], 'SIN_RIESGO')
        self.assertLess(resultado['puntaje_riesgo'], 0.4)
        
    def test_calcular_riesgo_estudiante_en_alerta(self):
        """Verifica que un estudiante con bajo promedio de notas califica en riesgo alto/alerta"""
        # Crear un nuevo estudiante en riesgo
        estudiante_riesgo = Estudiante(
            codigo_estudiante="20260002",
            nombres="Pedro",
            apellidos="Pérez Gómez",
            email="pedro.perez@test.com",
            telefono="999888776",
            fecha_inscripcion=date(2026, 3, 15),
            activo=True
        )
        db.session.add(estudiante_riesgo)
        db.session.commit()
        
        inscripcion_riesgo = Inscripcion(
            estudiante_id=estudiante_riesgo.id,
            curso_id=self.curso.id,
            fecha_inscripcion=date(2026, 3, 16)
        )
        db.session.add(inscripcion_riesgo)
        db.session.commit()
        
        # Notas reprobatorias (promedio = 8.0)
        nota1 = Nota(inscripcion_id=inscripcion_riesgo.id, evaluacion_id=self.evaluacion.id, nota=8.0)
        db.session.add(nota1)
        
        # 80% inasistencia (4 de 5 clases ausente)
        for i in range(5):
            asistencia = Asistencia(
                inscripcion_id=inscripcion_riesgo.id,
                fecha=date(2026, 4, i+1),
                presente=(i == 0), # Solo presente la primera clase
                justificado=False
            )
            db.session.add(asistencia)
        
        db.session.commit()
        
        calculador = CalculatorRiesgoIntrasemestral()
        resultado = calculador.calcular_riesgo_estudiante(estudiante_riesgo.id, "2026-1", db)
        
        # Esperar alerta roja o amarilla
        self.assertIn(resultado['categoria'], ['ALERTA_AMARILLA', 'ALERTA_ROJA'])
        # El puntaje de riesgo debe ser alto
        self.assertGreater(resultado['puntaje_riesgo'], 0.4)

    def test_seguimiento_service_recalcular_riesgo_semestre(self):
        """Verifica que el servicio recalcula el riesgo de todos los estudiantes y persiste en BD"""
        # Ejecutar recalcular
        exito, msg = SeguimientoService.recalcular_riesgo_semestre("2026-1")
        self.assertTrue(exito)
        self.assertIn("Se procesaron 1 estudiantes", msg)
        
        # Verificar que se creó el registro de seguimiento en la base de datos
        seguimiento = SeguimientoRiesgo.query.filter_by(estudiante_id=self.estudiante.id, semestre="2026-1").first()
        self.assertIsNotNone(seguimiento)
        self.assertEqual(seguimiento.tendencia, 'ESTABLE')

    def test_seguimiento_service_actualizacion_tendencia(self):
        """Verifica que la tendencia cambie correctamente a SUBE o BAJA según cambie el puntaje de riesgo"""
        # 1. Crear un registro de seguimiento inicial con riesgo medio (0.5)
        seguimiento_inicial = SeguimientoRiesgo(
            estudiante_id=self.estudiante.id,
            semestre="2026-1",
            categoria_riesgo="ALERTA_AMARILLA",
            puntaje_riesgo=0.5,
            puntaje_anterior=0.0,
            tendencia='ESTABLE'
        )
        db.session.add(seguimiento_inicial)
        db.session.commit()
        
        # 2. Empeorar el rendimiento académico (añadir nota muy baja) para subir el riesgo
        eval2 = Evaluacion(curso_id=self.curso.id, nombre_evaluacion="PC2", peso=30.0)
        db.session.add(eval2)
        db.session.commit()
        
        # Nota baja: 05.0
        nota_baja = Nota(inscripcion_id=self.inscripcion.id, evaluacion_id=eval2.id, nota=5.0)
        db.session.add(nota_baja)
        
        # Inasistencias múltiples
        for i in range(10):
            asistencia = Asistencia(
                inscripcion_id=self.inscripcion.id,
                fecha=date(2026, 4, i+1),
                presente=False,
                justificado=False
            )
            db.session.add(asistencia)
            
        db.session.commit()
        
        # Recalcular usando el servicio
        exito, resultado = SeguimientoService.recalcular_estudiante(self.estudiante.id, "2026-1")
        self.assertTrue(exito)
        
        # 3. Obtener seguimiento actualizado
        seguimiento_act = SeguimientoRiesgo.query.filter_by(estudiante_id=self.estudiante.id, semestre="2026-1").first()
        self.assertEqual(seguimiento_act.tendencia, 'SUBE')
