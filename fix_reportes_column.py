# fix_reportes_column.py
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def fix_column():
    # Obtener variables de entorno directamente
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', '3306'))
    db_name = os.getenv('DB_NAME')
    
    if not db_name:
        print("❌ No se encontró configuración de MySQL en el archivo .env")
        print("Si está usando SQLite, no es necesario este cambio.")
        return

    try:
        print(f"Conectando a MySQL ({db_host}) para actualizar la tabla reportes...")
        
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name,
            port=db_port
        )
        
        with connection.cursor() as cursor:
            # Cambiar a LONGTEXT
            sql = "ALTER TABLE reportes MODIFY COLUMN contenido LONGTEXT;"
            cursor.execute(sql)
            print("✅ Columna 'contenido' actualizada exitosamente a LONGTEXT.")
            
        connection.commit()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {e}")
        print("\nPruebe ejecutar manualmente en su cliente MySQL:")
        print("ALTER TABLE reportes MODIFY COLUMN contenido LONGTEXT;")

if __name__ == "__main__":
    fix_column()
