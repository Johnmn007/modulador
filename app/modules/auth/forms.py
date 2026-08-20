# app/modules/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
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