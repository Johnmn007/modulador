import os
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(text("SELECT 1 FROM estudiante LIMIT 1"))
        print("La base de datos ya está inicializada.")
        
        # Parche para añadir la columna avatar si no existe (Railway)
        try:
            db.session.execute(text("ALTER TABLE usuarios ADD COLUMN avatar VARCHAR(255)"))
            db.session.commit()
            print("Columna 'avatar' añadida a 'usuarios'.")
        except Exception as e:
            db.session.rollback()
            print("La columna 'avatar' ya existe o hubo un error:", e)
            
    except Exception as e:
        print("Tablas no encontradas. Creando estructura de la base de datos...")
        db.session.rollback()
        db.create_all()
        print("Tablas creadas exitosamente.")
