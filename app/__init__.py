import os
from flask import Flask
from .extensions import db, migrate,login_manager

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.models import Usuario,Rol,Asignatura,Carrera,Periodo,Grupo,HorarioClase,Matricula,Asistencia,Archivo,Tramite
from config import config_by_name
# Puedes registrar más blueprints aquí



def create_app(config_name=None):
    app = Flask(__name__)
    config_name = config_name or os.getenv("FLASK_CONFIG", "development")
    app.config.from_object(config_by_name[config_name])

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app) 
    
    from app import models
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    
    
    
    from .modules.main import main_bp
    from .modules.auth import auth_bp
    from .modules.estudiante import estudiante_bp
    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(estudiante_bp)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    return app
