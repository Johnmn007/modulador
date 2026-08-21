import sys
import os

from app import create_app
from app.extensions import db
from app.models import Estudiante

def main():
    app = create_app()
    with app.app_context():
        estudiantes = Estudiante.query.all()
        count = 0
        for est in estudiantes:
            # Intercambiamos nombres por apellidos
            temp = est.nombres
            est.nombres = est.apellidos
            est.apellidos = temp
            count += 1
        
        db.session.commit()
        print(f"Se han intercambiado nombres y apellidos de {count} estudiantes exitosamente en la base de datos.")

if __name__ == '__main__':
    main()
