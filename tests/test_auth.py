# tests/test_auth.py
from tests.test_base import BaseTestCase

class TestAuth(BaseTestCase):
    def test_login_exitoso(self):
        """Verifica que un usuario activo puede iniciar sesión con credenciales correctas"""
        response = self.login("docente_test@test.com", "password123")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bienvenido docente_test!", response.data)
        
    def test_login_contrasena_incorrecta(self):
        """Verifica que no se puede iniciar sesión con contraseña incorrecta"""
        response = self.login("docente_test@test.com", "wrongpassword")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Email o contrase\xc3\xb1a incorrectos", response.data)

    def test_login_usuario_inexistente(self):
        """Verifica que no se puede iniciar sesión con un correo no registrado"""
        response = self.login("no_existe@test.com", "password123")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Email o contrase\xc3\xb1a incorrectos", response.data)

    def test_login_usuario_inactivo(self):
        """Verifica que un usuario inactivo no puede iniciar sesión"""
        response = self.login("inactivo_test@test.com", "password123")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Cuenta desactivada. Contacte al administrador.", response.data)

    def test_logout_exitoso(self):
        """Verifica que un usuario puede cerrar sesión correctamente"""
        # Primero inicia sesión
        self.login("docente_test@test.com", "password123")
        # Luego cierra sesión
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Has cerrado sesi\xc3\xb3n correctamente.", response.data)

    def test_acceso_anonimo_protegido(self):
        """Verifica que las rutas protegidas redirigen al login cuando no se ha iniciado sesión"""
        response = self.client.get('/dashboard/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Por favor inicia sesi\xc3\xb3n para acceder a esta p\xc3\xa1gina.", response.data)
