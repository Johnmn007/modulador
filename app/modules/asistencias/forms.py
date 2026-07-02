# app/modules/asistencias/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from datetime import datetime, timezone

class AsistenciaForm(FlaskForm):
    inscripcion_id = SelectField('Inscripción', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha de Clase', validators=[DataRequired()], default=lambda: datetime.now(timezone.utc).date())
    presente = BooleanField('Presente', default=True)
    justificado = BooleanField('Justificado', default=False)
    observaciones = StringField('Observaciones', 
                               validators=[Optional(), Length(max=500)])
    submit = SubmitField('Registrar Asistencia')
    
    def __init__(self, *args, **kwargs):
        super(AsistenciaForm, self).__init__(*args, **kwargs)
        # Importar modelos dentro del método para evitar importaciones circulares
        from app.models import Inscripcion, Estudiante, Curso, Ciclo
        from app.services.config_service import cargar_configuracion
        
        config = cargar_configuracion()
        periodo_actual = config.get('semestre_actual')
        
        # Cargar inscripciones activas del periodo actual
        self.inscripcion_id.choices = [
            (ins.id, f"{ins.estudiante.codigo_estudiante} - {ins.estudiante.nombres} {ins.estudiante.apellidos} - {ins.curso.nombre_curso}")
            for ins in Inscripcion.query.join(Estudiante).join(Curso).join(Ciclo).filter(
                Inscripcion.estado == 'ACTIVO',
                Estudiante.activo == True,
                Curso.activo == True,
                Ciclo.codigo_ciclo == periodo_actual
            ).order_by(Curso.nombre_curso, Estudiante.apellidos).all()
        ]

class AsistenciaMasivaForm(FlaskForm):
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha de Clase', validators=[DataRequired()], default=lambda: datetime.now(timezone.utc).date())
    submit = SubmitField('Generar Formulario Masivo')
    
    def __init__(self, *args, **kwargs):
        super(AsistenciaMasivaForm, self).__init__(*args, **kwargs)
        # Importar modelos dentro del método
        from app.models import Curso, Ciclo
        from app.services.config_service import cargar_configuracion
        
        config = cargar_configuracion()
        periodo_actual = config.get('semestre_actual')
        
        # Cargar cursos activos del periodo actual
        self.curso_id.choices = [
            (curso.id, f"{curso.codigo_curso} - {curso.nombre_curso} (Nivel {curso.semestre} | {curso.ciclo.codigo_ciclo})")
            for curso in Curso.query.join(Ciclo).filter(
                Curso.activo == True,
                Ciclo.codigo_ciclo == periodo_actual
            ).order_by('semestre', 'nombre_curso').all()
        ]