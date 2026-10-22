# migrate_indicadores_logro.py
"""
Migración para incorporar el modelo de Indicadores de Logro (IL)
en la base de datos PostgreSQL remota.
"""
import os
import sys
import re
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("ERROR: DATABASE_URL no encontrada en el entorno.")
    sys.exit(1)

def ejecutar_migracion():
    print("=" * 60)
    print("INICIANDO MIGRACIÓN: INDICADORES DE LOGRO (IL)")
    print(f"Destino remoto: {db_url.split('@')[1] if '@' in db_url else 'DB'}")
    print("=" * 60)

    conn = psycopg2.connect(db_url)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 1. Crear tabla indicadores_logro si no existe
        print("\n1. Verificando / creando tabla 'indicadores_logro'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS indicadores_logro (
                id SERIAL PRIMARY KEY,
                curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
                codigo VARCHAR(20) NOT NULL,
                nombre VARCHAR(200) NOT NULL,
                peso NUMERIC(5, 2) DEFAULT 0.0 NOT NULL,
                orden INTEGER DEFAULT 1 NOT NULL,
                fecha_creacion DATE DEFAULT CURRENT_DATE,
                CONSTRAINT uq_curso_indicador UNIQUE (curso_id, codigo)
            );
        """)
        print("  -> Tabla 'indicadores_logro' lista.")

        # 2. Agregar columna indicador_id a la tabla evaluaciones
        print("\n2. Verificando / agregando columna 'indicador_id' a tabla 'evaluaciones'...")
        cur.execute("""
            ALTER TABLE evaluaciones 
            ADD COLUMN IF NOT EXISTS indicador_id INTEGER REFERENCES indicadores_logro(id) ON DELETE SET NULL;
        """)
        print("  -> Columna 'indicador_id' lista en 'evaluaciones'.")

        # 3. Analizar evaluaciones existentes para extraer Indicadores de Logro
        print("\n3. Migrando y vinculando evaluaciones existentes a Indicadores de Logro...")
        cur.execute("""
            SELECT id, curso_id, nombre_evaluacion, peso 
            FROM evaluaciones 
            ORDER BY curso_id, id;
        """)
        evaluaciones = cur.fetchall()

        # Agrupar por curso
        cursos_evals = {}
        for ev in evaluaciones:
            c_id = ev['curso_id']
            if c_id not in cursos_evals:
                cursos_evals[c_id] = []
            cursos_evals[c_id].append(ev)

        indicadores_creados = 0
        evaluaciones_vinculadas = 0

        # Patrón para detectar IL01, IL-01, IL1, etc.
        il_pattern = re.compile(r'IL[-_\s]?0?([1-9])', re.IGNORECASE)

        for curso_id, ev_list in cursos_evals.items():
            # Detectar si hay códigos IL en los nombres
            codigos_detectados = set()
            mapa_ev_il = {}

            for ev in ev_list:
                m = il_pattern.search(ev['nombre_evaluacion'])
                if m:
                    num_il = int(m.group(1))
                    codigo_il = f"IL-{num_il:02d}"
                    codigos_detectados.add((num_il, codigo_il))
                    mapa_ev_il[ev['id']] = codigo_il

            # Si se detectaron indicadores en el curso
            if codigos_detectados:
                # Ordenar por número
                sorted_ils = sorted(list(codigos_detectados), key=lambda x: x[0])
                num_indicadores = len(sorted_ils)
                peso_base = round(100.0 / num_indicadores, 2)
                
                for idx, (num_il, codigo_il) in enumerate(sorted_ils, 1):
                    # El último puede ajustar para sumar exactamente 100
                    peso_il = peso_base if idx < num_indicadores else round(100.0 - peso_base * (num_indicadores - 1), 2)
                    nombre_il = f"Indicador de Logro {num_il:02d}"

                    # Insertar o recuperar IndicadorLogro
                    cur.execute("""
                        INSERT INTO indicadores_logro (curso_id, codigo, nombre, peso, orden)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (curso_id, codigo) DO UPDATE 
                        SET peso = EXCLUDED.peso, nombre = EXCLUDED.nombre
                        RETURNING id;
                    """, (curso_id, codigo_il, nombre_il, peso_il, num_il))
                    il_id = cur.fetchone()['id']
                    indicadores_creados += 1

                    # Vincular evaluaciones de este IL
                    for ev in ev_list:
                        if mapa_ev_il.get(ev['id']) == codigo_il:
                            cur.execute("""
                                UPDATE evaluaciones 
                                SET indicador_id = %s 
                                WHERE id = %s;
                            """, (il_id, ev['id']))
                            evaluaciones_vinculadas += 1

            else:
                # Curso con evaluaciones tradicionales (sin IL explícito)
                # Crear un único indicador por defecto IL-01 con peso 100%
                cur.execute("""
                    INSERT INTO indicadores_logro (curso_id, codigo, nombre, peso, orden)
                    VALUES (%s, 'IL-01', 'Indicador de Logro 01', 100.0, 1)
                    ON CONFLICT (curso_id, codigo) DO NOTHING
                    RETURNING id;
                """, (curso_id,))
                row = cur.fetchone()
                if not row:
                    cur.execute("SELECT id FROM indicadores_logro WHERE curso_id = %s AND codigo = 'IL-01';", (curso_id,))
                    row = cur.fetchone()
                il_id = row['id']
                indicadores_creados += 1

                for ev in ev_list:
                    cur.execute("""
                        UPDATE evaluaciones 
                        SET indicador_id = %s 
                        WHERE id = %s AND indicador_id IS NULL;
                    """, (il_id, ev['id']))
                    evaluaciones_vinculadas += 1

        conn.commit()
        print(f"\n3. Migración completada exitosamente:")
        print(f"  -> {indicadores_creados} Indicadores de Logro creados/actualizados.")
        print(f"  -> {evaluaciones_vinculadas} Evaluaciones vinculadas a sus respectivos Indicadores.")

        # Verificar resultados para Curso 98
        cur.execute("""
            SELECT il.codigo, il.nombre, il.peso as peso_il, 
                   COUNT(e.id) as num_evaluaciones, 
                   COALESCE(SUM(e.peso), 0) as suma_peso_evaluaciones
            FROM indicadores_logro il
            LEFT JOIN evaluaciones e ON e.indicador_id = il.id
            WHERE il.curso_id = 98
            GROUP BY il.id, il.codigo, il.nombre, il.peso
            ORDER BY il.orden;
        """)
        rows = cur.fetchall()
        print("\nVerificación en Curso 98 (Taller de Base de Datos):")
        for r in rows:
            print(f"  * {r['codigo']} ({r['nombre']}): Peso IL={r['peso_il']}% | {r['num_evaluaciones']} Evaluaciones | Suma pesos evals={r['suma_peso_evaluaciones']}%")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR durante la migración: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    ejecutar_migracion()
