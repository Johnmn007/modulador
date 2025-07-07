# app/models.py

from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

# ---------- MODELO DE ROLES ----------
class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    usuarios = db.relationship('Usuario', back_populates='rol')

# ---------- MODELO DE CARRERAS ----------
class Carrera(db.Model):
    __tablename__ = 'carreras'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    usuarios = db.relationship('Usuario', backref='carrera')

# ---------- MODELO DE USUARIOS ----------
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

