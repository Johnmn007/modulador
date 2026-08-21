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
        from app.models import Inscripcion, Estudiante, Curso
        from app.services.config_service import get_ciclo_activo
        
        ciclo = get_ciclo_activo()
        
        if ciclo:
            self.inscripcion_id.choices = [
                (ins.id, f"{ins.estudiante.codigo_estudiante} - {ins.estudiante.apellidos} {ins.estudiante.nombres} - {ins.curso.nombre_curso}")
                for ins in Inscripcion.query.join(Estudiante).join(Curso).filter(
                    Inscripcion.estado == 'ACTIVO',
                    Estudiante.activo == True,
                    Curso.activo == True,
                    Curso.ciclo_id == ciclo.id
                ).order_by(Curso.nombre_curso, Estudiante.apellidos, Estudiante.nombres).all()
            ]
        else:
            self.inscripcion_id.choices = []

class AsistenciaMasivaForm(FlaskForm):
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha de Clase', validators=[DataRequired()], default=lambda: datetime.now(timezone.utc).date())
    submit = SubmitField('Generar Formulario Masivo')
    
    def __init__(self, *args, **kwargs):
        super(AsistenciaMasivaForm, self).__init__(*args, **kwargs)
        from app.models import Curso
        from app.services.config_service import get_ciclo_activo
        
        ciclo = get_ciclo_activo()
        
        if ciclo:
            self.curso_id.choices = [
                (curso.id, f"{curso.codigo_curso} - {curso.nombre_curso} (Nivel {curso.semestre})")
                for curso in Curso.query.filter_by(activo=True, ciclo_id=ciclo.id).order_by('semestre', 'nombre_curso').all()
            ]
        else:
            self.curso_id.choices = []