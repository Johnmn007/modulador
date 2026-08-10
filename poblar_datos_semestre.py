"""
Script para poblar asistencias, evaluaciones y notas del semestre 2026-1
Basado en horarios del Excel "HORARIOS I SEMESTRE 2026"
"""
import random
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import (
    Curso, Inscripcion, Estudiante, Asistencia, Evaluacion, Nota, Ciclo
)

# ============================================================
# MAPEO DE CURSOS SEGUN HORARIO EXCEL
# format: codigo_curso: [dias_semana] (0=Lun, 1=Mar, 2=Mie, 3=Jue, 4=Vie)
# ============================================================
HORARIO_CURSOS = {
    # I CICLO
    'LP101':       [0, 3],           # Lenguaje de Programacion: Lunes, Jueves
    'CO105':       [0],              # Comunicacion Oral: Lunes
    'DMLP102':     [0, 2, 3],        # Diagnostico y Mantenimiento: Lunes, Miercoles, Jueves
    'FDIA109':     [1],              # Fund. IA: Martes
    'FP202':       [1, 4],           # Fund. Programacion: Martes, Viernes
    'O208':        [2],              # Ofimatica: Miercoles
    'EFSRT107':    [2],              # Exp. Formativas I: Miercoles
    'PCRETI103':   [1, 4],           # Planif. Redes: Martes, Viernes
    # III CICLO
    'PD303-21':    [0, 2],           # Prog. Distribuida: Lunes, Miercoles
    'IPCO307-21':  [1],              # Ingles Oral: Martes
    'POO305-21':   [2, 4],           # POO: Miercoles, Viernes
    'IT308-21':    [3],              # Innovacion Tecnologica: Jueves
    'MS306-21':    [0],              # Modelamiento Software: Lunes
    'ABD302-21':   [4],              # Arquitectura BD: Viernes
    'PC304-21':    [1, 3, 4],        # Prog. Concurrente: Martes, Jueves, Viernes
    'EFSRT301':    [3],              # Exp. Formativas III: Jueves
    # V CICLO
    'AG503-21':    [0, 1, 3],        # Animacion Grafica: Lunes, Martes, Jueves
    'CE606-21':    [1, 4],           # Comportamiento Etico: Martes, Viernes
    'EFSRT501':    [2],              # Exp. Formativas V: Miercoles
    'DW504-21':    [0, 2, 3],        # Diseno Web: Lunes, Miercoles, Jueves
    'GAW502-21':   [0, 2],           # Gestion Web: Lunes, Miercoles
    'DAM505-21':   [1, 3, 4],        # Diseno Apps Moviles: Martes, Jueves, Viernes
}

# Cursos que NO llevan evaluacion (Experiencias Formativas = evaluacion interna)
CURSOS_SIN_EVAL = {'EFSRT107', 'EFSRT301', 'EFSRT501'}

# Estructura de evaluacion estandar por curso
EVALUACION_PLANTILLA = [
    ('Parcial I',         'PARCIAL',       20.0),
    ('Trabajo I',         'TRABAJO',       15.0),
    ('Parcial II',        'PARCIAL',       20.0),
    ('Trabajo II',        'TRABAJO',       15.0),
    ('Examen Final',      'EXAMEN_FINAL',  25.0),
    ('Participacion',     'OTRO',           5.0),
]


def generar_fechas_clase(dias_semana, fecha_inicio, fecha_fin):
    """Genera todas las fechas de clase para los dias de la semana indicados"""
    fechas = []
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        if fecha_actual.weekday() in dias_semana:
            fechas.append(fecha_actual)
        fecha_actual += timedelta(days=1)
    return fechas


def crear_asistencias(app):
    """Crea asistencias masivas para todos los cursos"""
    print("\n" + "="*60)
    print("POBLANDO ASISTENCIAS")
    print("="*60)

    fecha_inicio = date(2026, 4, 6)   # Lunes 6 de abril
    fecha_fin = date(2026, 7, 31)     # Viernes 31 de julio

    total_asistencias = 0
    cursos_procesados = 0

    for codigo, dias in HORARIO_CURSOS.items():
        curso = Curso.query.filter_by(codigo_curso=codigo).first()
        if not curso:
            print(f"  [SKIP] Curso {codigo} no encontrado en BD")
            continue

        inscripciones = Inscripcion.query.filter_by(
            curso_id=curso.id, estado='ACTIVO'
        ).all()

        if not inscripciones:
            print(f"  [SKIP] Curso {codigo} ({curso.nombre_curso}) sin inscripciones activas")
            continue

        # Verificar si ya tiene asistencias
        asist_existentes = Asistencia.query.join(Inscripcion).filter(
            Inscripcion.curso_id == curso.id
        ).count()
        if asist_existentes > 0:
            print(f"  [SKIP] Curso {codigo} ya tiene {asist_existentes} asistencias")
            continue

        fechas_clase = generar_fechas_clase(dias, fecha_inicio, fecha_fin)
        count = 0

        for insc in inscripciones:
            for fecha in fechas_clase:
                asistencia = Asistencia(
                    inscripcion_id=insc.id,
                    fecha=fecha,
                    presente=random.random() < 0.82,  # 82% asistencia promedio
                    justificado=random.random() < 0.05,
                    observaciones=None
                )
                db.session.add(asistencia)
                count += 1

        total_asistencias += count
        cursos_procesados += 1
        print(f"  [OK] {codigo} ({curso.nombre_curso}): {len(inscripciones)} estudiantes x {len(fechas_clase)} clases = {count} asistencias")

    db.session.commit()
    print(f"\n  TOTAL: {cursos_procesados} cursos, {total_asistencias} asistencias creadas")
    return total_asistencias


def crear_evaluaciones(app):
    """Crea evaluaciones estandar para todos los cursos (excepto Exp. Formativas)"""
    print("\n" + "="*60)
    print("POBLANDO EVALUACIONES")
    print("="*60)

    total_evals = 0
    cursos_procesados = 0

    for codigo, dias in HORARIO_CURSOS.items():
        if codigo in CURSOS_SIN_EVAL:
            print(f"  [SKIP] {codigo} es Experiencia Formativa (sin evaluacion en sistema)")
            continue

        curso = Curso.query.filter_by(codigo_curso=codigo).first()
        if not curso:
            continue

        inscripciones = Inscripcion.query.filter_by(
            curso_id=curso.id, estado='ACTIVO'
        ).all()
        if not inscripciones:
            continue

        # Verificar si ya tiene evaluaciones
        evals_existentes = Evaluacion.query.filter_by(curso_id=curso.id).count()
        if evals_existentes > 0:
            print(f"  [SKIP] {codigo} ya tiene {evals_existentes} evaluaciones")
            continue

        for nombre, tipo, peso in EVALUACION_PLANTILLA:
            evaluacion = Evaluacion(
                curso_id=curso.id,
                nombre_evaluacion=nombre,
                tipo_evaluacion=tipo,
                peso=peso,
                fecha_creacion=date(2026, 4, 6)
            )
            db.session.add(evaluacion)
            total_evals += 1

        cursos_procesados += 1
        print(f"  [OK] {codigo} ({curso.nombre_curso}): {len(EVALUACION_PLANTILLA)} evaluaciones")

    db.session.commit()
    print(f"\n  TOTAL: {cursos_procesados} cursos, {total_evals} evaluaciones creadas")
    return total_evals


def crear_notas(app):
    """Crea notas con distribucion realista para todos los cursos"""
    print("\n" + "="*60)
    print("POBLANDO NOTAS")
    print("="*60)

    total_notas = 0
    cursos_procesados = 0

    for codigo, dias in HORARIO_CURSOS.items():
        if codigo in CURSOS_SIN_EVAL:
            continue

        curso = Curso.query.filter_by(codigo_curso=codigo).first()
        if not curso:
            continue

        evaluaciones = Evaluacion.query.filter_by(curso_id=curso.id).all()
        if not evaluaciones:
            continue

        inscripciones = Inscripcion.query.filter_by(
            curso_id=curso.id, estado='ACTIVO'
        ).all()
        if not inscripciones:
            continue

        # Verificar si ya tiene notas
        notas_existentes = Nota.query.join(Inscripcion).filter(
            Inscripcion.curso_id == curso.id
        ).count()
        if notas_existentes > 0:
            print(f"  [SKIP] {codigo} ya tiene {notas_existentes} notas")
            continue

        count = 0
        for insc in inscripciones:
            # Generar un "nivel" aleatorio para el estudiante (bueno, regular, malo)
            nivel = random.choices(
                ['excelente', 'bueno', 'regular', 'malo'],
                weights=[15, 45, 30, 10]
            )[0]

            for ev in evaluaciones:
                if nivel == 'excelente':
                    nota = round(random.uniform(16.0, 20.0), 1)
                elif nivel == 'bueno':
                    nota = round(random.uniform(13.0, 16.9), 1)
                elif nivel == 'regular':
                    nota = round(random.uniform(9.0, 12.9), 1)
                else:
                    nota = round(random.uniform(3.0, 8.9), 1)

                # Ajustar segun tipo de evaluacion
                if ev.tipo_evaluacion == 'EXAMEN_FINAL':
                    nota = max(0, nota - random.uniform(0, 2))  # Examenes un poco mas bajos
                elif ev.tipo_evaluacion == 'TRABAJO':
                    nota = min(20, nota + random.uniform(0, 2))  # Trabajos un poco mas altos

                nota = round(max(0, min(20, nota)), 1)

                nota_obj = Nota(
                    inscripcion_id=insc.id,
                    evaluacion_id=ev.id,
                    nota=nota,
                    fecha_registro=date(2026, 7, 15),
                    observaciones=None
                )
                db.session.add(nota_obj)
                count += 1

        total_notas += count
        cursos_procesados += 1
        print(f"  [OK] {codigo} ({curso.nombre_curso}): {len(inscripciones)} estudiantes x {len(evaluaciones)} evals = {count} notas")

    db.session.commit()
    print(f"\n  TOTAL: {cursos_procesados} cursos, {total_notas} notas creadas")
    return total_notas


def main():
    random.seed(42)  # Reproducible

    app = create_app()
    with app.app_context():
        print("\n" + "#"*60)
        print("# POBLADO DE DATOS - SEMESTRE I 2026")
        print("#"*60)

        asistencias = crear_asistencias(app)
        evaluaciones = crear_evaluaciones(app)
        notas = crear_notas(app)

        print("\n" + "#"*60)
        print("# RESUMEN FINAL")
        print("#"*60)
        print(f"  Asistencias creadas:  {asistencias}")
        print(f"  Evaluaciones creadas: {evaluaciones}")
        print(f"  Notas creadas:        {notas}")
        print("#"*60)


if __name__ == '__main__':
    main()
