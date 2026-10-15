# app/modules/cursos/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class CursoForm(FlaskForm):
    codigo_curso = StringField('Código del Curso', 
                              validators=[DataRequired(), Length(max=20)])
    nombre_curso = StringField('Nombre del Curso', 
                              validators=[DataRequired(), Length(max=100)])
    creditos = IntegerField('Créditos', 
                           validators=[Optional(), NumberRange(min=0, max=10)],
                           default=3)
    semestre = StringField('Semestre', 
                          validators=[DataRequired(), Length(max=10)])
    sesiones_por_semana = IntegerField('Sesiones por Semana', 
                                      validators=[DataRequired(), NumberRange(min=1, max=10)],
                                      default=2)
    total_sesiones = IntegerField('Total Sesiones Programadas (16 sem)', 
                                 validators=[Optional(), NumberRange(min=1, max=250)],
                                 description='Por defecto: 16 semanas × sesiones/semana')
    limite_inasistencia_porcentaje = DecimalField('Límite de Inasistencias (%)', 
                                                 validators=[Optional(), NumberRange(min=5, max=50)],
                                                 default=30.0)
    docente_id = SelectField('Docente Asignado', coerce=int, validators=[Optional()])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar Curso')