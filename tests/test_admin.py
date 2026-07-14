# tests/test_admin.py
import json
from tests.test_base import BaseTestCase
from app.services.config_service import cargar_configuracion
from app.models import Usuario

class TestAdmin(BaseTestCase):
    def test_acceso_admin_exitoso(self):
        """Verifica que el administrador puede acceder a la configuración"""
        self.login("admin_test@test.com", "password123")
        response = self.client.get('/admin/configuracion')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Configuraci\xc3\xb3n", response.data)

    def test_bloqueo_acceso_docente(self):
        """Verifica que un docente es rechazado al intentar acceder al panel de administración"""
        self.login("docente_test@test.com", "password123")
        response = self.client.get('/admin/configuracion', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No tiene permisos para acceder a esta secci\xc3\xb3n", response.data)

    def test_actualizar_configuracion_exitosa(self):
        """Verifica que se puede actualizar la configuración con parámetros válidos"""
        self.login("admin_test@test.com", "password123")
        response = self.client.post('/admin/configuracion', data={
            'umbral_amarillo': '0.3',
            'umbral_rojo': '0.6',
            'peso_rendimiento': '0.30',
            'peso_asistencia': '0.30',
            'peso_distribucion': '0.20',
            'peso_historial': '0.20',
            'semestre_actual': '2026-2',
            'nota_minima_aprobatoria': '12.5',
            'porcentaje_asistencia_minimo': '75.0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Configuraci\xc3\xb3n institucional actualizada exitosamente", response.data)
        
        # Verificar que se guardó en el archivo JSON mockeado
        config = cargar_configuracion()
        self.assertEqual(config['umbral_amarillo'], 0.3)
        self.assertEqual(config['peso_rendimiento'], 0.30)
        self.assertEqual(config['semestre_actual'], '2026-2')

    def test_actualizar_configuracion_pesos_incorrectos(self):
        """Verifica que la configuración es rechazada si los pesos no suman 1.0"""
        self.login("admin_test@test.com", "password123")
        # Suma de pesos = 0.3 + 0.3 + 0.3 + 0.3 = 1.2
        response = self.client.post('/admin/configuracion', data={
            'umbral_amarillo': '0.4',
            'umbral_rojo': '0.7',
            'peso_rendimiento': '0.30',
            'peso_asistencia': '0.30',
            'peso_distribucion': '0.30',
            'peso_historial': '0.30',
            'semestre_actual': '2026-1',
            'nota_minima_aprobatoria': '12.0',
            'porcentaje_asistencia_minimo': '70.0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Los pesos de los factores deben sumar exactamente 1.0", response.data)

    def test_cambiar_semestre_exitoso(self):
        """Verifica que el administrador puede cambiar solo el semestre actual"""
        self.login("admin_test@test.com", "password123")
        response = self.client.post('/admin/cambiar-semestre', data={
            'semestre': '2026-2'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Semestre cambiado exitosamente a 2026-2", response.data)
        
        config = cargar_configuracion()
        self.assertEqual(config['semestre_actual'], '2026-2')

    def test_cambiar_semestre_invalido(self):
        """Verifica que se rechaza un formato inválido de semestre"""
        self.login("admin_test@test.com", "password123")
        response = self.client.post('/admin/cambiar-semestre', data={
            'semestre': 'semestre-2026'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Formato de semestre inv\xc3\xa1lido", response.data)

    def test_creacion_usuario_exitoso(self):
        """Verifica que el administrador puede crear nuevos usuarios"""
        self.login("admin_test@test.com", "password123")
        response = self.client.post('/admin/usuarios/crear', data={
            'username': 'nuevo_docente',
            'email': 'nuevo@test.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'rol': 'docente'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Usuario creado exitosamente", response.data)
        
        # Verificar en base de datos
        usuario = Usuario.query.filter_by(username='nuevo_docente').first()
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.rol, 'docente')
