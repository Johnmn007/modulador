# tests/test_base.py
import unittest
import tempfile
import os
import json
from unittest.mock import patch
from datetime import datetime, date
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Usuario, Estudiante, Ciclo, Curso, Inscripcion, Evaluacion, Nota
from app.services.config_service import CONFIG_DEFAULT

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # 1. Crear archivo temporal de configuración para no dañar el desarrollo local
        self.temp_config_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_config_file.close() # Lo cerramos para permitir que el servicio lo abra
        
        # Mapear ruta de configuración al archivo temporal
        self.patcher = patch('app.services.config_service.get_config_path', return_value=self.temp_config_file.name)
        self.mock_get_config_path = self.patcher.start()
        
        # Escribir configuración por defecto
        config_data = CONFIG_DEFAULT.copy()
        config_data['semestre_actual'] = '2026-1'
        with open(self.temp_config_file.name, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
            
        # 2. Inicializar la app Flask en modo de prueba
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False  # Deshabilitar CSRF para simplificar los POST en pruebas
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 3. Cliente de prueba
        self.client = self.app.test_client()
        
        # 4. Configurar Base de Datos en Memoria
        db.create_all()
        
        # 5. Cargar datos semilla
        self.create_fixtures()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        self.patcher.stop()
        
        try:
            os.unlink(self.temp_config_file.name)
        except Exception:
            pass

    def create_fixtures(self):
        # Crear usuarios con diferentes roles
        # Nota: La contraseña encriptada es "password123"
        self.admin = Usuario(
            username="admin_test",
            email="admin_test@test.com",
            password_hash=generate_password_hash("password123"),
            rol="administrador",
            activo=True
        )
        self.coordinador = Usuario(
            username="coord_test",
            email="coord_test@test.com",
            password_hash=generate_password_hash("password123"),
            rol="coordinador",
            activo=True
        )
        self.docente = Usuario(
            username="docente_test",
            email="docente_test@test.com",
            password_hash=generate_password_hash("password123"),
            rol="docente",
            activo=True
        )
        self.usuario_inactivo = Usuario(
            username="inactivo_test",
            email="inactivo_test@test.com",
            password_hash=generate_password_hash("password123"),
            rol="docente",
            activo=False
        )
        db.session.add_all([self.admin, self.coordinador, self.docente, self.usuario_inactivo])
        db.session.commit()
        
        # Ciclo
        self.ciclo = Ciclo(
            nombre="Ciclo I 2026",
            codigo_ciclo="2026-1",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 30),
            activo=True
        )
        db.session.add(self.ciclo)
        db.session.commit()
        
        # Curso
        self.curso = Curso(
            codigo_curso="INF101",
            nombre_curso="Introducción a la Programación",
            creditos=4,
            semestre="2026-1",
            ciclo_id=self.ciclo.id,
            docente_id=self.docente.id,
            activo=True
        )
        db.session.add(self.curso)
        db.session.commit()
        
        # Estudiante
        self.estudiante = Estudiante(
            codigo_estudiante="20260001",
            nombres="Juan",
            apellidos="Pérez Gómez",
            email="juan.perez@test.com",
            telefono="999888777",
            fecha_inscripcion=date(2026, 3, 15),
            activo=True
        )
        db.session.add(self.estudiante)
        db.session.commit()
        
        # Inscripción
        self.inscripcion = Inscripcion(
            estudiante_id=self.estudiante.id,
            curso_id=self.curso.id,
            fecha_inscripcion=date(2026, 3, 16),
            estado="ACTIVO"
        )
        db.session.add(self.inscripcion)
        db.session.commit()
        
        # Evaluación
        self.evaluacion = Evaluacion(
            curso_id=self.curso.id,
            nombre_evaluacion="Práctica Calificada 1",
            tipo_evaluacion="PC",
            peso=20.0
        )
        db.session.add(self.evaluacion)
        db.session.commit()
        
        # Nota
        self.nota = Nota(
            inscripcion_id=self.inscripcion.id,
            evaluacion_id=self.evaluacion.id,
            nota=14.0,
            observaciones="Buen desempeño"
        )
        db.session.add(self.nota)
        db.session.commit()

    def login(self, email, password):
        return self.client.post('/auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
