# app/models.py

from datetime import datetime
from app.extensions import db
from flask_login import UserMixin

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)

    usuarios = db.relationship('Usuario', back_populates='rol')

class Carrera(db.Model):
    __tablename__ = 'carreras'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)

    usuarios = db.relationship('Usuario', backref='carrera')

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    rol = db.relationship('Rol', back_populates='usuarios')

    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return str(self.id)

    @property
    def role(self):
        return self.rol

class Asignatura(db.Model):
    __tablename__ = 'asignaturas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    creditos = db.Column(db.Integer)
    carrera = db.relationship('Carrera', backref='asignaturas')

class Periodo(db.Model):
    __tablename__ = 'periodos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    anio = db.Column(db.Integer)
    estado = db.Column(db.Enum('activo', 'inactivo'), default='activo')

    grupos = db.relationship('Grupo', back_populates='periodo')

class Grupo(db.Model):
    __tablename__ = 'grupos'
    id = db.Column(db.Integer, primary_key=True)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignaturas.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodos.id'), nullable=False)

    asignatura = db.relationship('Asignatura', backref='grupos')
    docente = db.relationship('Usuario', backref='grupos_docente', foreign_keys=[docente_id])
    periodo = db.relationship('Periodo', back_populates='grupos')

class HorarioClase(db.Model):
    __tablename__ = 'horarios_clases'
    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'), nullable=False)
    dia_semana = db.Column(db.Enum('lunes','martes','miércoles','jueves','viernes','sábado'), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    aula = db.Column(db.String(50))

    grupo = db.relationship('Grupo', backref='horarios')

class Matricula(db.Model):
    __tablename__ = 'matriculas'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'), nullable=False)
    fecha_matricula = db.Column(db.DateTime, default=datetime.utcnow)

    estudiante = db.relationship('Usuario', backref='matriculas', foreign_keys=[estudiante_id])
    grupo = db.relationship('Grupo', backref='matriculas')

class Calificacion(db.Model):
    __tablename__ = 'calificaciones'
    id = db.Column(db.Integer, primary_key=True)
    matricula_id = db.Column(db.Integer, db.ForeignKey('matriculas.id'), nullable=False)
    parcial1 = db.Column(db.Numeric(5,2))
    parcial2 = db.Column(db.Numeric(5,2))
    final = db.Column(db.Numeric(5,2))

    matricula = db.relationship('Matricula', backref='calificaciones')

class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.Enum('presente','ausente','tarde'), default='presente')
    observaciones = db.Column(db.Text)

    estudiante = db.relationship('Usuario', backref='asistencias', foreign_keys=[estudiante_id])
    grupo = db.relationship('Grupo', backref='asistencias')

class Archivo(db.Model):
    __tablename__ = 'archivos'
    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255))
    ruta_archivo = db.Column(db.String(255))
    subido_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    descripcion = db.Column(db.Text)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    uploader = db.relationship('Usuario', backref='archivos', foreign_keys=[subido_por])

class Tramite(db.Model):
    __tablename__ = 'tramites'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    creador = db.relationship('Usuario', backref='tramites', foreign_keys=[creado_por])

class TramiteSolicitud(db.Model):
    __tablename__ = 'tramites_solicitudes'
    id = db.Column(db.Integer, primary_key=True)
    tramite_id = db.Column(db.Integer, db.ForeignKey('tramites.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    estado = db.Column(db.Enum('pendiente','en_proceso','completado','rechazado'), default='pendiente')
    archivo_subido = db.Column(db.String(255))
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)

    tramite = db.relationship('Tramite', backref='solicitudes')
    usuario = db.relationship('Usuario', backref='solicitudes', foreign_keys=[usuario_id])

