from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text('ALTER TABLE seguimiento_riesgo ADD COLUMN puntaje_anterior DECIMAL(5,2) DEFAULT 0.0'))
        print("Columna puntaje_anterior añadida.")
    except Exception as e:
        print(f"Error o ya existe puntaje_anterior: {e}")
        
    try:
        db.session.execute(text('ALTER TABLE seguimiento_riesgo ADD COLUMN tendencia VARCHAR(20) DEFAULT "ESTABLE"'))
        print("Columna tendencia añadida.")
    except Exception as e:
        print(f"Error o ya existe tendencia: {e}")
        
    db.session.commit()
    print("Migración completada.")
