# app/modules/evaluaciones/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class IndicadorForm(FlaskForm):
    codigo = StringField('Código del Indicador', 
                         validators=[DataRequired(message="Ingrese código (ej: IL-01)"), Length(max=20)])
    nombre = StringField('Nombre del Indicador', 
                         validators=[DataRequired(message="Ingrese nombre del indicador"), Length(max=200)])
    peso = DecimalField('Peso en el Curso (%)', 
                       validators=[DataRequired(message="Ingrese el peso del indicador"), NumberRange(min=0.1, max=100)],
                       places=2)
    orden = DecimalField('Orden', default=1, places=0)
    submit = SubmitField('Guardar Indicador')

class EvaluacionForm(FlaskForm):
    curso_id = SelectField('Curso / Unidad Didáctica', coerce=int, validators=[DataRequired(message="Seleccione un curso")])
    indicador_id = SelectField('Indicador de Logro', coerce=int, validators=[DataRequired(message="Seleccione un Indicador de Logro")])
    nombre_evaluacion = StringField('Nombre de la Evaluación', 
                                   validators=[DataRequired(message="Ingrese nombre de la evaluación"), Length(max=100)])
    tipo_evaluacion = SelectField('Tipo de Evaluación',
                                 choices=[
                                     ('', 'Seleccione tipo'),
                                     ('PARCIAL', 'Examen Parcial / Evaluación'),
                                     ('QUIZ', 'Quiz / Control'),
                                     ('TRABAJO', 'Tarea Académica / Trabajo'),
                                     ('PROYECTO', 'Proyecto'),
                                     ('LABORATORIO', 'Evaluación Práctica / Laboratorio'),
                                     ('INTERVENCION', 'Intervención Activa'),
                                     ('EXAMEN_FINAL', 'Examen Final'),
                                     ('OTRO', 'Otro')
                                 ],
                                 validators=[DataRequired(message="Seleccione el tipo de evaluación")])
    peso = DecimalField('Peso (%) en este Indicador', 
                       validators=[DataRequired(message="Ingrese el peso"), NumberRange(min=0.1, max=100, message="El peso debe ser entre 0.1 y 100")],
                       places=2)
    fecha_creacion = DateField('Fecha de Creación', validators=[DataRequired(message="Ingrese la fecha")])
    submit = SubmitField('Guardar Evaluación')
    
    def __init__(self, *args, **kwargs):
        super(EvaluacionForm, self).__init__(*args, **kwargs)
        from app.models import Curso, IndicadorLogro
        from app.services.config_service import get_ciclo_activo
        from flask_login import current_user
        
        ciclo = get_ciclo_activo()
        
        if ciclo:
            query = Curso.query.filter_by(activo=True, ciclo_id=ciclo.id)
            if current_user.rol in ('docente', 'coordinador'):
                query = query.filter_by(docente_id=current_user.id)
                
            self.curso_id.choices = [
                (curso.id, f"{curso.codigo_curso} - {curso.nombre_curso} (Nivel {curso.semestre})")
                for curso in query.order_by('semestre', 'nombre_curso').all()
            ]
        else:
            self.curso_id.choices = []

        # Determinar curso seleccionado para poblar los indicadores correspondientes
        selected_curso_id = None
        if self.curso_id.data:
            selected_curso_id = self.curso_id.data
        elif 'curso_id' in kwargs and kwargs['curso_id']:
            selected_curso_id = kwargs['curso_id']
        elif len(self.curso_id.choices) > 0:
            selected_curso_id = self.curso_id.choices[0][0]

        if selected_curso_id:
            indicadores = IndicadorLogro.query.filter_by(curso_id=selected_curso_id).order_by(IndicadorLogro.orden).all()
            self.indicador_id.choices = [
                (il.id, f"{il.codigo}: {il.nombre} ({il.peso_disponible:.1f}% disponible)")
                for il in indicadores
            ]
        else:
            self.indicador_id.choices = []

class NotaForm(FlaskForm):
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    estudiante_id = SelectField('Estudiante', coerce=int, validators=[DataRequired()])
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
        from app.models import Curso, Estudiante, Evaluacion, Inscripcion
        from app.services.config_service import get_ciclo_activo
        from flask_login import current_user
        
        ciclo = get_ciclo_activo()
        
        if ciclo:
            query = Curso.query.filter_by(activo=True, ciclo_id=ciclo.id)
            if current_user.rol in ('docente', 'coordinador'):
                query = query.filter_by(docente_id=current_user.id)
                
            self.curso_id.choices = [
                (curso.id, f"{curso.codigo_curso} - {curso.nombre_curso} (Nivel {curso.semestre})")
                for curso in query.order_by('semestre', 'nombre_curso').all()
            ]
        else:
            self.curso_id.choices = []
        
        self.estudiante_id.choices = []
        self.evaluacion_id.choices = []