# tests/test_indicadores_evaluaciones.py
import unittest
from tests.test_base import BaseTestCase
from app.extensions import db
from app.models import Curso, IndicadorLogro, Evaluacion, Nota, Estudiante, Inscripcion
from app.services.report_generator import ReportGenerator

class TestIndicadoresLogroEvaluaciones(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        # Clean up default evaluation from BaseTestCase to avoid interference
        Nota.query.delete()
        Evaluacion.query.delete()
        db.session.commit()

        # Create indicators for testing on self.curso
        self.il1 = IndicadorLogro(
            curso_id=self.curso.id,
            codigo='IL-01',
            nombre='Indicador 01',
            peso=50.0,
            orden=1
        )
        self.il2 = IndicadorLogro(
            curso_id=self.curso.id,
            codigo='IL-02',
            nombre='Indicador 02',
            peso=50.0,
            orden=2
        )
        db.session.add_all([self.il1, self.il2])
        db.session.commit()

    def test_suma_pesos_y_peso_disponible(self):
        """Verifica que el modelo calcula correctamente la suma de pesos y peso disponible"""
        ev1 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il1.id,
            nombre_evaluacion='Evaluacion 1',
            tipo_evaluacion='tarea',
            peso=40.0
        )
        ev2 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il1.id,
            nombre_evaluacion='Evaluacion 2',
            tipo_evaluacion='examen_parcial',
            peso=35.0
        )
        db.session.add_all([ev1, ev2])
        db.session.commit()

        self.assertAlmostEqual(self.il1.suma_pesos_evaluaciones, 75.0)
        self.assertAlmostEqual(self.il1.peso_disponible, 25.0)

    def test_validacion_peso_maximo_100_en_creacion(self):
        """Verifica que no se permita crear evaluaciones cuyo peso acumulado supere el 100%"""
        # Login as docente
        self.login('docente_test@test.com', 'password123')

        # Add evaluation with 70%
        ev1 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il1.id,
            nombre_evaluacion='Eval 70%',
            tipo_evaluacion='tarea',
            peso=70.0
        )
        db.session.add(ev1)
        db.session.commit()

        # Try to add evaluation with 40% (total 110% > 100%)
        response = self.client.post('/evaluaciones/crear', data={
            'curso_id': self.curso.id,
            'nombre_evaluacion': 'Eval Excedente',
            'tipo_evaluacion': 'PARCIAL',
            'indicador_id': self.il1.id,
            'peso': 40.0,
            'fecha_creacion': '2026-05-01'
        }, follow_redirects=True)

        self.assertIn('no puede sobrepasar el 100%', response.data.decode('utf-8'))
        
        # Verify it was not saved
        ev_excedente = Evaluacion.query.filter_by(nombre_evaluacion='Eval Excedente').first()
        self.assertIsNone(ev_excedente)

    def test_calculo_promedio_parcial_y_final_report_generator(self):
        """Verifica que el promedio parcial por indicador y promedio final sean precisos y no superen 20"""
        # Setup IL-01 with 2 evaluations (50% and 50%)
        ev1 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il1.id,
            nombre_evaluacion='IL1-E1',
            tipo_evaluacion='tarea',
            peso=50.0
        )
        ev2 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il1.id,
            nombre_evaluacion='IL1-E2',
            tipo_evaluacion='tarea',
            peso=50.0
        )
        # Setup IL-02 with 2 evaluations (40% and 60%)
        ev3 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il2.id,
            nombre_evaluacion='IL2-E1',
            tipo_evaluacion='examen_parcial',
            peso=40.0
        )
        ev4 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il2.id,
            nombre_evaluacion='IL2-E2',
            tipo_evaluacion='examen_final',
            peso=60.0
        )
        db.session.add_all([ev1, ev2, ev3, ev4])
        db.session.commit()

        # Add grades for self.inscripcion
        # IL-01: ev1 = 16, ev2 = 18 -> Promedio IL-01 = 16*0.5 + 18*0.5 = 17.0
        # IL-02: ev3 = 10, ev4 = 15 -> Promedio IL-02 = 10*0.4 + 15*0.6 = 4.0 + 9.0 = 13.0
        # Final: 17.0 * 50% + 13.0 * 50% = 8.5 + 6.5 = 15.0
        ins = self.inscripcion
        n1 = Nota(inscripcion_id=ins.id, evaluacion_id=ev1.id, nota=16.0)
        n2 = Nota(inscripcion_id=ins.id, evaluacion_id=ev2.id, nota=18.0)
        n3 = Nota(inscripcion_id=ins.id, evaluacion_id=ev3.id, nota=10.0)
        n4 = Nota(inscripcion_id=ins.id, evaluacion_id=ev4.id, nota=15.0)
        db.session.add_all([n1, n2, n3, n4])
        db.session.commit()

        rep = ReportGenerator()
        resultado = rep.generar_reporte_notas_curso(self.curso.id)
        consolidado = resultado['consolidado']
        self.assertEqual(len(consolidado), 1)

        est_data = consolidado[0]
        bloques = est_data['bloques_il']
        self.assertEqual(len(bloques), 2)
        
        # Verify Promedio IL-01
        self.assertEqual(bloques[0]['promedio_il'], 17.0)
        # Verify Promedio IL-02
        self.assertEqual(bloques[1]['promedio_il'], 13.0)
        # Verify Promedio Final
        self.assertEqual(est_data['promedio'], 15.0)
        self.assertLessEqual(est_data['promedio'], 20.0)
        self.assertGreaterEqual(est_data['promedio'], 0.0)
        self.assertEqual(est_data['condicion'], 'APROBADO')

    def test_procesar_masiva_asigna_cero_a_vacios(self):
        """Verifica que procesar_masiva asigne 0.0 a las casillas vacías cuando al menos un alumno fue calificado"""
        # Crear segundo estudiante en el curso
        est2 = Estudiante(
            codigo_estudiante="20260002",
            nombres="Maria",
            apellidos="Lopez",
            email="maria.lopez@test.com",
            activo=True
        )
        db.session.add(est2)
        db.session.commit()

        ins2 = Inscripcion(
            estudiante_id=est2.id,
            curso_id=self.curso.id,
            estado="ACTIVO"
        )
        db.session.add(ins2)
        db.session.commit()

        ev = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il1.id,
            nombre_evaluacion="Prueba Masiva",
            tipo_evaluacion="PARCIAL",
            peso=50.0
        )
        db.session.add(ev)
        db.session.commit()

        self.login('docente_test@test.com', 'password123')

        # Se califica al estudiante 1 con 18.0 y se deja vacío al estudiante 2
        response = self.client.post('/evaluaciones/notas/masiva/procesar', data={
            'evaluacion_id': ev.id,
            f'nota_{self.inscripcion.id}': '18.0',
            f'nota_{ins2.id}': ''  # Vacio
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verificar notas guardadas en BD
        nota1 = Nota.query.filter_by(inscripcion_id=self.inscripcion.id, evaluacion_id=ev.id).first()
        nota2 = Nota.query.filter_by(inscripcion_id=ins2.id, evaluacion_id=ev.id).first()

        self.assertIsNotNone(nota1)
        self.assertEqual(nota1.nota, 18.0)
        self.assertIsNotNone(nota2)
        self.assertEqual(nota2.nota, 0.0, "La nota vacia debe haberse guardado como 0.0")

    def test_evitar_falso_aprobado_alumnos_con_notas_vacias_en_reporte(self):
        """Verifica que un estudiante con notas vacias en evaluaciones ya evaluadas reciba 0 y no un falso aprobado"""
        # Crear segundo estudiante
        est2 = Estudiante(
            codigo_estudiante="20260003",
            nombres="Carlos",
            apellidos="Garcia",
            email="carlos.garcia@test.com",
            activo=True
        )
        db.session.add(est2)
        db.session.commit()

        ins2 = Inscripcion(
            estudiante_id=est2.id,
            curso_id=self.curso.id,
            estado="ACTIVO"
        )
        db.session.add(ins2)
        db.session.commit()

        # IL-01 tiene 2 evaluaciones de 50%
        ev1 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il1.id,
            nombre_evaluacion="Eval 1",
            tipo_evaluacion="PARCIAL",
            peso=50.0
        )
        ev2 = Evaluacion(
            curso_id=self.curso.id,
            indicador_id=self.il1.id,
            nombre_evaluacion="Eval 2",
            tipo_evaluacion="PARCIAL",
            peso=50.0
        )
        db.session.add_all([ev1, ev2])
        db.session.commit()

        # Estudiante 2 rinde ambas evaluaciones (15 y 16)
        n_est2_ev1 = Nota(inscripcion_id=ins2.id, evaluacion_id=ev1.id, nota=15.0)
        n_est2_ev2 = Nota(inscripcion_id=ins2.id, evaluacion_id=ev2.id, nota=16.0)
        
        # Estudiante 1 solo rindió Eval 1 (obtuvo 20), pero NUNCA rindió Eval 2 (está vacía/sin nota en BD)
        n_est1_ev1 = Nota(inscripcion_id=self.inscripcion.id, evaluacion_id=ev1.id, nota=20.0)

        db.session.add_all([n_est2_ev1, n_est2_ev2, n_est1_ev1])
        db.session.commit()

        rep = ReportGenerator()
        resultado = rep.generar_reporte_notas_curso(self.curso.id)
        consolidado = resultado['consolidado']

        est1_rep = next(c for c in consolidado if c['codigo'] == self.estudiante.codigo_estudiante)
        bloque_il1 = est1_rep['bloques_il'][0]

        # Dado que Eval 2 ya fue evaluada en el curso, el Estudiante 1 debe tener 0.0 en Eval 2
        # Promedio IL-01 = 20*0.5 + 0*0.5 = 10.0 (DESAPROBADO), NO 20.0 (falso aprobado)
        self.assertEqual(bloque_il1['promedio_il'], 10.0)
        self.assertEqual(bloque_il1['notas'][1], 0.0)

    def test_editar_peso_indicador_logro(self):
        """Verifica que un docente pueda editar el peso y datos de un indicador de logro"""
        self.login('docente_test@test.com', 'password123')
        
        response = self.client.post(f'/evaluaciones/indicador/{self.il1.id}/editar', data={
            'codigo': 'IL-01-MOD',
            'nombre': 'Indicador Modificado',
            'peso': '40.0',
            'orden': '1'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar en base de datos
        db.session.refresh(self.il1)
        self.assertEqual(self.il1.codigo, 'IL-01-MOD')
        self.assertEqual(self.il1.nombre, 'Indicador Modificado')
        self.assertAlmostEqual(float(self.il1.peso), 40.0)

    def test_actualizar_pesos_masivo_y_recalculo_consolidado(self):
        """Verifica que la actualización en bloque de pesos de indicadores afecte el promedio final"""
        self.login('docente_test@test.com', 'password123')
        
        # Crear evaluaciones con notas en IL1 e IL2
        ev1 = Evaluacion(curso_id=self.curso.id, indicador_id=self.il1.id, nombre_evaluacion='Ev 1', peso=100.0)
        ev2 = Evaluacion(curso_id=self.curso.id, indicador_id=self.il2.id, nombre_evaluacion='Ev 2', peso=100.0)
        db.session.add_all([ev1, ev2])
        db.session.commit()

        # Alumno saca 10 en IL1 y 20 en IL2
        n1 = Nota(inscripcion_id=self.inscripcion.id, evaluacion_id=ev1.id, nota=10.0)
        n2 = Nota(inscripcion_id=self.inscripcion.id, evaluacion_id=ev2.id, nota=20.0)
        db.session.add_all([n1, n2])
        db.session.commit()

        # Con pesos iniciales (50% y 50%): promedio final = 10*0.5 + 20*0.5 = 15.0
        rep = ReportGenerator()
        res_ini = rep.generar_reporte_notas_curso(self.curso.id)
        self.assertEqual(res_ini['consolidado'][0]['promedio'], 15.0)

        # Ahora actualizamos los pesos: IL1 = 20% y IL2 = 80%
        response = self.client.post(f'/evaluaciones/curso/{self.curso.id}/indicadores/actualizar-pesos', data={
            f'peso_{self.il1.id}': '20.0',
            f'peso_{self.il2.id}': '80.0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verificar nuevos pesos en BD
        db.session.refresh(self.il1)
        db.session.refresh(self.il2)
        self.assertAlmostEqual(float(self.il1.peso), 20.0)
        self.assertAlmostEqual(float(self.il2.peso), 80.0)

        # Con nuevos pesos: promedio final = 10*(0.2) + 20*(0.8) = 2.0 + 16.0 = 18.0
        res_nuevo = rep.generar_reporte_notas_curso(self.curso.id)
        self.assertEqual(res_nuevo['consolidado'][0]['promedio'], 18.0)

    def test_eliminar_indicador_con_y_sin_evaluaciones(self):
        """Verifica que solo se puedan eliminar indicadores que no tengan evaluaciones asociadas"""
        self.login('docente_test@test.com', 'password123')

        # il1 tiene una evaluación asignada
        ev = Evaluacion(curso_id=self.curso.id, indicador_id=self.il1.id, nombre_evaluacion='Ev IL1', peso=100.0)
        db.session.add(ev)
        db.session.commit()

        # Intentar eliminar il1 -> Debe fallar / rechazar la eliminación
        resp_bloqueado = self.client.post(f'/evaluaciones/indicador/{self.il1.id}/eliminar', follow_redirects=True)
        self.assertEqual(resp_bloqueado.status_code, 200)
        self.assertIsNotNone(IndicadorLogro.query.get(self.il1.id))

        # il2 no tiene evaluaciones -> Debe eliminarse exitosamente
        resp_exito = self.client.post(f'/evaluaciones/indicador/{self.il2.id}/eliminar', follow_redirects=True)
        self.assertEqual(resp_exito.status_code, 200)
        self.assertIsNone(IndicadorLogro.query.get(self.il2.id))

    def test_generar_excel_notas_curso_service(self):
        """Verifica que ReportGenerator genera un buffer Excel (.xlsx) estructurado correctamente"""
        import openpyxl

        ev1 = Evaluacion(curso_id=self.curso.id, indicador_id=self.il1.id, nombre_evaluacion='Ev 1', peso=100.0)
        ev2 = Evaluacion(curso_id=self.curso.id, indicador_id=self.il2.id, nombre_evaluacion='Ev 2', peso=100.0)
        db.session.add_all([ev1, ev2])
        db.session.commit()

        # Registrar nota
        nota = Nota(inscripcion_id=self.inscripcion.id, evaluacion_id=ev1.id, nota=16.0)
        db.session.add(nota)
        db.session.commit()

        rep = ReportGenerator()
        excel_buffer = rep.generar_excel_notas_curso(self.curso.id)
        self.assertIsNotNone(excel_buffer)

        # Leer con openpyxl para verificar integridad
        wb = openpyxl.load_workbook(excel_buffer)
        self.assertTrue(len(wb.sheetnames) > 0)
        ws = wb.active
        # Celda A1 contiene el encabezado institucional
        self.assertIn("SADES", ws['A1'].value)
        self.assertIn("ACTA CONSOLIDADA", ws['A2'].value)

    def test_descargar_excel_notas_curso_routes(self):
        """Verifica que las rutas de descarga en Excel responden con código 200 y el mimetype correcto"""
        self.login('docente_test@test.com', 'password123')

        # 1. Petición POST a /reportes/notas/curso con formato=excel
        resp_post = self.client.post('/reportes/notas/curso', data={
            'curso_id': self.curso.id,
            'formato': 'excel'
        })
        self.assertEqual(resp_post.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resp_post.content_type)
        self.assertIn('.xlsx', resp_post.headers.get('Content-Disposition', ''))

        # 2. Petición GET a la ruta directa /reportes/notas/curso/<id>/excel
        resp_get = self.client.get(f'/reportes/notas/curso/{self.curso.id}/excel')
        self.assertEqual(resp_get.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resp_get.content_type)
        self.assertIn('.xlsx', resp_get.headers.get('Content-Disposition', ''))



