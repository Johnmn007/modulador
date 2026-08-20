# app/modules/admin/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, DateField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional, Regexp


class ConfiguracionForm(FlaskForm):
    """Formulario de configuración del sistema"""
    umbral_amarillo = FloatField('Umbral Amarillo', validators=[
        DataRequired(message='El umbral amarillo es obligatorio'),
        NumberRange(min=0.1, max=1.0, message='Debe estar entre 0.1 y 1.0')
    ])
    umbral_rojo = FloatField('Umbral Rojo', validators=[
        DataRequired(message='El umbral rojo es obligatorio'),
        NumberRange(min=0.1, max=1.0, message='Debe estar entre 0.1 y 1.0')
    ])
    peso_rendimiento = FloatField('Peso Rendimiento', validators=[
        DataRequired(message='El peso es obligatorio'),
        NumberRange(min=0.0, max=1.0, message='Debe estar entre 0.0 y 1.0')
    ])
    peso_asistencia = FloatField('Peso Asistencia', validators=[
        DataRequired(message='El peso es obligatorio'),
        NumberRange(min=0.0, max=1.0, message='Debe estar entre 0.0 y 1.0')
    ])
    peso_distribucion = FloatField('Peso Distribución', validators=[
        DataRequired(message='El peso es obligatorio'),
        NumberRange(min=0.0, max=1.0, message='Debe estar entre 0.0 y 1.0')
    ])
    peso_historial = FloatField('Peso Historial', validators=[
        DataRequired(message='El peso es obligatorio'),
        NumberRange(min=0.0, max=1.0, message='Debe estar entre 0.0 y 1.0')
    ])
    nota_minima_aprobatoria = FloatField('Nota Mínima Aprobatoria', validators=[
        DataRequired(message='La nota mínima es obligatoria'),
        NumberRange(min=0.0, max=20.0, message='Debe estar entre 0.0 y 20.0')
    ])
    porcentaje_asistencia_minimo = FloatField('Porcentaje Asistencia Mínimo', validators=[
        DataRequired(message='El porcentaje es obligatorio'),
        NumberRange(min=0.0, max=100.0, message='Debe estar entre 0.0 y 100.0')
    ])


class CrearUsuarioForm(FlaskForm):
    """Formulario para crear usuario"""
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message='El nombre de usuario es obligatorio'),
        Length(min=3, max=80, message='Debe tener entre 3 y 80 caracteres'),
        Regexp(r'^[a-zA-ZáéíóúñÑÁÉÍÓÚüÜ\s]+$', message='Solo letras y espacios')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='Ingrese un email válido')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    confirm_password = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message='Confirme la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    rol = SelectField('Rol', choices=[
        ('docente', 'Docente'),
        ('coordinador', 'Coordinador'),
        ('administrador', 'Administrador')
    ], validators=[DataRequired(message='Seleccione un rol')])


class EditarUsuarioForm(FlaskForm):
    """Formulario para editar usuario"""
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message='El nombre de usuario es obligatorio'),
        Length(min=3, max=80, message='Debe tener entre 3 y 80 caracteres'),
        Regexp(r'^[a-zA-ZáéíóúñÑÁÉÍÓÚüÜ\s]+$', message='Solo letras y espacios')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='Ingrese un email válido')
    ])
    password = PasswordField('Nueva contraseña (dejar vacío para no cambiar)', validators=[
        Optional(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    confirm_password = PasswordField('Confirmar nueva contraseña', validators=[
        Optional(),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])


class CicloForm(FlaskForm):
    """Formulario para crear ciclo académico"""
    nombre = StringField('Nombre del ciclo', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=3, max=100, message='Debe tener entre 3 y 100 caracteres')
    ])
    codigo = StringField('Código del ciclo', validators=[
        DataRequired(message='El código es obligatorio'),
        Regexp(r'^\d{4}-[12]$', message='Formato inválido. Use: YYYY-N (ej: 2026-1)')
    ])
    fecha_inicio = DateField('Fecha de inicio', validators=[
        DataRequired(message='La fecha de inicio es obligatoria')
    ], format='%Y-%m-%d')
    fecha_fin = DateField('Fecha de fin', validators=[
        DataRequired(message='La fecha de fin es obligatoria')
    ], format='%Y-%m-%d')
