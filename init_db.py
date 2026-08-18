import os
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(text("SELECT 1 FROM estudiante LIMIT 1"))
        print("La base de datos ya está inicializada.")
    except Exception as e:
        print("Tablas no encontradas. Creando estructura de la base de datos...")
        db.session.rollback()
        db.create_all()
        print("Tablas creadas exitosamente.")
