import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'seguimiento_estudiantil')

try:
    conn = psycopg2.connect(
        dbname='postgres',
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    
    if not exists:
        print(f"Creando base de datos: {db_name}...")
        cursor.execute(f"CREATE DATABASE {db_name};")
        print("Base de datos creada exitosamente.")
    else:
        print(f"La base de datos {db_name} ya existe.")
        
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error al conectar o crear la base de datos: {e}")
