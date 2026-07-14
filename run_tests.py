# run_tests.py
import os
import sys
import unittest

# Asegurar que el directorio raíz está en el PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Forzar el entorno de testing
os.environ['FLASK_CONFIG'] = 'testing'
os.environ['FLASK_ENV'] = 'testing'

def run_suite():
    print("=== Iniciando la suite de pruebas del sistema Modulador ===\n")
    
    # Descubrir y cargar todas las pruebas de la carpeta 'tests'
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests', pattern='test_*.py')
    
    # Ejecutar las pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar código de salida adecuado
    if not result.wasSuccessful():
        print("\n[ERROR] Algunas pruebas fallaron. Revisa los detalles arriba.")
        sys.exit(1)
    else:
        print("\n[OK] ¡Todas las pruebas pasaron exitosamente!")
        sys.exit(0)

if __name__ == '__main__':
    run_suite()
