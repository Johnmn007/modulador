# migrate_academic_attendance.py
"""
Migración para incorporar lógica académica de 16 semanas y límite de 30% de inasistencias (DPI)
en la base de datos remota de PostgreSQL.
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("ERROR: DATABASE_URL no encontrada en el entorno.")
    sys.exit(1)

# Mapeo de frecuencias conocidas de HORARIOS I SEMESTRE 2026
HORARIO_FRECUENCIA = {
    # 1 sesión por semana (16 clases programadas en 16 semanas)
    'CO105': 1, 'FDIA109': 1, 'O208': 1, 'EFSRT107': 1,
    'IPCO307-21': 1, 'IT308-21': 1, 'MS306-21': 1, 'ABD302-21': 1,
    'EFSRT301': 1, 'EFSRT501': 1, 'TBD402-21': 1, 'SI404-21': 1,
    'DG405-21': 1, 'TS403-21': 1,
    
    # 2 sesiones por semana (32 clases programadas en 16 semanas)
    'LP101': 2, 'FP202': 2, 'PCRETI103': 2,
    'PD303-21': 2, 'POO305-21': 2, 'POO305': 2,
    'CE606-21': 2, 'GAW502-21': 2,
    
    # 3 sesiones por semana (48 clases programadas en 16 semanas)
    'DMLP102': 3, 'PC304-21': 3, 'PC304': 3,
    'AG503-21': 3, 'DW504-21': 3, 'DW504': 3, 'DAM505-21': 3
}

def ejecutar_migracion():
    print("=" * 60)
    print("INICIANDO MIGRACIÓN: ASISTENCIA ACADÉMICA (16 SEMANAS / 30% DPI)")
    print(f"Destino remoto: {db_url.split('@')[1] if '@' in db_url else 'DB'}")
    print("=" * 60)

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    try:
        # 1. Agregar columnas si no existen
        print("\n1. Verificando/agregando columnas a la tabla 'cursos'...")
        cur.execute("""
            ALTER TABLE cursos 
            ADD COLUMN IF NOT EXISTS sesiones_por_semana INTEGER DEFAULT 2 NOT NULL;
        """)
        cur.execute("""
            ALTER TABLE cursos 
            ADD COLUMN IF NOT EXISTS total_sesiones INTEGER;
        """)
        cur.execute("""
            ALTER TABLE cursos 
            ADD COLUMN IF NOT EXISTS limite_inasistencia_porcentaje NUMERIC(4, 1) DEFAULT 30.0 NOT NULL;
        """)
        print("  -> Columnas 'sesiones_por_semana', 'total_sesiones', 'limite_inasistencia_porcentaje' listas.")

        # 2. Actualizar cursos conocidos con su frecuencia y total_sesiones
        print("\n2. Configurando frecuencias y totales de sesiones según horario...")
        actualizados = 0
        for codigo, ses_sem in HORARIO_FRECUENCIA.items():
            tot = ses_sem * 16
            cur.execute("""
                UPDATE cursos
                SET sesiones_por_semana = %s,
                    total_sesiones = %s,
                    limite_inasistencia_porcentaje = 30.0
                WHERE codigo_curso = %s;
            """, (ses_sem, tot, codigo))
            actualizados += cur.rowcount

        print(f"  -> {actualizados} registros actualizados según tabla de horarios.")

        # 3. Asignar valores por defecto a los cursos restantes que aún no tengan total_sesiones
        cur.execute("""
            UPDATE cursos
            SET sesiones_por_semana = COALESCE(sesiones_por_semana, 2),
                total_sesiones = COALESCE(total_sesiones, COALESCE(sesiones_por_semana, 2) * 16),
                limite_inasistencia_porcentaje = COALESCE(limite_inasistencia_porcentaje, 30.0)
            WHERE total_sesiones IS NULL;
        """)
        restantes = cur.rowcount
        print(f"  -> {restantes} cursos restantes configurados con valores estándar (16 semanas x sesiones).")

        conn.commit()
        print("\n3. Migración en BD remota completada con ÉXITO.")

        # 4. Mostrar resumen
        cur.execute("""
            SELECT sesiones_por_semana, total_sesiones, COUNT(*) 
            FROM cursos 
            GROUP BY sesiones_por_semana, total_sesiones
            ORDER BY sesiones_por_semana;
        """)
        print("\nResumen de cursos por distribución horaria:")
        for row in cur.fetchall():
            print(f"  - {row[0]} sesiones/sem (Total: {row[1]} clases) -> {row[2]} cursos")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR durante la migración: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    ejecutar_migracion()
