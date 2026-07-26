# app/modules/inscripciones/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, SubmitField
from wtforms.validators import DataRequired
from app.models import Estudiante, Curso

class InscripcionForm(FlaskForm):
    estudiante_id = SelectField('Estudiante', coerce=int, validators=[DataRequired()])
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    fecha_inscripcion = DateField('Fecha de Inscripción', validators=[DataRequired()])
    estado = SelectField('Estado', 
                        choices=[
                            ('ACTIVO', 'Activo'),
                            ('INACTIVO', 'Inactivo'), 
                            ('RETIRADO', 'Retirado'),
                            ('APROBADO', 'Aprobado'),
                            ('REPROBADO', 'Reprobado')
                        ],
                        validators=[DataRequired()])
    submit = SubmitField('Guardar Inscripción')
    
    def __init__(self, *args, **kwargs):
        super(InscripcionForm, self).__init__(*args, **kwargs)
        # Cargar estudiantes activos
        self.estudiante_id.choices = [(0, '')] + [
            (est.id, f"{est.codigo_estudiante} - {est.nombres} {est.apellidos}")
            for est in Estudiante.query.filter_by(activo=True).order_by('apellidos').all()
        ]
        from app.services.config_service import cargar_configuracion
        from app.models import Ciclo
        
        config = cargar_configuracion()
        periodo_actual = config.get('semestre_actual')
        
        # Cargar cursos activos del periodo actual
        self.curso_id.choices = [(0, '')] + [
            (curso.id, f"{curso.codigo_curso} - {curso.nombre_curso} (Nivel {curso.semestre} | {curso.ciclo.codigo_ciclo})")
            for curso in Curso.query.join(Ciclo).filter(
                Curso.activo.is_(True),
                Ciclo.codigo_ciclo == periodo_actual
            ).order_by('semestre', 'nombre_curso').all()
        ]
        
# ------------------------------------------------------------------
# MATRICULAS MASIVAS    
# app/modules/inscripciones/forms.py - AÑADIR
class MatriculaMasivaForm(FlaskForm):
    semestre = SelectField('Semestre', coerce=str, validators=[DataRequired()])
    grupo_estudiantes = SelectField('Grupo de Estudiantes', 
        choices=[
            ('todos', 'Todos los estudiantes activos'),
            ('nuevos', 'Solo estudiantes nuevos en el semestre')
        ], validators=[DataRequired()])
    fecha_inscripcion = DateField('Fecha de Matrícula', validators=[DataRequired()])
    estado = SelectField('Estado Inicial',
        choices=[
            ('ACTIVO', 'Activo'),
            ('OBSERVADO', 'Observado')
        ], default='ACTIVO')
    submit = SubmitField('Generar Matrícula Masiva')
    
    def __init__(self, *args, **kwargs):
        super(MatriculaMasivaForm, self).__init__(*args, **kwargs)
        # Importar la aplicación para acceder a la BD
        from flask import current_app
        
        with current_app.app_context():
            try:
                from app.extensions import db
                semestres = db.session.query(Curso.semestre)\
                    .filter(Curso.activo.is_(True))\
                    .distinct()\
                    .order_by(Curso.semestre)\
                    .all()
                
                self.semestre.choices = [(sem[0], f'Semestre {sem[0]}') for sem in semestres]
                
                if not self.semestre.choices:
                    self.semestre.choices = [('', 'No hay cursos activos')]
                    
            except Exception:
                # Fallback a semestres por defecto
                self.semestre.choices = [
                    ('I', 'Semestre I'), ('II', 'Semestre II'), ('III', 'Semestre III'),
                    ('IV', 'Semestre IV'), ('V', 'Semestre V'), ('VI', 'Semestre VI')
                ]

# ------------------------------------------------------------------
# MATRICULA POR CICLO
# app/modules/inscripciones/forms.py - AÑADIR
class MatriculaPorCicloForm(FlaskForm):
    estudiante_id = SelectField('Estudiante', coerce=int, validators=[DataRequired()])
    semestre = SelectField('Ciclo / Semestre', coerce=str, validators=[DataRequired()])
    fecha_inscripcion = DateField('Fecha de Matrícula', validators=[DataRequired()])
    estado = SelectField('Estado Inicial',
        choices=[
            ('ACTIVO', 'Activo'),
            ('OBSERVADO', 'Observado')
        ], default='ACTIVO')
    submit = SubmitField('Generar Matrícula por Ciclo')
    
    def __init__(self, *args, **kwargs):
        super(MatriculaPorCicloForm, self).__init__(*args, **kwargs)
        from flask import current_app
        from app.extensions import db
        
        # Cargar estudiantes activos
        self.estudiante_id.choices = [(0, '')] + [
            (est.id, f"{est.codigo_estudiante} - {est.nombres} {est.apellidos}")
            for est in Estudiante.query.filter_by(activo=True).order_by('apellidos').all()
        ]
        
        with current_app.app_context():
            try:
                semestres = db.session.query(Curso.semestre)\
                    .filter(Curso.activo.is_(True))\
                    .distinct()\
                    .order_by(Curso.semestre)\
                    .all()
                
                self.semestre.choices = [('', '-- Seleccione un ciclo --')] + [(sem[0], f'Semestre {sem[0]}') for sem in semestres]
                
                if len(self.semestre.choices) == 1:
                    self.semestre.choices = [('', 'No hay cursos activos')]
                    
            except Exception:
                # Fallback
                self.semestre.choices = [
                    ('', '-- Seleccione un ciclo --'),
                    ('I', 'Semestre I'), ('II', 'Semestre II'), ('III', 'Semestre III'),
                    ('IV', 'Semestre IV'), ('V', 'Semestre V'), ('VI', 'Semestre VI')
                ]