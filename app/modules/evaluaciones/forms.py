# app/modules/evaluaciones/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class EvaluacionForm(FlaskForm):
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    nombre_evaluacion = StringField('Nombre de la Evaluación', 
                                   validators=[DataRequired(), Length(max=100)])
    tipo_evaluacion = SelectField('Tipo de Evaluación',
                                 choices=[
                                     ('', 'Seleccione tipo'),
                                     ('PARCIAL', 'Parcial'),
                                     ('QUIZ', 'Quiz'),
                                     ('TRABAJO', 'Trabajo'),
                                     ('PROYECTO', 'Proyecto'),
                                     ('LABORATORIO', 'Laboratorio'),
                                     ('EXAMEN_FINAL', 'Examen Final'),
                                     ('OTRO', 'Otro')
                                 ],
                                 validators=[DataRequired()])
    peso = DecimalField('Peso (%)', 
                       validators=[DataRequired(), NumberRange(min=0, max=100)],
                       places=2)
    fecha_creacion = DateField('Fecha de Creación', validators=[DataRequired()])
    submit = SubmitField('Guardar Evaluación')
    
    def __init__(self, *args, **kwargs):
        super(EvaluacionForm, self).__init__(*args, **kwargs)
        # Cargar cursos activos del periodo actual
        from app.models import Curso, Ciclo
        from app.services.config_service import cargar_configuracion
        
        config = cargar_configuracion()
        periodo_actual = config.get('semestre_actual')
        
        self.curso_id.choices = [
            (curso.id, f"{curso.codigo_curso} - {curso.nombre_curso} (Nivel {curso.semestre} | {curso.ciclo.codigo_ciclo})")
            for curso in Curso.query.join(Ciclo).filter(
                Curso.activo == True,
                Ciclo.codigo_ciclo == periodo_actual
            ).order_by('semestre', 'nombre_curso').all()
        ]

class NotaForm(FlaskForm):
    inscripcion_id = SelectField('Inscripción', coerce=int, validators=[DataRequired()])
    evaluacion_id = SelectField('Evaluación', coerce=int, validators=[DataRequired()])
    nota = DecimalField('Nota', 
                       validators=[DataRequired(), NumberRange(min=0, max=20)],
                       places=2)
    fecha_registro = DateField('Fecha de Registro', validators=[DataRequired()])
    observaciones = StringField('Observaciones', 
                               validators=[Optional(), Length(max=500)])
    submit = SubmitField('Guardar Nota')
    
    def __init__(self, *args, **kwargs):
        super(NotaForm, self).__init__(*args, **kwargs)
        # Importar modelos dentro del método para evitar importaciones circulares
        from app.models import Evaluacion, Inscripcion, Estudiante, Curso, Ciclo
        from app.services.config_service import cargar_configuracion
        
        config = cargar_configuracion()
        periodo_actual = config.get('semestre_actual')
        
        # Cargar evaluaciones activas del periodo actual
        self.evaluacion_id.choices = [
            (eval.id, f"{eval.nombre_evaluacion} - {eval.curso.nombre_curso}")
            for eval in Evaluacion.query.join(Curso).join(Ciclo).filter(
                Curso.activo == True,
                Ciclo.codigo_ciclo == periodo_actual
            ).order_by(Curso.nombre_curso, Evaluacion.nombre_evaluacion).all()
        ]
        
        # Cargar inscripciones activas del periodo actual
        self.inscripcion_id.choices = [
            (ins.id, f"{ins.estudiante.codigo_estudiante} - {ins.estudiante.nombres} {ins.estudiante.apellidos} - {ins.curso.nombre_curso}")
            for ins in Inscripcion.query.join(Estudiante).join(Curso).join(Ciclo).filter(
                Inscripcion.estado == 'ACTIVO',
                Estudiante.activo == True,
                Curso.activo == True,
                Ciclo.codigo_ciclo == periodo_actual
            ).order_by(Estudiante.apellidos, Curso.nombre_curso).all()
        ]