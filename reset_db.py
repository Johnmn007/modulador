from app import create_app
from app.extensions import db
from app.models import Usuario
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def reset_database():
    app = create_app()
    with app.app_context():
        print("⏳ Borrando todas las tablas (esto puede tardar unos segundos)...")
        # Ignoramos la revisión de llaves foráneas para poder borrar las tablas sin problemas de dependencias en MySQL
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.drop_all()
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        
        print("🧹 Limpiando el historial de migraciones...")
        db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
        db.session.commit()
        
        print("🏗️ Recreando las tablas limpias...")
        db.create_all()
        
        print("👤 Creando usuario administrador por defecto...")
        admin = Usuario(
            username="admin",
            email="admin@sades.edu",
            password_hash=generate_password_hash("admin123"),
            rol="administrador",
            activo=True
        )
        db.session.add(admin)
        db.session.commit()
        
        print("\n" + "="*50)
        print("✅ BASE DE DATOS RESETEADA CON ÉXITO ✅")
        print("="*50)
        print("Puedes iniciar sesión con:")
        print("Email o Usuario: admin@sades.edu / admin")
        print("Password: admin123")
        print("="*50 + "\n")
        print("⚠️ IMPORTANTE: Para sincronizar las migraciones con esta base limpia, ejecuta:")
        print("1. flask db stamp head")
        print("\n")

if __name__ == '__main__':
    print("\n" + "!"*50)
    print("⚠️ ADVERTENCIA DE DESTRUCCIÓN MASIVA ⚠️")
    print("!"*50)
    confirm = input("Esto borrará TODOS los datos de tu base de datos actual para siempre.\n¿Estás seguro de que deseas continuar? (escribe 'SI' para confirmar): ")
    if confirm == 'SI':
        reset_database()
    else:
        print("Operación cancelada. Tus datos están a salvo.")
