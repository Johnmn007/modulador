import os
import re
from flask import Flask, render_template, request
from app.extensions import db, migrate, login_manager
from config import config_by_name
from app.services.logger import app_logger

def create_app(config_name=None):
    app = Flask(__name__)
    
    config_name = config_name or os.getenv("FLASK_CONFIG", "development")
    app.config.from_object(config_by_name[config_name])

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    app_logger.info(f"Iniciando aplicación en modo {config_name}")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    with app.app_context():
        from app.models import (
            Usuario, Estudiante, Curso, Inscripcion, 
            Asistencia, Evaluacion, Nota, 
            SeguimientoRiesgo, Intervencion, Ciclo, Reporte)
        
        @login_manager.user_loader
        def load_user(user_id):
            return Usuario.query.get(int(user_id))

    # Sanitize HTML filter for reports
    @app.template_filter('sanitize_html')
    def sanitize_html_filter(value):
        if not value:
            return value
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.DOTALL | re.IGNORECASE)
        value = re.sub(r'\bon\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
        value = re.sub(r'<iframe[^>]*>.*?</iframe>', '', value, flags=re.DOTALL | re.IGNORECASE)
        value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
        return value

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        csp = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data:;"
        response.headers['Content-Security-Policy'] = csp
        return response

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', codigo=400, mensaje='Solicitud incorrecta'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', codigo=403, mensaje='Acceso denegado'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', codigo=404, mensaje='Página no encontrada'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        app_logger.error(f"Error 500: {e}")
        return render_template('error.html', codigo=500, mensaje='Error interno del servidor'), 500

    # Registrar blueprints
    from app.modules.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.modules.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.modules.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.modules.estudiantes import estudiantes_bp
    app.register_blueprint(estudiantes_bp)
    
    from app.modules.seguimiento import seguimiento_bp
    app.register_blueprint(seguimiento_bp)
    
    from app.modules.importacion import importacion_bp
    app.register_blueprint(importacion_bp)
    
    from app.modules.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    from app.modules.reportes import reportes_bp
    app.register_blueprint(reportes_bp)
    
    from app.modules.cursos import cursos_bp
    app.register_blueprint(cursos_bp)
    
    from app.modules.inscripciones import inscripciones_bp
    app.register_blueprint(inscripciones_bp)
    
    from app.modules.evaluaciones import evaluaciones_bp
    app.register_blueprint(evaluaciones_bp)
    
    from app.modules.asistencias import asistencias_bp
    app.register_blueprint(asistencias_bp)
    
    return app