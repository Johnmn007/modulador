# app/modules/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message='El correo es obligatorio'),
        Email(message='Ingrese un correo válido')
    ])
    submit = SubmitField('Enviar enlace de recuperación')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    confirm_password = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message='Confirme la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Restablecer contraseña')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña actual', validators=[
        DataRequired(message='Ingrese su contraseña actual')
    ])
    new_password = PasswordField('Nueva contraseña', validators=[
        DataRequired(message='La nueva contraseña es obligatoria'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    confirm_password = PasswordField('Confirmar nueva contraseña', validators=[
        DataRequired(message='Confirme la nueva contraseña'),
        EqualTo('new_password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Actualizar contraseña')

class PreguntaSeguridadForm(FlaskForm):
    """Formulario para configurar preguntas de seguridad"""
    pregunta_1 = StringField('Pregunta 1', validators=[
        DataRequired(message='La pregunta es obligatoria'),
        Length(min=5, max=200, message='La pregunta debe tener entre 5 y 200 caracteres')
    ])
    respuesta_1 = StringField('Respuesta 1', validators=[
        DataRequired(message='La respuesta es obligatoria'),
        Length(min=2, max=100, message='La respuesta debe tener entre 2 y 100 caracteres')
    ])
    pregunta_2 = StringField('Pregunta 2', validators=[
        DataRequired(message='La pregunta es obligatoria'),
        Length(min=5, max=200, message='La pregunta debe tener entre 5 y 200 caracteres')
    ])
    respuesta_2 = StringField('Respuesta 2', validators=[
        DataRequired(message='La respuesta es obligatoria'),
        Length(min=2, max=100, message='La respuesta debe tener entre 2 y 100 caracteres')
    ])
    pregunta_3 = StringField('Pregunta 3', validators=[
        DataRequired(message='La pregunta es obligatoria'),
        Length(min=5, max=200, message='La pregunta debe tener entre 5 y 200 caracteres')
    ])
    respuesta_3 = StringField('Respuesta 3', validators=[
        DataRequired(message='La respuesta es obligatoria'),
        Length(min=2, max=100, message='La respuesta debe tener entre 2 y 100 caracteres')
    ])
    submit = SubmitField('Guardar Preguntas de Seguridad')

class ResponderPreguntasForm(FlaskForm):
    """Formulario para responder preguntas de seguridad (recuperación)"""
    respuesta_1 = StringField('Respuesta 1', validators=[
        DataRequired(message='La respuesta es obligatoria')
    ])
    respuesta_2 = StringField('Respuesta 2', validators=[
        DataRequired(message='La respuesta es obligatoria')
    ])
    respuesta_3 = StringField('Respuesta 3', validators=[
        DataRequired(message='La respuesta es obligatoria')
    ])
    submit = SubmitField('Verificar Respuestas')

class NuevaPasswordRecuperacionForm(FlaskForm):
    """Formulario para establecer nueva contraseña después de verificar identidad"""
    password = PasswordField('Nueva contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    confirm_password = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message='Confirme la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Restablecer Contraseña')